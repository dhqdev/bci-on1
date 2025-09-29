# auth/todoist_auth.py
# Módulo de autenticação e extração para o Todoist

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurações do Todoist
TODOIST_URL = "https://app.todoist.com/auth/login"
# Credenciais padrão (serão substituídas pelas do arquivo JSON)
DEFAULT_TODOIST_EMAIL = "oscarifn6@gmail.com"
DEFAULT_TODOIST_PASSWORD = "spfctri12"
TIMEOUT = 20

def login_todoist_and_extract(driver, progress_callback=None, credentials=None):
    """
    Faz login no Todoist e extrai número da tarefa
    
    IMPORTANTE: Esta função mantém TODAS as abas abertas após a extração.
    Ela apenas muda o foco de volta para a aba original do Servopa,
    mas mantém a aba do Todoist aberta para verificação manual.
    
    Args:
        driver: Instância do WebDriver já existente
        progress_callback: Função para atualizar progresso na UI
        credentials: Dict com 'usuario' e 'senha', ou None para usar padrão
        
    Returns:
        str: Número extraído da tarefa ou None se falhar
    """
    original_window = None
    
    try:
        # Usar credenciais fornecidas ou padrões
        if credentials:
            todoist_email = credentials.get('usuario', DEFAULT_TODOIST_EMAIL)
            todoist_password = credentials.get('senha', DEFAULT_TODOIST_PASSWORD)
            if progress_callback:
                progress_callback(f"🔐 Credenciais Todoist recebidas - Usuario: {todoist_email}")
        else:
            todoist_email = DEFAULT_TODOIST_EMAIL
            todoist_password = DEFAULT_TODOIST_PASSWORD
            if progress_callback:
                progress_callback(f"⚠️ Usando credenciais Todoist padrão - Usuario: {todoist_email}")
        # Salva janela original
        original_window = driver.current_window_handle
        
        if progress_callback:
            progress_callback("🆕 Abrindo nova aba para o Todoist...")
        
        # Abre nova aba
        driver.execute_script("window.open('');")
        new_window = driver.window_handles[-1]
        driver.switch_to.window(new_window)
        time.sleep(1)
        
        if progress_callback:
            progress_callback("🌐 Navegando para página de login do Todoist...")
        
        driver.get(TODOIST_URL)
        time.sleep(3)  # Pausa para carregamento
        
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🔍 Localizando campo de email...")
        
        # Campo de email
        email_input = wait.until(EC.presence_of_element_located((By.ID, "element-0")))
        
        if progress_callback:
            progress_callback(f"✏️ Preenchendo email: {todoist_email[:15]}...")
        
        email_input.clear()
        time.sleep(0.5)
        for char in todoist_email:
            email_input.send_keys(char)
            time.sleep(0.05)  # Digitação natural
        
        time.sleep(1)
        
        if progress_callback:
            progress_callback("🔍 Localizando campo de senha...")
        
        # Campo de senha
        password_input = wait.until(EC.presence_of_element_located((By.ID, "element-2")))
        
        if progress_callback:
            progress_callback("🔐 Preenchendo senha...")
        
        password_input.clear()
        time.sleep(0.5)
        for char in todoist_password:
            password_input.send_keys(char)
            time.sleep(0.05)  # Digitação natural
        
        time.sleep(1)
        
        if progress_callback:
            progress_callback("🚀 Clicando em login...")
        
        # Botão de login
        login_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit'], .submit_button, button[data-gtm-id='start-login']")
        ))
        login_button.click()
        
        if progress_callback:
            progress_callback("⏳ Aguardando login ser processado (10 segundos)...")
        
        time.sleep(10)  # Aguarda login como solicitado
        
        if progress_callback:
            progress_callback("🔍 Procurando projeto 'Lances Servopa Outubro Dia 8'...")
        
        # Procura o projeto
        project_element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Lances Servopa Outubro Dia 8')]")
        ))
        
        if progress_callback:
            progress_callback("📂 Abrindo projeto...")
        
        project_element.click()
        time.sleep(4)  # Aguarda carregamento do projeto
        
        if progress_callback:
            progress_callback("🔍 Procurando tarefa '1550 - dia 8'...")
        
        # Procura a tarefa específica
        task_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[@class='simple_content'][contains(text(), '1550 - dia 8')]")
        ))
        
        task_text = task_element.text.strip()
        
        if progress_callback:
            progress_callback(f"📋 Tarefa encontrada: '{task_text}'")
        
        # Extrai o número usando regex
        number_match = re.match(r'(\d+)', task_text)
        if number_match:
            extracted_number = number_match.group(1)
            
            if progress_callback:
                progress_callback(f"🎯 Número extraído com sucesso: {extracted_number}")
            
            # NÃO fecha aba do Todoist - apenas retorna à original
            if progress_callback:
                progress_callback("🔄 Retornando para aba do Servopa (mantendo Todoist aberto)")
            
            try:
                # Apenas muda para aba original, SEM fechar a do Todoist
                if original_window in driver.window_handles:
                    driver.switch_to.window(original_window)
                    if progress_callback:
                        progress_callback("✅ Retornado para aba do Servopa - Todoist permanece aberto")
                else:
                    # Se janela original não existe mais, usa a primeira disponível
                    driver.switch_to.window(driver.window_handles[0])
                    if progress_callback:
                        progress_callback("✅ Retornado para primeira aba disponível - Todoist permanece aberto")
            except Exception as switch_error:
                if progress_callback:
                    progress_callback(f"⚠️ Erro ao mudar de aba: {switch_error}")
            
            return extracted_number
        else:
            if progress_callback:
                progress_callback("❌ Não foi possível extrair número da tarefa")
            return None
            
    except TimeoutException as e:
        if progress_callback:
            progress_callback(f"⏰ Timeout no Todoist: {e}")
        
        # NÃO fecha aba do Todoist - apenas tenta retornar à original
        try:
            if original_window in driver.window_handles:
                driver.switch_to.window(original_window)
                if progress_callback:
                    progress_callback("🔄 Retornado para aba do Servopa após timeout")
        except:
            pass
            
        return None
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro no Todoist: {e}")
        
        # NÃO fecha aba do Todoist - apenas tenta retornar à original
        try:
            if original_window in driver.window_handles:
                driver.switch_to.window(original_window)
                if progress_callback:
                    progress_callback("🔄 Retornado para aba do Servopa após erro")
        except:
            pass
            
        return None
    finally:
        # Garante retorno à janela original mantendo todas as abas abertas
        try:
            if len(driver.window_handles) > 1:
                current_handle = driver.current_window_handle
                if current_handle != original_window and original_window in driver.window_handles:
                    driver.switch_to.window(original_window)
                    if progress_callback:
                        progress_callback("🔄 Garantindo retorno à janela do Servopa (todas as abas mantidas)")
        except Exception as final_error:
            if progress_callback:
                progress_callback(f"⚠️ Aviso no cleanup final: {final_error}")

if __name__ == "__main__":
    # Teste do módulo
    from auth.servopa_auth import create_driver
    
    driver = create_driver()
    try:
        driver.get("about:blank")  # Simula janela inicial
        number = login_todoist_and_extract(driver, print)
        
        if number:
            print(f"✅ Teste bem-sucedido! Número: {number}")
        else:
            print("❌ Teste falhou")
            
        input("Pressione Enter para continuar...")
    finally:
        driver.quit()