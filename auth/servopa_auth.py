# auth/servopa_auth.py
# Módulo de autenticação para o sistema Servopa

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configurações do Servopa
SERVOPA_LOGIN_URL = "https://www.consorcioservopa.com.br/vendas/login"
# Credenciais padrão (serão substituídas pelas do arquivo JSON)
DEFAULT_SERVOPA_LOGIN = "26.350.659/0001-61"
DEFAULT_SERVOPA_SENHA = "43418"
TIMEOUT = 20

def create_driver(headless=False):
    """Cria e configura o driver do navegador"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    if headless:
        options.add_argument("--headless=new")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Remove indicadores de automação
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def login_servopa(driver, progress_callback=None, credentials=None):
    """
    Realiza login no sistema Servopa
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        credentials: Dict com 'usuario' e 'senha', ou None para usar padrão
        
    Returns:
        bool: True se login bem-sucedido, False caso contrário
    """
    try:
        # Usar credenciais fornecidas ou padrões
        if credentials:
            servopa_login = credentials.get('usuario', DEFAULT_SERVOPA_LOGIN)
            servopa_senha = credentials.get('senha', DEFAULT_SERVOPA_SENHA)
            if progress_callback:
                progress_callback(f"🔐 Credenciais recebidas - Usuario: {servopa_login}")
        else:
            servopa_login = DEFAULT_SERVOPA_LOGIN
            servopa_senha = DEFAULT_SERVOPA_SENHA
            if progress_callback:
                progress_callback(f"⚠️ Usando credenciais padrão - Usuario: {servopa_login}")
        
        if progress_callback:
            progress_callback(f"🌐 Fazendo login com usuário: {servopa_login[:10]}...")
        
        driver.get(SERVOPA_LOGIN_URL)
        time.sleep(2)  # Pausa para carregamento natural
        
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🔍 Localizando campos de login...")
        
        # Localiza campo CPF/CNPJ
        cpf_input = wait.until(EC.presence_of_element_located(
            (By.ID, "representante_cpf_cnpj")
        ))
        
        # Localiza campo senha
        senha_input = driver.find_element(By.ID, "representante_senha")
        
        if progress_callback:
            progress_callback("✏️ Preenchendo credenciais...")
        
        # Preenche CPF/CNPJ com delay natural
        cpf_input.clear()
        time.sleep(0.5)
        for char in servopa_login:
            cpf_input.send_keys(char)
            time.sleep(0.1)  # Simula digitação humana
        
        time.sleep(1)
        
        # Preenche senha com delay natural
        senha_input.clear()
        time.sleep(0.5)
        for char in servopa_senha:
            senha_input.send_keys(char)
            time.sleep(0.1)  # Simula digitação humana
        
        time.sleep(1)
        
        if progress_callback:
            progress_callback("🚀 Submetendo formulário de login...")
        
        # Tenta submeter o formulário
        try:
            submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit.click()
        except NoSuchElementException:
            senha_input.send_keys(Keys.ENTER)
        
        time.sleep(3)  # Aguarda processamento do login
        
        if progress_callback:
            progress_callback("⏳ Verificando resultado do login...")
        
        # Espera mudança na página
        try:
            wait.until(EC.staleness_of(cpf_input))
        except TimeoutException:
            pass
        
        time.sleep(2)
        
        # Verifica se login foi bem-sucedido
        current_url = driver.current_url
        if current_url == SERVOPA_LOGIN_URL:
            # Verifica se há mensagem de erro
            try:
                error = driver.find_element(By.CSS_SELECTOR, ".error, .alert, .invalid-feedback")
                if progress_callback:
                    progress_callback(f"❌ Erro no login: {error.text.strip()}")
                return False
            except NoSuchElementException:
                if progress_callback:
                    progress_callback("❌ Login falhou - ainda na página de login")
                return False
        else:
            if progress_callback:
                progress_callback(f"✅ Login realizado com sucesso! Redirecionado para: {current_url}")
            
            return True
            
    except TimeoutException as e:
        if progress_callback:
            progress_callback(f"⏰ Timeout no login do Servopa: {e}")
        return False
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro no login do Servopa: {e}")
        return False

if __name__ == "__main__":
    # Teste do módulo
    driver = create_driver()
    try:
        success = login_servopa(driver, print)
        if success:
            print("✅ Teste de login bem-sucedido!")
            input("Pressione Enter para continuar...")
        else:
            print("❌ Teste de login falhou!")
    finally:
        driver.quit()