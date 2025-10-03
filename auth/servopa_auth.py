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
    """Cria e configura o driver do navegador com anti-detecção"""
    options = webdriver.ChromeOptions()
    
    # Argumentos básicos
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Anti-detecção: Remove flags de automação
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent real (Chrome 120 em Windows)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Desabilita detecção de headless
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    
    # Adiciona preferências para parecer navegador real
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        # Simula plugins
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    
    if headless:
        # Modo headless com resolução HD para screenshots nítidos
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--force-device-scale-factor=1")
        # Importante: Simula GPU mesmo em headless
        options.add_argument("--disable-gpu")
    else:
        options.add_argument("--start-maximized")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # ===== STEALTH MODE: Injeta scripts anti-detecção =====
    
    # 1. Remove propriedade webdriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    # 2. Sobrescreve plugins e mimeTypes
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [1, 2, 3, 4]
            });
        """
    })
    
    # 3. Modifica languages para parecer real
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
        """
    })
    
    # 4. Adiciona propriedades de Chrome real
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """
    })
    
    # 5. Modifica permissions
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """
    })
    
    return driver

def wait_for_cloudflare_pass(driver, progress_callback=None, max_wait=30):
    """
    Aguarda o Cloudflare/Captcha passar
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso
        max_wait: Tempo máximo de espera em segundos
        
    Returns:
        bool: True se passou, False se timeout
    """
    import time
    
    if progress_callback:
        progress_callback("🛡️ Detectado proteção anti-bot, aguardando...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            # Verifica se ainda está na página de verificação
            page_source = driver.page_source.lower()
            
            # Indicadores de Cloudflare/proteção
            cloudflare_indicators = [
                'cloudflare',
                'verificando seu navegador',
                'checking your browser',
                'just a moment',
                'please wait',
                'captcha',
                'confirme que você é humano'
            ]
            
            is_cloudflare = any(indicator in page_source for indicator in cloudflare_indicators)
            
            if not is_cloudflare:
                # Passou da verificação
                if progress_callback:
                    progress_callback("✅ Verificação anti-bot concluída!")
                return True
            
            # Aguarda 2 segundos antes de verificar novamente
            time.sleep(2)
            
            elapsed = int(time.time() - start_time)
            if progress_callback and elapsed % 5 == 0:
                progress_callback(f"⏳ Aguardando verificação... ({elapsed}s/{max_wait}s)")
                
        except Exception as e:
            if progress_callback:
                progress_callback(f"⚠️ Erro ao verificar Cloudflare: {e}")
            time.sleep(2)
    
    # Timeout
    if progress_callback:
        progress_callback(f"❌ Timeout aguardando verificação anti-bot ({max_wait}s)")
    
    return False

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
        
        # Acessa a URL
        driver.get(SERVOPA_LOGIN_URL)
        
        # Aguarda Cloudflare/Captcha passar (máximo 60 segundos)
        if not wait_for_cloudflare_pass(driver, progress_callback, max_wait=60):
            if progress_callback:
                progress_callback("⚠️ Verificação anti-bot demorou muito, continuando mesmo assim...")
        
        # Pausa adicional para carregamento natural
        time.sleep(3)
        
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