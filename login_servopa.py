# login_servopa.py
# Requisitos: pip install selenium webdriver-manager

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

# --- CONFIGURAÇÃO ---
URL = "https://www.consorcioservopa.com.br/vendas/login"

# Credenciais (substitua por variáveis de ambiente em produção)
LOGIN = os.getenv("SERVOPA_LOGIN", "26.350.659/0001-61")
SENHA = os.getenv("SERVOPA_SENHA", "43418")

# Use headless = True se não quiser abrir janela do navegador
HEADLESS = False

# Timeout para esperas (segundos)
TIMEOUT = 15

def create_driver(headless: bool = False):
    options = webdriver.ChromeOptions()
    # opções recomendadas
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless=new")  # ou "--headless"
    # cria driver usando webdriver-manager (faz download do chromedriver automaticamente)
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_servopa(driver=None, return_driver=False):
    """
    Faz login no sistema Servopa.
    
    Args:
        driver: Driver existente (opcional)
        return_driver: Se True, retorna o driver sem fechá-lo
        
    Returns:
        driver se return_driver=True, senão None
    """
    driver_created = False
    if driver is None:
        driver = create_driver(HEADLESS)
        driver_created = True
    
    try:
        wait = WebDriverWait(driver, TIMEOUT)

        driver.get(URL)

        # Espera pelo campo do CPF/CNPJ usando id do label 'representante_cpf_cnpj'
        # geralmente o input tem id igual ao 'for' do label.
        cpf_input = wait.until(EC.presence_of_element_located(
            (By.ID, "representante_cpf_cnpj")
        ))

        senha_input = driver.find_element(By.ID, "representante_senha")

        # Limpa e preenche (mantendo o formato que você passou)
        cpf_input.clear()
        cpf_input.send_keys(LOGIN)

        senha_input.clear()
        senha_input.send_keys(SENHA)

        # Tenta submeter: procura um botão do tipo submit dentro do form
        try:
            # primeiro tenta por botão com type=submit
            submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit.click()
        except NoSuchElementException:
            # se não tiver, tenta enviar ENTER no campo de senha
            senha_input.send_keys(Keys.ENTER)

        # espera por alguma mudança que indique login (pode ser URL diferente, dashboard, ou ausência do form)
        # vou esperar até que o campo de login desapareça ou URL mude
        wait.until(EC.staleness_of(cpf_input))  # espera o elemento atual ficar obsoleto (ou seja, page change)
        time.sleep(1)  # pequena pausa para carregamento adicional

        # Verificação simples: se ainda estiver na mesma URL, tentar detectar erro de login
        current_url = driver.current_url
        if current_url == URL:
            # tenta detectar mensagens de erro (geral e comum nas páginas)
            try:
                err = driver.find_element(By.CSS_SELECTOR, ".error, .alert, .invalid-feedback")
                print("POSSÍVEL ERRO de login detectado na página:", err.text.strip())
                return None if return_driver else None
            except NoSuchElementException:
                print("Ainda na página de login — verifique credenciais ou possíveis medidas anti-bot (captcha).")
                return None if return_driver else None
        else:
            print("Login efetuado (URL mudou para):", current_url)

        # opcional: tira screenshot da página pós-login
        out_screenshot = "servopa_post_login.png"
        driver.save_screenshot(out_screenshot)
        print("Screenshot salva em:", out_screenshot)
        
        # Retorna o driver se solicitado
        if return_driver:
            return driver

        
        # Retorna o driver se solicitado
        if return_driver:
            return driver

    except TimeoutException as e:
        print("Timeout esperando elementos na página:", e)
        if driver:
            driver.save_screenshot("servopa_timeout.png")
            print("Screenshot salva em servopa_timeout.png")
        return None if return_driver else None
    except WebDriverException as e:
        print("Erro no webdriver:", e)
        return None if return_driver else None
    except Exception as e:
        print("Erro inesperado:", e)
        return None if return_driver else None
    finally:
        if not return_driver and driver_created and driver:
            driver.quit()

def navigate_to_consorcio_selection_and_fill(driver, grupo_number):
    """
    Navega para a seleção de consórcio e preenche o número do grupo.
    
    Args:
        driver: Instância do WebDriver já logado no Servopa
        grupo_number: Número do grupo extraído do Todoist (ex: "1550")
        
    Returns:
        bool: True se bem-sucedido, False caso contrário
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        # Navega para o dashboard
        dashboard_url = "https://www.consorcioservopa.com.br/vendas/dashboard"
        print(f"Navegando para o dashboard: {dashboard_url}")
        driver.get(dashboard_url)
        
        # Aguarda um pouco para carregar
        time.sleep(2)
        
        # Procura e clica no link "Selecionar Consórcio"
        print("Procurando link 'Selecionar Consórcio'...")
        selecionar_consorcio_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='https://www.consorcioservopa.com.br/vendas/painel' or contains(text(), 'Selecionar Consórcio')]")
        ))
        selecionar_consorcio_link.click()
        
        # Aguarda a página carregar
        time.sleep(2)
        
        # Procura o campo de grupo e preenche com o número
        print(f"Procurando campo 'grupofrm' para preencher com: {grupo_number}")
        grupo_input = wait.until(EC.presence_of_element_located(
            (By.ID, "grupofrm")
        ))
        
        # Limpa e preenche o campo
        grupo_input.clear()
        grupo_input.send_keys(grupo_number)
        
        print(f"✓ Campo preenchido com sucesso: {grupo_number}")
        
        # Tira screenshot do resultado final
        driver.save_screenshot("servopa_consorcio_preenchido.png")
        print("Screenshot final salva em: servopa_consorcio_preenchido.png")
        
        return True
        
    except TimeoutException as e:
        print(f"Timeout ao navegar/preencher consórcio: {e}")
        driver.save_screenshot("servopa_consorcio_error.png")
        return False
    except Exception as e:
        print(f"Erro ao navegar/preencher consórcio: {e}")
        driver.save_screenshot("servopa_consorcio_error.png")
        return False

if __name__ == "__main__":
    # Teste apenas do login
    driver = login_servopa(return_driver=True)
    if driver:
        input("Pressione Enter para fechar o navegador...")
        driver.quit()
    else:
        print("Falha no login")
