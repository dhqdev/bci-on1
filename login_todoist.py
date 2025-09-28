# login_todoist.py
# Automação para login no Todoist e extração de número de tarefa

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

# Configurações do Todoist
TODOIST_URL = "https://app.todoist.com/auth/login"
TODOIST_EMAIL = "oscarifn6@gmail.com"
TODOIST_PASSWORD = "spfctri12"

# Timeout para esperas (segundos)
TIMEOUT = 15

def login_todoist_and_extract_number(driver):
    """
    Abre nova aba, faz login no Todoist e extrai o número da tarefa.
    
    Args:
        driver: Instância do WebDriver já existente
        
    Returns:
        str: Número extraído da tarefa (ex: "1550") ou None se falhar
    """
    try:
        # Salva a aba atual (Servopa)
        original_window = driver.current_window_handle
        
        # Abre nova aba para o Todoist
        driver.execute_script("window.open('');")
        new_window = driver.window_handles[-1]
        driver.switch_to.window(new_window)
        
        print("Navegando para o Todoist...")
        driver.get(TODOIST_URL)
        
        wait = WebDriverWait(driver, TIMEOUT)
        
        # Aguarda e preenche o campo de email
        print("Preenchendo email...")
        email_input = wait.until(EC.presence_of_element_located(
            (By.ID, "element-0")
        ))
        email_input.clear()
        email_input.send_keys(TODOIST_EMAIL)
        
        # Aguarda e preenche o campo de senha
        print("Preenchendo senha...")
        password_input = wait.until(EC.presence_of_element_located(
            (By.ID, "element-2")
        ))
        password_input.clear()
        password_input.send_keys(TODOIST_PASSWORD)
        
        # Procura e clica no botão de login
        login_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit'], .submit_button, button[data-gtm-id='start-login']")
        ))
        login_button.click()
        
        print("Aguardando login... (10 segundos)")
        time.sleep(10)
        
        # Aguarda e clica no projeto "Lances Servopa Outubro Dia 8"
        print("Procurando projeto 'Lances Servopa Outubro Dia 8'...")
        project_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Lances Servopa Outubro Dia 8')]")
        ))
        project_link.click()
        
        # Aguarda um pouco para o projeto carregar
        time.sleep(3)
        
        # Procura pela tarefa "1550 - dia 8"
        print("Procurando tarefa '1550 - dia 8'...")
        task_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[@class='simple_content'][contains(text(), '1550 - dia 8')]")
        ))
        
        # Extrai o texto da tarefa
        task_text = task_element.text.strip()
        print(f"Tarefa encontrada: {task_text}")
        
        # Extrai apenas o número usando regex
        number_match = re.match(r'(\d+)', task_text)
        if number_match:
            extracted_number = number_match.group(1)
            print(f"Número extraído: {extracted_number}")
            
            # Fecha a aba do Todoist e volta para a aba do Servopa
            driver.close()
            driver.switch_to.window(original_window)
            
            return extracted_number
        else:
            print("Erro: Não foi possível extrair o número da tarefa")
            return None
            
    except TimeoutException as e:
        print(f"Timeout ao carregar elementos no Todoist: {e}")
        return None
    except NoSuchElementException as e:
        print(f"Elemento não encontrado no Todoist: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado no Todoist: {e}")
        return None
    finally:
        # Garante que volta para a aba original em caso de erro
        try:
            if len(driver.window_handles) > 1:
                driver.switch_to.window(original_window)
        except:
            pass

def test_todoist_login():
    """Função de teste independente para o Todoist"""
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Simula que já temos uma aba aberta (abre uma página qualquer)
        driver.get("about:blank")
        
        # Testa a extração do número
        number = login_todoist_and_extract_number(driver)
        
        if number:
            print(f"✓ Teste bem-sucedido! Número extraído: {number}")
            return number
        else:
            print("✗ Teste falhou - não foi possível extrair o número")
            return None
            
    finally:
        input("Pressione Enter para fechar o navegador...")
        driver.quit()

if __name__ == "__main__":
    test_todoist_login()