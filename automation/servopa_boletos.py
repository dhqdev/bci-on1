"""Automação dedicada à geração de boletos no portal Servopa.

Este módulo centraliza a lógica para distinguir boletos individuais (com grupo/cota
específico) de boletos agrupados/massivos e executa o fluxo correspondente no
portal da Servopa utilizando Selenium. Ele retorna a URL final do boleto e uma
captura em PNG (base64) para ser reutilizada no envio automatizado via WhatsApp.
"""

from __future__ import annotations

import base64
import json
import re
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Reutilizamos utilitários existentes dos módulos de lances/login
from automation.servopa_lances import buscar_grupo, selecionar_cota

ProgressCallback = Optional[Callable[[str], None]]

DEFAULT_TIMEOUT = 25
SERVOPA_DASHBOARD_URL = "https://www.consorcioservopa.com.br/vendas/dashboard"
SERVOPA_PAINEL_URL = "https://www.consorcioservopa.com.br/vendas/painel"
SERVOPA_FERRAMENTAS_URL = "https://www.consorcioservopa.com.br/vendas/boleto-agrupado"


@dataclass
class BoletoTaskContext:
    """Informações derivadas de uma entrada de boleto importada do Todoist."""

    nome: str
    cotas_raw: str
    dia: str
    tipo: str  # "individual" ou "agrupado"
    grupo: Optional[str]
    cota: Optional[str]


@dataclass
class BoletoAutomationResult:
    """Resultado final da automação de geração de boleto."""

    tipo: str
    boleto_url: Optional[str]
    png_base64: Optional[str]
    grupo: Optional[str]
    cota: Optional[str]
    metadata: Dict[str, Optional[str]]


class BoletoAutomationError(RuntimeError):
    """Erro especializado para fluxos de boleto."""


def _notify(callback: ProgressCallback, message: str) -> None:
    if callback:
        try:
            callback(message)
        except Exception:
            # Não interrompe o fluxo em caso de erro no callback
            pass


def _remove_ip_from_servopa_url(url: str) -> str:
    """[FUNÇÃO DEPRECADA - NÃO USAR]
    
    Originalmente tentava remover o IP do payload base64 para tornar URLs universais,
    mas o servidor Servopa REQUER o parâmetro IP para validação.
    
    Remover o IP causa erro: "ENDERECO IP DEVE SER INFORMADO"
    
    Mantida apenas para referência histórica. Use a URL original do servidor.
    """
    if not url or 'consorcioservopa.com.br' not in url:
        return url
    
    try:
        # Extrai o payload base64 da URL
        parts = url.split('/docparser/view/')
        if len(parts) != 2:
            return url
        
        base_url = parts[0] + '/docparser/view/'
        encoded_payload = parts[1]
        
        # Decodifica o payload
        decoded_bytes = base64.b64decode(encoded_payload)
        payload_data = json.loads(decoded_bytes.decode('utf-8'))
        
        # Remove o campo IP se existir
        if 'data' in payload_data and 'ip' in payload_data['data']:
            del payload_data['data']['ip']
        
        # Re-codifica sem o IP
        new_payload = json.dumps(payload_data, separators=(',', ':'))
        new_encoded = base64.b64encode(new_payload.encode('utf-8')).decode('utf-8')
        
        return base_url + new_encoded
        
    except Exception as e:
        # Em caso de erro, retorna URL original
        print(f"⚠️ Erro ao remover IP da URL Servopa: {e}")
        return url


def parse_boleto_context(
    boleto_entry: Dict,
    dia: str,
    progress_callback: ProgressCallback = None,
) -> BoletoTaskContext:
    """Analisa uma entrada de boleto e classifica o tipo de automação requerido."""

    nome = (boleto_entry or {}).get("nome", "").strip()
    cotas_raw = (boleto_entry or {}).get("cotas", "") or ""
    normalized = cotas_raw.lower().strip()

    # Heurística: se menciona "cota" no texto ou não existem números suficientes,
    # tratamos como agrupado (boleto em massa). Caso contrário, tentamos extrair
    # grupo/cota para boleto individual.
    numeric_tokens = re.findall(r"\d+", cotas_raw)
    tipo = "agrupado"
    grupo = None
    cota = None

    if normalized and "cota" not in normalized and len(numeric_tokens) >= 2:
        # Consideramos boleto individual. O último grupo de 3-5 dígitos é o grupo;
        # o segmento antes do primeiro hífen costuma ser a cota.
        grupo_candidate = numeric_tokens[-1]
        if len(grupo_candidate) >= 3:
            grupo = grupo_candidate.zfill(4)[-4:]
        else:
            grupo = grupo_candidate

        # Extrai cota removendo caracteres não numéricos antes do primeiro " - "
        prefix_match = re.split(r"\s*-\s*", cotas_raw, maxsplit=1)
        if prefix_match:
            cota_digits = re.sub(r"\D", "", prefix_match[0])
            if cota_digits:
                cota = cota_digits

        if not cota and numeric_tokens:
            cota = numeric_tokens[0]

        if grupo and cota:
            tipo = "individual"

    _notify(
        progress_callback,
        f"📌 Boleto '{nome}' classificado como: {tipo.upper()} | Cotas='{cotas_raw}'",
    )

    return BoletoTaskContext(
        nome=nome or "Cliente",
        cotas_raw=cotas_raw,
        dia=dia,
        tipo=tipo,
        grupo=grupo,
        cota=cota,
    )


