# automation/servopa_lances.py
# Módulo completo para automação de lances no Servopa

import time
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.protocol_extractor import (
    ProtocolExtractionResult,
    extract_protocol_from_docparser,
)

TIMEOUT = 20
SERVOPA_PAINEL_URL = "https://www.consorcioservopa.com.br/vendas/painel"
SERVOPA_LANCES_URL = "https://www.consorcioservopa.com.br/vendas/lances"


def _atualizar_cota_com_lance(grupo, cota, valor_lance, modalidade, progress_callback=None):
    """
    Atualiza o arquivo cotas_data.json com informações do lance registrado
    
    Args:
        grupo: Número do grupo
        cota: Número da cota
        valor_lance: Valor do lance (ex: "30" ou "15")
        modalidade: Tipo de modalidade (FIXO, FIDELIDADE, LIVRE)
        progress_callback: Função para logs
    """
    try:
        import json
        import os
        from datetime import datetime
        
        # Remove % se existir (garantia extra)
        valor_limpo = str(valor_lance).replace('%', '').strip()
        
        # Caminho para o arquivo de cotas
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cotas_data.json')
        
        if not os.path.exists(filepath):
            if progress_callback:
                progress_callback("⚠️ Arquivo cotas_data.json não encontrado")
            return
        
        # Carrega dados
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Procura pelo grupo e cota
        atualizado = False
        for dia_key in ['dia08', 'dia16']:
            if dia_key not in data:
                continue
            
            # Procura o grupo
            for grupo_obj in data[dia_key]:
                if str(grupo_obj.get('numero', '')) == str(grupo):
                    # Procura a cota dentro do grupo
                    for cota_obj in grupo_obj.get('cotas', []):
                        if str(cota_obj.get('cota', '')) == str(cota):
                            # Atualiza com informações do lance
                            cota_obj['lance_registrado'] = {
                                'valor': valor_limpo,
                                'modalidade': modalidade,
                                'data_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            atualizado = True
                            
                            if progress_callback:
                                progress_callback(f"✅ Cota {cota} atualizada com lance {modalidade} de {valor_limpo}%")
                            break
                    
                    if atualizado:
                        break
            
            if atualizado:
                break
        
        if atualizado:
            # Salva arquivo atualizado
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            if progress_callback:
                progress_callback(f"⚠️ Cota {cota} do grupo {grupo} não encontrada para atualizar")
    
    except Exception as e:
        if progress_callback:
            progress_callback(f"⚠️ Erro ao atualizar cota com lance: {e}")


def _resolve_docparser_candidate(url: Optional[str]) -> Optional[str]:
    """Retorna a string apropriada para o extrator de protocolo."""
    if not url:
        return None

    url = url.strip()
    if not url:
        return None

    lowered = url.lower()

    if lowered.startswith("http") and "docparser" in lowered:
        # URL já no formato /docparser/view/<base64>
        return url

    if "docgen" in lowered:
        try:
            parsed = urlparse(url)
            data_values = parse_qs(parsed.query).get("data")
            if data_values:
                return data_values[0]
        except Exception:
            return None

    if url.startswith("eyJ"):
        # Base64 puro
        return url

    return None


def _capture_protocol_document(
    driver,
    handles_before: set,
    original_handle: str,
    original_url: str,
    progress_callback=None,
    wait_seconds: int = 12,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Captura o número de protocolo a partir da aba/URL gerada após registrar."""

    protocol_number: Optional[str] = None
    docparser_url: Optional[str] = None
    documento_url: Optional[str] = None
    target_handle: Optional[str] = None

    deadline = time.time() + wait_seconds
    candidate_url: Optional[str] = None

    while time.time() < deadline and not candidate_url:
        try:
            handles_now = driver.window_handles
        except Exception:
            handles_now = []

        new_handles = [handle for handle in handles_now if handle not in handles_before]

        if new_handles:
            target_handle = new_handles[-1]
            try:
                driver.switch_to.window(target_handle)
            except Exception as error:
                if progress_callback:
                    progress_callback(f"⚠️ [PROTOCOLO] Erro ao acessar nova aba: {error}")
                target_handle = None
            else:
                inner_deadline = time.time() + 5
                while time.time() < inner_deadline:
                    try:
                        current_url = driver.current_url
                    except Exception:
                        current_url = ""

                    if current_url and current_url.lower() != "about:blank":
                        candidate_url = current_url
                        break
                    time.sleep(0.5)

        else:
            try:
                current_url = driver.current_url
            except Exception:
                current_url = ""

            if (
                current_url
                and current_url != original_url
                and (
                    "docparser" in current_url.lower()
                    or "docgen" in current_url.lower()
                    or current_url.strip().startswith("eyJ")
                )
            ):
                candidate_url = current_url

        if not candidate_url:
            time.sleep(0.5)

    candidate = _resolve_docparser_candidate(candidate_url)

    if candidate:
        try:
            if progress_callback:
                preview = candidate_url[:80] if candidate_url else candidate[:80]
                progress_callback(f"🔗 [PROTOCOLO] Documento detectado: {preview}...")

            extraction: ProtocolExtractionResult = extract_protocol_from_docparser(
                driver,
                candidate,
                progress_callback,
            )

            protocol_number = extraction.protocol
            docparser_url = extraction.docparser_url or candidate_url or candidate
            documento_url = extraction.pdf_url or docparser_url

            if progress_callback:
                if protocol_number:
                    progress_callback(f"📑 [PROTOCOLO] Número capturado: {protocol_number}")
                else:
                    progress_callback("⚠️ [PROTOCOLO] Documento aberto, mas número não foi identificado")

        except Exception as error:
            if progress_callback:
                progress_callback(f"⚠️ [PROTOCOLO] Erro ao extrair protocolo: {error}")
    else:
        if progress_callback:
            progress_callback("ℹ️ [PROTOCOLO] Nenhum documento de protocolo detectado")

    # Fecha a aba extra, se aberta, e retorna para a original
    try:
        if target_handle and target_handle in driver.window_handles:
            driver.close()
            driver.switch_to.window(original_handle)
            time.sleep(1)
        else:
            if driver.current_window_handle != original_handle and original_handle in driver.window_handles:
                driver.switch_to.window(original_handle)
    except Exception as error:
        if progress_callback:
            progress_callback(f"⚠️ [PROTOCOLO] Falha ao restaurar aba original: {error}")

    return protocol_number, docparser_url, documento_url


def alterar_consorcio(driver, progress_callback=None):
    """
    Clica em 'Alterar Consórcio' para voltar à busca
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se bem-sucedido
    """
    try:
        if progress_callback:
            progress_callback("🔄 Clicando em 'Alterar Consórcio'...")
        
        wait = WebDriverWait(driver, TIMEOUT)
        
        # Procura link "Alterar Consórcio"
        alterar_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='https://www.consorcioservopa.com.br/vendas/painel' or contains(text(), 'Alterar Consórcio')]")
        ))
        
        alterar_link.click()
        time.sleep(3)  # Aguarda carregamento
        
        if progress_callback:
            progress_callback("✅ Retornado à seleção de consórcio")
        
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao alterar consórcio: {e}")
        return False


def buscar_grupo(driver, grupo_number, progress_callback=None):
    """
    Preenche número do grupo e clica em buscar
    
    Args:
        driver: Instância do WebDriver
        grupo_number: Número do grupo (ex: "1550")
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se bem-sucedido
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback(f"🔍 Buscando grupo {grupo_number}...")
        
        # Localiza o campo de grupo
        grupo_input = wait.until(EC.presence_of_element_located((By.ID, "grupofrm")))
        
        # Preenche o campo com delay natural
        grupo_input.clear()
        time.sleep(0.5)
        for char in grupo_number:
            grupo_input.send_keys(char)
            time.sleep(0.1)  # Digitação natural
        
        time.sleep(1)
        
        # Localiza e clica no botão Buscar
        buscar_button = wait.until(EC.element_to_be_clickable(
            (By.ID, "btn_representante_cota")
        ))
        
        buscar_button.click()
        time.sleep(4)  # Aguarda busca carregar
        
        if progress_callback:
            progress_callback(f"✅ Grupo {grupo_number} buscado com sucesso")
        
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao buscar grupo: {e}")
        return False


def selecionar_cota(driver, cota_number, progress_callback=None):
    """
    Seleciona a cota específica na tabela de resultados
    
    Args:
        driver: Instância do WebDriver
        cota_number: Número da cota (ex: "303" ou "1123")
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: Dados da cota selecionada ou None se falhar
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        # IMPORTANTE: Normaliza o número da cota para 4 dígitos com zeros à esquerda
        # Ex: "303" vira "0303", "1123" continua "1123"
        cota_normalizada = str(cota_number).zfill(4)
        
        if progress_callback:
            progress_callback(f"🔍 Procurando cota {cota_number} (normalizada: {cota_normalizada}) na tabela...")
        
        # Aguarda tabela carregar
        time.sleep(2)
        
        # Procura todas as linhas da tabela
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        
        if not rows:
            if progress_callback:
                progress_callback("❌ Nenhuma linha encontrada na tabela")
            return None
        
        if progress_callback:
            progress_callback(f"📊 {len(rows)} linhas encontradas, procurando cota {cota_normalizada}...")
        
        # Lista para debug - mostra todas as cotas encontradas
        cotas_encontradas = []
        
        # Procura a linha com a cota específica
        for row in rows:
            try:
                # Pega todas as células da linha
                cells = row.find_elements(By.TAG_NAME, "td")
                
                # A cota está na 5ª coluna (índice 4)
                if len(cells) >= 5:
                    cota_cell = cells[4]  # Coluna "Cota"
                    cota_value = cota_cell.text.strip()
                    
                    # Adiciona à lista de debug
                    cotas_encontradas.append(cota_value)
                    
                    # Compara com a cota normalizada
                    if cota_value == cota_normalizada:
                        # Encontrou a cota!
                        nome_cliente = cells[0].text.strip()
                        valor = cells[1].text.strip()
                        grupo = cells[3].text.strip()
                        digito = cells[5].text.strip()
                        contrato = cells[6].text.strip()
                        
                        if progress_callback:
                            progress_callback(f"✅ Cota {cota_number} encontrada: {nome_cliente}")
                        
                        # Clica na linha
                        row.click()
                        time.sleep(3)  # Aguarda redirecionamento
                        
                        return {
                            'cota': cota_number,
                            'nome': nome_cliente,
                            'valor': valor,
                            'grupo': grupo,
                            'digito': digito,
                            'contrato': contrato
                        }
                        
            except Exception as cell_error:
                continue
        
        # Se chegou aqui, não encontrou a cota
        if progress_callback:
            progress_callback(f"❌ Cota {cota_normalizada} não encontrada na tabela")
            progress_callback(f"📋 Cotas disponíveis: {', '.join(cotas_encontradas[:10])}")  # Mostra até 10 cotas
            if len(cotas_encontradas) > 10:
                progress_callback(f"   ... e mais {len(cotas_encontradas) - 10} cotas")
        
        return None
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao selecionar cota: {e}")
        return None


def navegar_para_lances(driver, progress_callback=None):
    """
    Clica no link 'Lances' para ir para a página de lances
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se bem-sucedido
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🎯 Navegando para página de Lances...")
        
        # Procura o link de lances
        lances_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='https://www.consorcioservopa.com.br/vendas/lances' or contains(text(), 'Lances')]")
        ))
        
        lances_link.click()
        time.sleep(3)  # Aguarda carregamento
        
        if progress_callback:
            progress_callback("✅ Página de lances carregada")
        
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao navegar para lances: {e}")
        return False


