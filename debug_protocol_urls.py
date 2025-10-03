# debug_protocol_urls.py
# Script para debugar URLs que aparecem ao clicar em "Registrar"

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

print("=" * 80)
print("🔍 DEBUG - CAPTURA DE URLs AO REGISTRAR LANCE")
print("=" * 80)
print()
print("INSTRUÇÕES:")
print("1. Este script vai abrir o Chrome")
print("2. Faça login no Servopa manualmente")
print("3. Navegue até a página de lances")
print("4. Clique em 'Registrar'")
print("5. O script vai mostrar TODAS as URLs que aparecem")
print()
print("=" * 80)
input("Pressione ENTER para começar...")

# Cria driver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

print("\n🌐 Iniciando Chrome...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print("✅ Chrome iniciado!")
print()
print("👉 AGORA:")
print("   1. Faça login no Servopa")
print("   2. Navegue até a página de lances")
print("   3. Quando estiver pronto para clicar em 'Registrar',")
print("      volte aqui e pressione ENTER")
print()
input("Pressione ENTER quando estiver na página de lances...")

# Guarda informações atuais
original_window = driver.current_window_handle
handles_before = set(driver.window_handles)
original_url = driver.current_url

print()
print("=" * 80)
print("📊 ESTADO ANTES DE CLICAR EM 'REGISTRAR':")
print("=" * 80)
print(f"URL atual: {original_url}")
print(f"Janelas abertas: {len(handles_before)}")
print()
print("👉 Agora clique em 'Registrar' no Servopa")
print("   (O script vai monitorar por 15 segundos)")
print()
input("Pressione ENTER APÓS clicar em 'Registrar'...")

# Monitora por 15 segundos
print()
print("=" * 80)
print("🔍 MONITORANDO URLs E JANELAS...")
print("=" * 80)
print()

start_time = time.time()
urls_detectadas = []
max_wait = 15

print("⏱️  Aguardando até 15 segundos...")
print()

while time.time() - start_time < max_wait:
    elapsed = int(time.time() - start_time)
    
    # Verifica novas janelas
    handles_now = set(driver.window_handles)
    new_handles = handles_now - handles_before
    
    if new_handles:
        print(f"\n[{elapsed}s] 🆕 NOVA JANELA DETECTADA!")
        for handle in new_handles:
            try:
                driver.switch_to.window(handle)
                url = driver.current_url
                print(f"       URL: {url}")
                
                if url not in urls_detectadas:
                    urls_detectadas.append(url)
                    
                    # Verifica se é o DocParser
                    if "docparser" in url or "docgen" in url:
                        print(f"       ✅ ESTA É A URL DO PROTOCOLO!")
                        print(f"       🔑 Vamos extrair o Base64...")
                        
                        # Tenta pegar o Base64 do final da URL
                        if "/view/" in url:
                            base64_part = url.split("/view/")[-1]
                            print(f"       📦 Base64 encontrado: {base64_part[:50]}...")
                        elif url.startswith("data:"):
                            print(f"       ⚠️  URL é data: URI - precisamos lidar diferente!")
                        else:
                            print(f"       ⚠️  Formato de URL diferente do esperado!")
            except Exception as e:
                print(f"       ❌ Erro ao acessar janela: {e}")
    
    # Volta para janela original e verifica mudança de URL
    try:
        driver.switch_to.window(original_window)
        current_url = driver.current_url
        
        if current_url != original_url and current_url not in urls_detectadas:
            print(f"\n[{elapsed}s] 🔄 URL MUDOU NA JANELA ORIGINAL!")
            print(f"       De: {original_url}")
            print(f"       Para: {current_url}")
            urls_detectadas.append(current_url)
            original_url = current_url
    except Exception as e:
        print(f"\n[{elapsed}s] ⚠️  Erro ao verificar janela original: {e}")
    
    time.sleep(1)

# Resumo final
print()
print("=" * 80)
print("📋 RESUMO - URLs DETECTADAS:")
print("=" * 80)

if urls_detectadas:
    for i, url in enumerate(urls_detectadas, 1):
        print(f"\n{i}. {url}")
        
        # Análise da URL
        if "docparser/view" in url:
            print("   ✅ Formato: docparser/view - CÓDIGO ATUAL VAI FUNCIONAR")
        elif "docgen/lance" in url:
            print("   ⚠️  Formato: docgen/lance - CÓDIGO PRECISA SER AJUSTADO")
        elif url.startswith("data:"):
            print("   ⚠️  Formato: data: URI - CÓDIGO PRECISA SER AJUSTADO")
        else:
            print("   ❓ Formato desconhecido - precisa investigar")
else:
    print("\n❌ NENHUMA URL NOVA FOI DETECTADA!")
    print("   Possíveis causas:")
    print("   1. O botão 'Registrar' não foi clicado")
    print("   2. O lance já existe (popup apareceu)")
    print("   3. A janela/aba abre e fecha muito rápido")
    print("   4. O documento abre na mesma aba (sem nova janela)")

print()
print("=" * 80)
print("🔍 DICAS PARA PRÓXIMOS PASSOS:")
print("=" * 80)

if any("docgen" in url or "docparser" in url for url in urls_detectadas):
    print("\n✅ URL do protocolo foi detectada!")
    print("   Agora vamos ajustar o código para capturar corretamente.")
else:
    print("\n⚠️  URL do protocolo NÃO foi detectada automaticamente.")
    print("   Por favor:")
    print("   1. Anote manualmente a URL que aparece ao clicar em 'Registrar'")
    print("   2. Se abrir um PDF, clique com botão direito > Copiar URL")
    print("   3. Cole aqui a URL completa")

print()
print("=" * 80)
input("\nPressione ENTER para fechar o navegador e encerrar...")

driver.quit()
print("\n✅ Debug concluído!")