def _ensure_on_dashboard(driver: WebDriver, progress_callback: ProgressCallback) -> None:
    current_url = driver.current_url
    if "consorcioservopa.com.br" not in current_url:
        driver.get(SERVOPA_DASHBOARD_URL)
        time.sleep(2)
        return

    if "dashboard" not in current_url:
        _notify(progress_callback, "↩️ Voltando para o dashboard da Servopa...")
        driver.get(SERVOPA_DASHBOARD_URL)
        time.sleep(2)


def _wait_new_window(
    driver: WebDriver,
    handles_before: set,
    timeout: int = 20,
) -> Optional[str]:
    """Aguarda a abertura de uma nova aba/janela e retorna o handle."""

    end_time = time.time() + timeout
    while time.time() < end_time:
        current_handles = set(driver.window_handles)
        new_handles = current_handles - handles_before
        if new_handles:
            return new_handles.pop()
        time.sleep(0.5)
    return None


def _capture_pdf_view(
    driver: WebDriver,
    handles_before: set,
    progress_callback: ProgressCallback,
    timeout: int = 20,
) -> BoletoAutomationResult:
    """Captura URL e screenshot em PNG da aba recém-aberta com o boleto."""

    new_handle = _wait_new_window(driver, handles_before, timeout=timeout)
    original_handle = driver.current_window_handle
    metadata: Dict[str, Optional[str]] = {}

    if new_handle:
        driver.switch_to.window(new_handle)
    else:
        # Pode ter aberto na mesma aba; segue fluxo atual
        new_handle = original_handle

    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)  # garante renderização
        current_url = driver.current_url
        
        # IMPORTANTE: Mantém o IP no URL - o servidor Servopa REQUER este parâmetro
        # Anteriormente removíamos o IP tentando tornar universal, mas isso causava erro:
        # "ENDERECO IP DEVE SER INFORMADO"
        boleto_url = current_url
        
        png_bytes = driver.get_screenshot_as_png()
        png_base64 = "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")

        metadata.update(
            {
                "window_handle": new_handle,
                "url": current_url,
                "boleto_url": boleto_url,
                "screenshot_size": str(len(png_bytes)),
            }
        )

        return BoletoAutomationResult(
            tipo="unknown",
            boleto_url=boleto_url,  # Mantém URL com IP original do servidor
            png_base64=png_base64,
            grupo=None,
            cota=None,
            metadata=metadata,
        )
    finally:
        # Fecha aba extra se aberta e retorna para original
        try:
            if new_handle and new_handle != original_handle:
                driver.close()
                driver.switch_to.window(original_handle)
        except Exception:
            driver.switch_to.window(original_handle)


def process_individual_boleto(
    driver: WebDriver,
    context: BoletoTaskContext,
    progress_callback: ProgressCallback = None,
) -> BoletoAutomationResult:
    if not context.grupo or not context.cota:
        raise BoletoAutomationError("Dados insuficientes para boleto individual (grupo/cota ausentes).")

    _notify(progress_callback, f"🔍 Iniciando fluxo INDIVIDUAL para {context.nome}...")
    driver.get(SERVOPA_PAINEL_URL)
    time.sleep(2)

    if not buscar_grupo(driver, context.grupo, progress_callback):
        raise BoletoAutomationError(f"Não foi possível localizar o grupo {context.grupo}.")

    cota_data = selecionar_cota(driver, context.cota, progress_callback)
    if not cota_data:
        raise BoletoAutomationError(f"Cota {context.cota} não encontrada no grupo {context.grupo}.")

    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
    try:
        gerar_boleto_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@href, 'docparser') and contains(normalize-space(.), 'Gerar Boleto')]",
                )
            )
        )
    except TimeoutException as exc:
        raise BoletoAutomationError("Botão 'Gerar Boleto' não foi encontrado na página da cota." ) from exc

    handles_before = set(driver.window_handles)
    gerar_boleto_btn.click()
    _notify(progress_callback, "🧾 Gerando boleto individual...")

    capture = _capture_pdf_view(driver, handles_before, progress_callback)
    capture.tipo = "individual"
    capture.grupo = context.grupo
    capture.cota = context.cota

    _notify(progress_callback, "✅ Boleto individual capturado com sucesso!")
    return capture