def executar_lance(driver, progress_callback=None):
    """
    Executa o lance completo com detecção automática de modalidade:
    
    MODALIDADES (por ordem de prioridade):
    1. FIDELIDADE - Se existir aba "Fidelidade", usa ela (PRIORIDADE MÁXIMA)
    2. FIXO - Se existir "Fixo" e "Livre", usa Fixo (comportamento atual)
    3. LIVRE - Se existir APENAS "Livre", usa valor 30 com embutido
    
    Fluxo:
    1. Detecta qual modalidade está disponível
    2. Clica na aba correta (se necessário)
    3. Preenche os campos apropriados
    4. Clica em 'Simular Lance'
    5. Clica em 'Registrar'
    6. Verifica se aparece popup "Número do Protocolo Anterior é obrigatório"
       - Se aparecer = lance já existe = sucesso!
       - Se não aparecer = lance registrado = sucesso!
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: {'success': bool, 'already_exists': bool, 'message': str, 'valor_lance': str, 'modalidade': str}
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        # ========== PASSO 1: DETECTAR MODALIDADE DISPONÍVEL ==========
        if progress_callback:
            progress_callback("🔍 Detectando modalidade de lance disponível...")
        
        time.sleep(2)  # Aguarda página carregar completamente
        
        # Procura pela div tab-switcher
        tab_switcher = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tab-switcher")))
        abas_disponiveis = tab_switcher.find_elements(By.TAG_NAME, "a")
        
        # Mapeia as abas disponíveis
        abas_map = {}
        for aba in abas_disponiveis:
            tipo_lance = aba.get_attribute('data-lance')
            texto_aba = aba.text.strip()
            abas_map[tipo_lance] = {'element': aba, 'texto': texto_aba}
        
        if progress_callback:
            abas_texto = ', '.join([f"{v['texto']} ({k})" for k, v in abas_map.items()])
            progress_callback(f"📋 Abas disponíveis: {abas_texto}")
        
        # ========== DECISÃO DE MODALIDADE (POR ORDEM DE PRIORIDADE) ==========
        modalidade = None
        aba_para_clicar = None
        
        # PRIORIDADE 1: FIDELIDADE (data-lance="D")
        if 'D' in abas_map:
            modalidade = 'FIDELIDADE'
            aba_para_clicar = abas_map['D']['element']
            if progress_callback:
                progress_callback("✨ Modalidade FIDELIDADE detectada (PRIORIDADE)")
        
        # PRIORIDADE 2: FIXO (data-lance="F") - se não tem Fidelidade
        elif 'F' in abas_map:
            modalidade = 'FIXO'
            aba_para_clicar = abas_map['F']['element']
            if progress_callback:
                progress_callback("📌 Modalidade FIXO detectada")
        
        # PRIORIDADE 3: LIVRE (data-lance="L") - se é a única opção
        elif 'L' in abas_map and len(abas_map) == 1:
            modalidade = 'LIVRE'
            aba_para_clicar = abas_map['L']['element']
            if progress_callback:
                progress_callback("🆓 Modalidade LIVRE detectada (única opção)")
        
        else:
            raise Exception(f"Nenhuma modalidade válida detectada. Abas: {list(abas_map.keys())}")
        
        # ========== PASSO 2: CLICAR NA ABA CORRETA ==========
        if aba_para_clicar and 'active' not in aba_para_clicar.get_attribute('class'):
            if progress_callback:
                progress_callback(f"👆 Clicando na aba {modalidade}...")
            aba_para_clicar.click()
            time.sleep(1.5)
        
        # ========== PASSO 3: PREENCHER CAMPOS CONFORME MODALIDADE ==========
        valor_lance = None
        
        if modalidade == 'FIDELIDADE':
            # Fidelidade: Tenta preencher tx_lanfix_emb, se não existir, clica direto em Simular
            if progress_callback:
                progress_callback("📋 Processando lance fidelidade...")
            
            tx_lanfix = wait.until(EC.presence_of_element_located((By.ID, "tx_lanfix")))
            valor_lance_raw = tx_lanfix.get_attribute('value')
            # Remove % se existir e mantém apenas o número
            valor_lance = valor_lance_raw.replace('%', '').strip()
            
            if progress_callback:
                progress_callback(f"📋 Valor do lance fidelidade: {valor_lance}%")
            
            # Verifica se existe o campo tx_lanfix_emb
            try:
                tx_lanfix_emb = driver.find_element(By.ID, "tx_lanfix_emb")
                
                # Se existe, preenche normalmente
                if progress_callback:
                    progress_callback("📝 Preenchendo campo embutido...")
                
                tx_lanfix_emb.clear()
                time.sleep(0.5)
                
                for char in valor_lance:
                    tx_lanfix_emb.send_keys(char)
                    time.sleep(0.1)
                
                time.sleep(1)
                if progress_callback:
                    progress_callback(f"✅ Valor {valor_lance}% preenchido (Fidelidade com embutido)")
                    
            except:
                # Se não existe o campo, apenas lê o valor e segue direto para simular
                if progress_callback:
                    progress_callback(f"✅ Fidelidade sem campo embutido - valor {valor_lance}% detectado")
                time.sleep(0.5)
        
        elif modalidade == 'FIXO':
            # Fixo (comportamento atual)
            if progress_callback:
                progress_callback("📋 Copiando valor do lance fixo...")
            
            tx_lanfix = wait.until(EC.presence_of_element_located((By.ID, "tx_lanfix")))
            valor_lance_raw = tx_lanfix.get_attribute('value')
            # Remove % se existir e mantém apenas o número
            valor_lance = valor_lance_raw.replace('%', '').strip()
            
            if progress_callback:
                progress_callback(f"📋 Valor do lance fixo: {valor_lance}%")
            
            tx_lanfix_emb = wait.until(EC.presence_of_element_located((By.ID, "tx_lanfix_emb")))
            tx_lanfix_emb.clear()
            time.sleep(0.5)
            
            for char in valor_lance:
                tx_lanfix_emb.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(1)
            if progress_callback:
                progress_callback(f"✅ Valor {valor_lance}% preenchido (Fixo)")
        
        elif modalidade == 'LIVRE':
            # Livre usa valor fixo 30 em ambos os campos + marca checkbox embutido
            valor_lance = "30"
            
            if progress_callback:
                progress_callback("📋 Preenchendo lance livre com valor 30%...")
            
            # Campo 1: tx_Lanliv
            tx_lanliv = wait.until(EC.presence_of_element_located((By.ID, "tx_Lanliv")))
            tx_lanliv.clear()
            time.sleep(0.3)
            for char in valor_lance:
                tx_lanliv.send_keys(char)
                time.sleep(0.1)
            
            # Campo 2: tx_lanliv_emb
            tx_lanliv_emb = wait.until(EC.presence_of_element_located((By.ID, "tx_lanliv_emb")))
            tx_lanliv_emb.clear()
            time.sleep(0.3)
            for char in valor_lance:
                tx_lanliv_emb.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(0.5)
            
            # Marca checkbox "OFERTAR LANCE COM EMBUTIDO" (value="N")
            if progress_callback:
                progress_callback("✅ Marcando opção 'OFERTAR LANCE COM EMBUTIDO'...")
            
            checkbox_embutido = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[type='radio'][name='st_lanse'][value='N']")
            ))
            driver.execute_script("arguments[0].click();", checkbox_embutido)
            time.sleep(0.5)
            
            if progress_callback:
                progress_callback(f"✅ Valor {valor_lance}% preenchido com embutido (Livre)")
        
        # Passo 3: Clicar em 'Simular Lance'
        if progress_callback:
            progress_callback("🎲 Simulando lance...")
        
        simular_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a#btn_simular, a[name='btn_simular']")
        ))
        
        simular_button.click()
        time.sleep(3)  # Aguarda simulação processar
        
        if progress_callback:
            progress_callback("✅ Simulação concluída")
        
        # Passo 4: Clicar em 'Registrar'
        if progress_callback:
            progress_callback("💾 Registrando lance...")
        
        registrar_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.printBt")
        ))

        handles_before = set(driver.window_handles)
        original_handle = driver.current_window_handle
        original_url = driver.current_url

        registrar_button.click()

        if progress_callback:
            progress_callback("🔍 Verificando resultado do registro...")

        time.sleep(3)  # Aguarda processamento
        
        protocol_number: Optional[str] = None
        docparser_url: Optional[str] = None
        documento_url: Optional[str] = None

        # Tenta encontrar o popup de erro
        try:
            # Procura por popup/alert com a mensagem de protocolo obrigatório
            popup_text_found = False
            
            # Estratégia 1: Procura por divs de erro/alerta
            error_elements = driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Número do Protocolo Anterior') or " +
                "contains(text(), 'Protocolo Anterior é obrigatório') or " +
                "contains(text(), 'obrigatório')]")
            
            if error_elements:
                for elem in error_elements:
                    if elem.is_displayed():
                        popup_text_found = True
                        if progress_callback:
                            progress_callback("⚠️ Popup detectado: 'Número do Protocolo Anterior é obrigatório'")
                            progress_callback("✅ Lance JÁ FOI REGISTRADO anteriormente - considerando sucesso!")

                        # Tenta clicar em OK se houver botão
                        try:
                            ok_button = driver.find_element(By.XPATH, 
                                "//button[contains(text(), 'OK') or contains(text(), 'Ok')]")
                            if ok_button.is_displayed():
                                ok_button.click()
                                time.sleep(1)
                        except:
                            pass
                        
                        return {
                            'success': True,
                            'already_exists': True,
                            'message': 'Lance já foi registrado anteriormente',
                            'valor_lance': valor_lance,
                            'modalidade': modalidade,
                            'protocol_number': None,
                            'docparser_url': None,
                            'documento_url': None,
                        }
            
            # Se não encontrou popup, lance foi registrado com sucesso agora
            if not popup_text_found:
                if progress_callback:
                    progress_callback("✅ Lance registrado com sucesso!")
                protocol_number, docparser_url, documento_url = _capture_protocol_document(
                    driver,
                    handles_before,
                    original_handle,
                    original_url,
                    progress_callback,
                )
                return {
                    'success': True,
                    'already_exists': False,
                    'message': 'Lance registrado com sucesso',
                    'valor_lance': valor_lance,
                    'modalidade': modalidade,
                    'protocol_number': protocol_number,
                    'docparser_url': docparser_url,
                    'documento_url': documento_url,
                }
                
        except Exception as popup_error:
            # Se houve erro ao procurar popup, assume que lance foi registrado
            if progress_callback:
                progress_callback(f"✅ Lance registrado (verificação de popup: {popup_error})")

            protocol_number, docparser_url, documento_url = _capture_protocol_document(
                driver,
                handles_before,
                original_handle,
                original_url,
                progress_callback,
            )

            return {
                'success': True,
                'already_exists': False,
                'message': 'Lance registrado',
                'valor_lance': valor_lance,
                'modalidade': modalidade,
                'protocol_number': protocol_number,
                'docparser_url': docparser_url,
                'documento_url': documento_url,
            }
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao executar lance: {e}")
        return {
            'success': False,
            'already_exists': False,
            'message': f'Erro: {e}',
            'valor_lance': 'N/A',
            'modalidade': 'N/A',
            'protocol_number': None,
            'docparser_url': None,
            'documento_url': None,
        }


def processar_lance_completo(driver, grupo, cota, progress_callback=None):
    """
    Processa um lance completo do início ao fim
    
    Args:
        driver: Instância do WebDriver
        grupo: Número do grupo
        cota: Número da cota
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: Resultado do processamento
    """
    result = {
        'success': False,
        'grupo': grupo,
        'cota': cota,
        'steps_completed': []
    }
    
    try:
        # Passo 1: Alterar consórcio (se não for o primeiro lance)
        current_url = driver.current_url
        if 'painel' not in current_url:
            if not alterar_consorcio(driver, progress_callback):
                return result
            result['steps_completed'].append('alterar_consorcio')
        
        # Passo 2: Buscar grupo
        if not buscar_grupo(driver, grupo, progress_callback):
            return result
        result['steps_completed'].append('buscar_grupo')
        
        # Passo 3: Selecionar cota
        cota_data = selecionar_cota(driver, cota, progress_callback)
        if not cota_data:
            return result
        result['steps_completed'].append('selecionar_cota')
        result['cota_data'] = cota_data
        
        # Passo 4: Navegar para lances
        if not navegar_para_lances(driver, progress_callback):
            return result
        result['steps_completed'].append('navegar_lances')
        
        # Passo 5: Executar lance
        lance_result = executar_lance(driver, progress_callback)
        if not lance_result['success']:
            return result

        result['steps_completed'].append('executar_lance')
        result['already_exists'] = lance_result.get('already_exists', False)
        result['lance_message'] = lance_result.get('message', '')
        result['protocol_number'] = lance_result.get('protocol_number')
        result['docparser_url'] = lance_result.get('docparser_url')
        result['documento_url'] = lance_result.get('documento_url')
        result['valor_lance'] = lance_result.get('valor_lance', 'N/A')  # Adiciona valor do lance
        result['modalidade'] = lance_result.get('modalidade', 'N/A')  # Adiciona modalidade
        
        # Atualiza arquivo de cotas com informações do lance
        _atualizar_cota_com_lance(grupo, cota, result['valor_lance'], result['modalidade'], progress_callback)
        
        # Sucesso!
        result['success'] = True
        return result
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro no processamento completo: {e}")
        return result


if __name__ == "__main__":
    # Teste do módulo
    print("Este módulo deve ser importado e usado com uma instância do WebDriver")
    print("Exemplo:")
    print("  from auth.servopa_auth import create_driver, login_servopa")
    print("  from automation.servopa_lances import processar_lance_completo")
    print("  ")
    print("  driver = create_driver()")
    print("  login_servopa(driver)")
    print("  result = processar_lance_completo(driver, '1550', '1123')")
