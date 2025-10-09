# automation/servopa_automation.py
# Automação dos processos do sistema Servopa

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# URLs do Servopa
SERVOPA_DASHBOARD_URL = "https://www.consorcioservopa.com.br/vendas/dashboard"
SERVOPA_PAINEL_URL = "https://www.consorcioservopa.com.br/vendas/painel"
SERVOPA_LANCES_URL = "https://www.consorcioservopa.com.br/vendas/lances"
TIMEOUT = 20

def navigate_to_consorcio_selection(driver, progress_callback=None):
    """
    Navega para a seleção de consórcio
    
    Args:
        driver: Instância do WebDriver já logado
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se bem-sucedido
    """
    try:
        if progress_callback:
            progress_callback("🏠 Navegando para o dashboard...")
        
        driver.get(SERVOPA_DASHBOARD_URL)
        time.sleep(3)  # Aguarda carregamento
        
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🔍 Procurando link 'Selecionar Consórcio'...")
        
        # Procura o link de seleção de consórcio
        selecionar_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='https://www.consorcioservopa.com.br/vendas/painel' or contains(text(), 'Selecionar Consórcio')]")
        ))
        
        if progress_callback:
            progress_callback("👆 Clicando em 'Selecionar Consórcio'...")
        
        selecionar_link.click()
        time.sleep(3)  # Aguarda carregamento da página
        
        if progress_callback:
            progress_callback("✅ Navegação para seleção de consórcio concluída")
        
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro na navegação: {e}")
        return False

def fill_grupo_and_search(driver, grupo_number, progress_callback=None):
    """
    Preenche número do grupo e clica em buscar
    
    Args:
        driver: Instância do WebDriver
        grupo_number: Número do grupo extraído do Todoist
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se bem-sucedido
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🔍 Localizando campo de grupo...")
        
        # Localiza o campo de grupo
        grupo_input = wait.until(EC.presence_of_element_located((By.ID, "grupofrm")))
        
        if progress_callback:
            progress_callback(f"✏️ Preenchendo campo com número: {grupo_number}")
        
        # Preenche o campo com delay natural
        grupo_input.clear()
        time.sleep(0.5)
        for char in grupo_number:
            grupo_input.send_keys(char)
            time.sleep(0.1)  # Digitação natural
        
        time.sleep(1)
        
        if progress_callback:
            progress_callback("🔍 Procurando botão 'Buscar'...")
        
        # Localiza e clica no botão Buscar
        buscar_button = wait.until(EC.element_to_be_clickable(
            (By.ID, "btn_representante_cota")
        ))
        
        if progress_callback:
            progress_callback("🔍 Clicando em 'Buscar' para localizar clientes...")
        
        buscar_button.click()
        time.sleep(4)  # Aguarda busca carregar
        
        if progress_callback:
            progress_callback("✅ Busca por clientes realizada com sucesso")
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao buscar clientes: {e}")
        return False

def select_first_client(driver, progress_callback=None):
    """
    Seleciona o primeiro cliente da lista
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        str: Nome do cliente selecionado ou None se falhar
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🔍 Procurando primeiro cliente na lista...")
        
        # Procura o primeiro cliente (div com classe wrap)
        first_client = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div.wrap")
        ))
        
        # Pega o nome do cliente
        client_name = first_client.text.strip()
        
        if progress_callback:
            progress_callback(f"👤 Cliente encontrado: {client_name}")
        
        if progress_callback:
            progress_callback("👆 Selecionando primeiro cliente...")
        
        # Clica no cliente
        first_client.click()
        time.sleep(3)  # Aguarda seleção ser processada
        
        if progress_callback:
            progress_callback(f"✅ Cliente '{client_name}' selecionado com sucesso")
        
        return client_name
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao selecionar cliente: {e}")
        return None