def _abrir_ferramentas_admin(driver: WebDriver, progress_callback: ProgressCallback) -> None:
    _ensure_on_dashboard(driver, progress_callback)
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    try:
        admin_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'icon-tools') or contains(text(), 'Ferramentas Admin')]")
            )
        )
    except TimeoutException as exc:
        raise BoletoAutomationError("Não foi possível localizar o menu 'Ferramentas Admin'.") from exc

    admin_link.click()
    time.sleep(1.5)

    try:
        boleto_agrupado_link = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@href, '/vendas/boleto-agrupado') and contains(text(), 'Boleto Agrupado')]",
                )
            )
        )
    except TimeoutException as exc:
        raise BoletoAutomationError("Link 'Boleto Agrupado' não encontrado no menu de ferramentas.") from exc

    boleto_agrupado_link.click()
    _notify(progress_callback, "🔧 Página 'Boleto Agrupado' acessada.")
    time.sleep(2)


def process_group_boleto(
    driver: WebDriver,
    context: BoletoTaskContext,
    progress_callback: ProgressCallback = None,
) -> BoletoAutomationResult:
    _notify(progress_callback, f"🔍 Iniciando fluxo AGRUPADO para {context.nome}...")
    _abrir_ferramentas_admin(driver, progress_callback)

    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    try:
        nome_input = wait.until(EC.presence_of_element_located((By.ID, "nome")))
    except TimeoutException as exc:
        raise BoletoAutomationError("Campo 'nome' não encontrado na página Boleto Agrupado.") from exc

    nome_input.clear()
    nome_input.send_keys(context.nome)

    try:
        buscar_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn_busca_usuario")))
    except TimeoutException as exc:
        raise BoletoAutomationError("Botão de busca não encontrado na página Boleto Agrupado.") from exc

    buscar_btn.click()
    _notify(progress_callback, "👤 Buscando cliente para boleto agrupado...")
    time.sleep(2)

    try:
        resultados = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
        )
    except TimeoutException as exc:
        raise BoletoAutomationError("Nenhum resultado encontrado para o cliente informado.") from exc

    alvo = None
    nome_busca = context.nome.lower()
    for row in resultados:
        texto = row.text.lower()
        if nome_busca in texto:
            alvo = row
            break

    if alvo is None:
        alvo = resultados[0]
        _notify(progress_callback, "⚠️ Cliente exato não localizado, utilizando o primeiro resultado disponível.")

    try:
        gerar_btn = alvo.find_element(By.CSS_SELECTOR, "a.button-outline")
    except NoSuchElementException as exc:
        raise BoletoAutomationError("Linha selecionada não possui o botão 'Gerar Boleto'.") from exc

    handles_before = set(driver.window_handles)
    gerar_btn.click()
    _notify(progress_callback, "🧾 Abrindo tela de geração de boleto agrupado...")
    time.sleep(2)

    # A tela de geração abre na mesma aba; prossegue seleção
    try:
        select_dia = wait.until(EC.presence_of_element_located((By.ID, "dia")))
    except TimeoutException as exc:
        raise BoletoAutomationError("Seleção de dia não encontrada na tela de boleto agrupado.") from exc

    Select(select_dia).select_by_value("0")  # Todos
    time.sleep(1)

    # Alguns layouts usam abas; tentamos encontrar link/aba "Todos"
    try:
        aba_todos = driver.find_element(
            By.XPATH,
            "//a[contains(translate(text(),'TODOS','todos'), 'todos') or contains(@href, '#todos')]",
        )
        aba_todos.click()
        time.sleep(1)
    except NoSuchElementException:
        pass

    try:
        checker = wait.until(EC.element_to_be_clickable((By.ID, "checker")))
        if not checker.is_selected():
            checker.click()
    except TimeoutException as exc:
        raise BoletoAutomationError("Checkbox geral 'checker' não encontrado na tela de boleto agrupado.") from exc

    try:
        gerar_main = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.main")))
        gerar_main.click()
    except TimeoutException as exc:
        raise BoletoAutomationError("Botão principal de geração não encontrado.") from exc

    time.sleep(1.5)

    try:
        confirmar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.primary")))
        confirmar_btn.click()
    except TimeoutException as exc:
        raise BoletoAutomationError("Botão final de confirmação do boleto não foi exibido.") from exc

    _notify(progress_callback, "⏳ Gerando boletos agrupados...")
    capture = _capture_pdf_view(driver, handles_before, progress_callback)
    capture.tipo = "agrupado"
    capture.grupo = context.grupo
    capture.cota = context.cota
    _notify(progress_callback, "✅ Boleto agrupado capturado com sucesso!")
    return capture


def run_boleto_flow(
    driver: WebDriver,
    boleto_entry: Dict,
    dia: str,
    progress_callback: ProgressCallback = None,
) -> BoletoAutomationResult:
    """Executa o fluxo adequado (individual ou agrupado) para o boleto informado."""

    context = parse_boleto_context(boleto_entry, dia, progress_callback)

    if context.tipo == "individual":
        return process_individual_boleto(driver, context, progress_callback)

    return process_group_boleto(driver, context, progress_callback)
