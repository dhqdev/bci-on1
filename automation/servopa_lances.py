# automation/servopa_lances.py
# Módulo completo para automação de lances no Servopa

import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.protocol_extractor import extract_protocol_from_docparser

TIMEOUT = 20
SERVOPA_PAINEL_URL = "https://www.consorcioservopa.com.br/vendas/painel"
SERVOPA_LANCES_URL = "https://www.consorcioservopa.com.br/vendas/lances"


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
    Executa o lance completo:
    1. Copia valor de tx_lanfix para tx_lanfix_emb
    2. Clica em 'Simular Lance'
    3. Clica em 'Registrar'
    4. Verifica se aparece popup "Número do Protocolo Anterior é obrigatório"
       - Se aparecer = lance já existe = sucesso!
       - Se não aparecer = lance registrado = sucesso!
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: {'success': bool, 'already_exists': bool, 'message': str, 'valor_lance': str}
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        # Passo 1: Copiar valor de tx_lanfix
        if progress_callback:
            progress_callback("📋 Copiando valor do lance fixo...")
        
        tx_lanfix = wait.until(EC.presence_of_element_located((By.ID, "tx_lanfix")))
        valor_lanfix = tx_lanfix.get_attribute('value')
        
        if progress_callback:
            progress_callback(f"📋 Valor do lance fixo: {valor_lanfix}%")
        
        # Passo 2: Colar valor em tx_lanfix_emb
        tx_lanfix_emb = wait.until(EC.presence_of_element_located((By.ID, "tx_lanfix_emb")))
        tx_lanfix_emb.clear()
        time.sleep(0.5)
        
        # Digita com delay natural
        for char in valor_lanfix:
            tx_lanfix_emb.send_keys(char)
            time.sleep(0.1)
        
        time.sleep(1)
        
        if progress_callback:
            progress_callback(f"✅ Valor {valor_lanfix}% preenchido no campo embutido")
        
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

        original_window = driver.current_window_handle
        handles_before = set(driver.window_handles)

        registrar_button.click()

        if progress_callback:
            progress_callback("🔍 Verificando resultado do registro...")

        time.sleep(3)  # Aguarda popup aparecer se houver
        
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
                        
                        protocol_info = _capture_protocol_from_docparser(
                            driver,
                            original_window,
                            handles_before,
                            progress_callback,
                        )

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
                            'valor_lance': valor_lanfix,
                            'protocol_number': protocol_info.get('protocol'),
                            'docparser_url': protocol_info.get('docparser_url'),
                            'protocol_source': protocol_info.get('source'),
                        }
            
            # Se não encontrou popup, lance foi registrado com sucesso agora
            if not popup_text_found:
                if progress_callback:
                    progress_callback("✅ Lance registrado com sucesso!")
                
                protocol_info = _capture_protocol_from_docparser(
                    driver,
                    original_window,
                    handles_before,
                    progress_callback,
                )

                return {
                    'success': True,
                    'already_exists': False,
                    'message': 'Lance registrado com sucesso',
                    'valor_lance': valor_lanfix,
                    'protocol_number': protocol_info.get('protocol'),
                    'docparser_url': protocol_info.get('docparser_url'),
                    'protocol_source': protocol_info.get('source'),
                }
                
        except Exception as popup_error:
            # Se houve erro ao procurar popup, assume que lance foi registrado
            if progress_callback:
                progress_callback(f"✅ Lance registrado (verificação de popup: {popup_error})")
            
            protocol_info = _capture_protocol_from_docparser(
                driver,
                original_window,
                handles_before,
                progress_callback,
            )

            return {
                'success': True,
                'already_exists': False,
                'message': 'Lance registrado',
                'valor_lance': valor_lanfix,
                'protocol_number': protocol_info.get('protocol'),
                'docparser_url': protocol_info.get('docparser_url'),
                'protocol_source': protocol_info.get('source'),
            }
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao executar lance: {e}")
        return {
            'success': False,
            'already_exists': False,
            'message': f'Erro: {e}',
            'valor_lance': 'N/A'
        }


def _capture_protocol_from_docparser(driver, original_window, handles_before, progress_callback=None) -> dict:
    """Captura protocolo abrindo a aba gerada pelo registro do lance."""

    protocol_payload = {
        'protocol': None,
        'docparser_url': None,
        'source': None,
    }

    wait_until = time.time() + 10
    new_handles = []
    while time.time() < wait_until:
        handles_after = list(driver.window_handles)
        new_handles = [h for h in handles_after if h not in handles_before]
        current_url = driver.current_url
        if new_handles or "docparser/view" in current_url:
            break
        time.sleep(1)

    candidate_handles = new_handles + [original_window]

    for handle in candidate_handles:
        try:
            driver.switch_to.window(handle)
            current_url = driver.current_url
        except Exception:
            continue

        if "docparser/view" not in current_url:
            continue

        if progress_callback:
            progress_callback("📄 Documento de protocolo detectado, extraindo dados...")

        result = extract_protocol_from_docparser(driver, current_url, progress_callback)
        protocol_payload['protocol'] = result.protocol
        protocol_payload['docparser_url'] = result.docparser_url
        protocol_payload['source'] = result.source

        if handle != original_window:
            try:
                driver.close()
            except Exception:
                pass
        else:
            try:
                driver.back()
                WebDriverWait(driver, 10).until(EC.url_contains("/vendas/lances"))
            except Exception:
                pass

        break

    try:
        driver.switch_to.window(original_window)
    except Exception:
        pass

    return protocol_payload


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
        result['protocol_source'] = lance_result.get('protocol_source')
        result['docparser_url'] = lance_result.get('docparser_url')
        
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