def navigate_to_lances(driver, progress_callback=None):
    """
    Navega para a página de lances
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se bem-sucedido
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🔍 Procurando link de 'Lances'...")
        
        # Procura o link de lances
        lances_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='https://www.consorcioservopa.com.br/vendas/lances' or contains(text(), 'Lances')]")
        ))
        
        if progress_callback:
            progress_callback("🎯 Navegando para página de lances...")
        
        lances_link.click()
        time.sleep(3)  # Aguarda carregamento
        
        if progress_callback:
            progress_callback("✅ Navegação para lances concluída")
        
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao navegar para lances: {e}")
        return False

def extract_cotas_from_grupo(driver, grupo_number, progress_callback=None):
    """
    Extrai todas as cotas de um grupo específico
    AGORA TAMBÉM extrai Total Investido e Crédito Atual de cada cota
    
    Args:
        driver: Instância do WebDriver já logado
        grupo_number: Número do grupo para extração
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: Resultado com lista de cotas extraídas
    """
    result = {
        'success': False,
        'grupo_number': grupo_number,
        'cotas': []
    }
    
    try:
        if progress_callback:
            progress_callback(f"🏠 Navegando para painel de seleção...")
        
        # Navega diretamente para o painel
        driver.get(SERVOPA_PAINEL_URL)
        time.sleep(3)
        
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback(f"🔍 Localizando campo de grupo...")
        
        # Localiza o campo de grupo
        grupo_input = wait.until(EC.presence_of_element_located((By.ID, "grupofrm")))
        
        if progress_callback:
            progress_callback(f"✏️ Preenchendo grupo: {grupo_number}")
        
        # Preenche o campo com delay natural
        grupo_input.clear()
        time.sleep(0.5)
        for char in str(grupo_number):
            grupo_input.send_keys(char)
            time.sleep(0.1)
        
        time.sleep(1)
        
        if progress_callback:
            progress_callback("🔍 Clicando em buscar...")
        
        # Localiza e clica no botão Buscar
        buscar_button = wait.until(EC.element_to_be_clickable(
            (By.ID, "btn_representante_cota")
        ))
        buscar_button.click()
        time.sleep(4)  # Aguarda tabela carregar
        
        if progress_callback:
            progress_callback("📋 Extraindo dados básicos da tabela...")
        
        # Aguarda tabela aparecer
        table = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".cotas-table table tbody")
        ))
        
        # Extrai todas as linhas da tabela
        rows = table.find_elements(By.TAG_NAME, "tr")
        total_cotas = len(rows)
        
        if progress_callback:
            progress_callback(f"📊 Encontradas {total_cotas} cotas no grupo {grupo_number}")
        
        # PRIMEIRA PASSAGEM: Coleta apenas dados básicos da tabela
        cotas_basicas = []
        for idx, row in enumerate(rows, 1):
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 9:
                    cota_basica = {
                        'index': idx - 1,  # Índice para clicar depois
                        'nome': cells[0].text.strip(),
                        'valor': cells[1].text.strip(),
                        'data_compra': cells[2].text.strip(),
                        'grupo': cells[3].text.strip(),
                        'cota': cells[4].text.strip(),
                        'digito': cells[5].text.strip(),
                        'contrato': cells[6].text.strip(),
                        'dep_id': cells[7].text.strip(),
                        'status': cells[8].text.strip()
                    }
                    cotas_basicas.append(cota_basica)
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(f"⚠️ Erro ao extrair linha {idx}: {e}")
                continue
        
        if progress_callback:
            progress_callback(f"🔄 Iniciando extração detalhada (Total Investido + Crédito Atual)...")
        
        # SEGUNDA PASSAGEM: Para cada cota, acessa o extrato e extrai dados financeiros
        for idx, cota_basica in enumerate(cotas_basicas, 1):
            nome = cota_basica['nome']
            cota_number = cota_basica['cota']
            
            try:
                if progress_callback:
                    progress_callback(f"  📌 [{idx}/{total_cotas}] {nome} - Cota {cota_number}")
                
                # Re-obtém a tabela sempre (garantir que está atualizada)
                table = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".cotas-table table tbody")
                ))
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                # Procura a linha correta pelo número da cota
                target_row = None
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 5:
                        row_cota = cells[4].text.strip()
                        if row_cota == cota_number:
                            target_row = row
                            break
                
                if not target_row:
                    if progress_callback:
                        progress_callback(f"      ⚠️  Linha da cota {cota_number} não encontrada, pulando...")
                    # Adiciona sem dados financeiros
                    result['cotas'].append(cota_basica)
                    continue
                
                if progress_callback:
                    progress_callback(f"      ➡️  Clicando na linha para acessar extrato...")
                
                # Clica na linha (onclick vai para o extrato)
                driver.execute_script("arguments[0].scrollIntoView(true);", target_row)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", target_row)
                time.sleep(3)  # Aguarda página de extrato carregar
                
                # Extrai dados do extrato
                total_investido = None
                credito_atual = None
                
                try:
                    # Procura "VALOR TOTAL DAS PARCELAS PAGAS"
                    parcelas_element = driver.find_element(By.XPATH, 
                        "//span[contains(text(), 'VALOR TOTAL DAS PARCELAS PAGAS')]/following-sibling::strong")
                    total_investido = parcelas_element.text.strip()
                    
                    if progress_callback:
                        progress_callback(f"      💰 Total Investido: {total_investido}")
                except NoSuchElementException:
                    if progress_callback:
                        progress_callback(f"      ⚠️  Total Investido não encontrado")
                
                try:
                    # Procura "VALOR ATUAL DO CRÉDITO"
                    credito_element = driver.find_element(By.XPATH,
                        "//span[contains(text(), 'VALOR ATUAL DO CRÉDITO')]/following-sibling::strong")
                    credito_atual = credito_element.text.strip()
                    
                    if progress_callback:
                        progress_callback(f"      💎 Crédito Atual: {credito_atual}")
                except NoSuchElementException:
                    if progress_callback:
                        progress_callback(f"      ⚠️  Crédito Atual não encontrado")
                
                # Adiciona os campos extras aos dados da cota
                cota_completa = cota_basica.copy()
                cota_completa['total_investido'] = total_investido
                cota_completa['credito_atual'] = credito_atual
                
                # Remove index antes de salvar
                if 'index' in cota_completa:
                    del cota_completa['index']
                
                result['cotas'].append(cota_completa)
                
                # Volta para a tabela
                if progress_callback:
                    progress_callback(f"      ↩️  Voltando para a tabela...")
                
                # ========== CORREÇÃO BUG #1: NAVEGAÇÃO MELHORADA ==========
                driver.get(SERVOPA_PAINEL_URL)
                time.sleep(3)  # Aumentado para garantir carregamento completo
                
                # Re-preenche grupo e busca novamente COM RETRY
                tentativas = 0
                max_tentativas = 3
                busca_sucesso = False
                
                while tentativas < max_tentativas and not busca_sucesso:
                    try:
                        # Re-preenche grupo
                        grupo_input = wait.until(EC.presence_of_element_located((By.ID, "grupofrm")))
                        grupo_input.clear()
                        time.sleep(0.5)
                        
                        for char in str(grupo_number):
                            grupo_input.send_keys(char)
                            time.sleep(0.05)
                        
                        time.sleep(0.5)
                        
                        # Clica em buscar
                        buscar_button = wait.until(EC.element_to_be_clickable((By.ID, "btn_representante_cota")))
                        buscar_button.click()
                        time.sleep(4)  # Aumentado para garantir carregamento da tabela
                        
                        # Verifica se tabela carregou
                        table_check = driver.find_element(By.CSS_SELECTOR, ".cotas-table table tbody")
                        rows_check = table_check.find_elements(By.TAG_NAME, "tr")
                        
                        if len(rows_check) > 0:
                            busca_sucesso = True
                            if progress_callback and tentativas > 0:
                                progress_callback(f"      ✅ Tabela recarregada com sucesso (tentativa {tentativas + 1})")
                        else:
                            tentativas += 1
                            if tentativas < max_tentativas:
                                if progress_callback:
                                    progress_callback(f"      ⚠️  Tabela vazia, tentando novamente... ({tentativas}/{max_tentativas})")
                                time.sleep(2)
                    except Exception as retry_error:
                        tentativas += 1
                        if tentativas < max_tentativas:
                            if progress_callback:
                                progress_callback(f"      ⚠️  Erro ao recarregar tabela, tentando novamente... ({tentativas}/{max_tentativas})")
                            time.sleep(2)
                        else:
                            if progress_callback:
                                progress_callback(f"      ❌ Falha ao recarregar tabela após {max_tentativas} tentativas")
                            raise retry_error
                
            except Exception as e:
                if progress_callback:
                    progress_callback(f"      ❌ Erro ao processar cota {cota_number}: {e}")
                
                # Mesmo com erro, adiciona cota sem dados extras
                cota_sem_financeiro = cota_basica.copy()
                if 'index' in cota_sem_financeiro:
                    del cota_sem_financeiro['index']
                result['cotas'].append(cota_sem_financeiro)
                
                # Tenta voltar para a tabela
                try:
                    driver.get(SERVOPA_PAINEL_URL)
                    time.sleep(2)
                    
                    grupo_input = wait.until(EC.presence_of_element_located((By.ID, "grupofrm")))
                    grupo_input.clear()
                    for char in str(grupo_number):
                        grupo_input.send_keys(char)
                        time.sleep(0.05)
                    
                    buscar_button = wait.until(EC.element_to_be_clickable((By.ID, "btn_representante_cota")))
                    buscar_button.click()
                    time.sleep(3)
                except:
                    pass
        
        if progress_callback:
            progress_callback(f"✅ Extração completa concluída! Total: {len(result['cotas'])} cotas com dados detalhados")
        
        result['success'] = True
        return result
        
    except TimeoutException as e:
        if progress_callback:
            progress_callback(f"⏰ Timeout na extração: Tabela não carregou")
        return result
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro na extração: {e}")
        import traceback
        if progress_callback:
            progress_callback(f"Detalhes: {traceback.format_exc()}")
        return result

def complete_servopa_automation(driver, grupo_number, progress_callback=None):
    """
    Executa o processo completo de automação no Servopa
    
    Args:
        driver: Instância do WebDriver já logado
        grupo_number: Número do grupo do Todoist
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: Resultado da automação com status e dados
    """
    result = {
        'success': False,
        'grupo_number': grupo_number,
        'client_name': None,
        'steps_completed': []
    }
    
    try:
        # Passo 1: Navegar para seleção de consórcio
        if navigate_to_consorcio_selection(driver, progress_callback):
            result['steps_completed'].append('navigation')
        else:
            return result
        
        # Passo 2: Preencher e buscar
        if fill_grupo_and_search(driver, grupo_number, progress_callback):
            result['steps_completed'].append('search')
        else:
            return result
        
        # Passo 3: Selecionar primeiro cliente
        client_name = select_first_client(driver, progress_callback)
        if client_name:
            result['client_name'] = client_name
            result['steps_completed'].append('client_selection')
        else:
            return result
        
        # Passo 4: Navegar para lances
        if navigate_to_lances(driver, progress_callback):
            result['steps_completed'].append('lances_navigation')
            result['success'] = True
        
        return result
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro na automação completa: {e}")
        return result

if __name__ == "__main__":
    # Teste do módulo
    from auth.servopa_auth import create_driver, login_servopa
    
    driver = create_driver()
    try:
        # Faz login primeiro
        if login_servopa(driver, print):
            print("✅ Login OK, testando automação...")
            
            # Testa automação completa
            result = complete_servopa_automation(driver, "1550", print)
            
            if result['success']:
                print(f"✅ Automação completa! Cliente: {result['client_name']}")
            else:
                print("❌ Automação falhou")
                
            input("Pressione Enter para continuar...")
        else:
            print("❌ Falha no login")
    finally:
        driver.quit()