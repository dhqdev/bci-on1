#!/usr/bin/env python3
# verify_installation.py
# Script para verificar se tudo está instalado corretamente

"""
Script de verificação da instalação do Sistema de Automação v4.0

USO:
    python verify_installation.py
"""

import sys
import os

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def print_check(text, status):
    """Imprime resultado de verificação"""
    icon = "✅" if status else "❌"
    print(f"{icon} {text}")

def verify_python():
    """Verifica versão do Python"""
    print("\n🐍 Verificando Python...")
    version = sys.version_info
    is_ok = version.major == 3 and version.minor >= 8
    
    print_check(f"Python {version.major}.{version.minor}.{version.micro}", is_ok)
    
    if not is_ok:
        print("   ⚠️  Requer Python 3.8 ou superior")
        return False
    
    return True

def verify_dependencies():
    """Verifica dependências instaladas"""
    print("\n📦 Verificando dependências...")
    
    # Dependências obrigatórias
    required_dependencies = {
        'selenium': 'Selenium',
        'webdriver_manager': 'WebDriver Manager',
        'tkinter': 'Tkinter (GUI)'
    }
    
    # Dependências opcionais (para funcionalidades específicas)
    optional_dependencies = {
        'requests': 'Requests (HTTP)',
        'bs4': 'BeautifulSoup4 (HTML parsing)'
    }
    
    all_ok = True
    
    # Verifica dependências obrigatórias
    for module, name in required_dependencies.items():
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
            print_check(name, True)
        except ImportError:
            print_check(name, False)
            all_ok = False
    
    # Verifica dependências opcionais (não falha se ausentes)
    for module, name in optional_dependencies.items():
        try:
            __import__(module)
            print_check(f"{name} (opcional)", True)
        except ImportError:
            print_check(f"{name} (opcional) - ausente", False)
            print(f"   ℹ️  {name} não é obrigatório para funcionamento básico")
    
    return all_ok

def verify_files():
    """Verifica arquivos essenciais"""
    print("\n📁 Verificando arquivos essenciais...")
    
    required_files = {
        'main_gui.py': 'Executável principal (GUI)',
        'auth/servopa_auth.py': 'Módulo autenticação Servopa',
        'auth/todoist_auth.py': 'Módulo autenticação Todoist',
        'automation/servopa_lances.py': 'Módulo lances (v4.0)',
        'automation/cycle_orchestrator.py': 'Orquestrador ciclo (v4.0)',
        'utils/todoist_board_extractor.py': 'Extrator board (v4.0)',
        'ui/modern_automation_gui.py': 'Interface moderna',
        'requirements.txt': 'Lista de dependências'
    }
    
    all_ok = True
    
    for file, desc in required_files.items():
        exists = os.path.exists(file)
        print_check(f"{desc} ({file})", exists)
        if not exists:
            all_ok = False
    
    return all_ok

def verify_chrome():
    """Verifica se Chrome pode ser iniciado"""
    print("\n🌐 Verificando Google Chrome...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("   📥 Baixando/verificando ChromeDriver...")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("about:blank")
        driver.quit()
        
        print_check("Chrome e ChromeDriver", True)
        return True
        
    except Exception as e:
        print_check("Chrome e ChromeDriver", False)
        print(f"   ⚠️  Erro: {e}")
        return False

def verify_credentials():
    """Verifica se credenciais existem"""
    print("\n🔐 Verificando credenciais...")
    
    exists = os.path.exists('credentials.json')
    print_check("Arquivo credentials.json", exists)
    
    if not exists:
        print("   ℹ️  Configure as credenciais via interface gráfica")
        print("   ℹ️  Execute: python main_gui.py")
        return False
    
    try:
        import json
        with open('credentials.json', 'r') as f:
            data = json.load(f)
        
        has_servopa = 'servopa' in data and data['servopa'].get('usuario') and data['servopa'].get('senha')
        has_todoist = 'todoist' in data and data['todoist'].get('usuario') and data['todoist'].get('senha')
        
        print_check("Credenciais Servopa configuradas", has_servopa)
        print_check("Credenciais Todoist configuradas", has_todoist)
        
        return has_servopa and has_todoist
        
    except Exception as e:
        print_check("Credenciais válidas", False)
        print(f"   ⚠️  Erro ao ler credenciais: {e}")
        return False

def verify_documentation():
    """Verifica documentação"""
    print("\n📚 Verificando documentação...")
    
    docs = {
        'README.md': 'README principal',
        'QUICKSTART.md': 'Guia rápido',
        'README_USER_GUIDE.md': 'Guia completo do usuário',
        'TECHNICAL_DOCS.md': 'Documentação técnica',
        'SUMMARY.md': 'Resumo executivo'
    }
    
    all_ok = True
    
    for file, desc in docs.items():
        exists = os.path.exists(file)
        print_check(desc, exists)
        if not exists:
            all_ok = False
    
    return all_ok

def main():
    """Função principal"""
    print_header("VERIFICAÇÃO DE INSTALAÇÃO - v1.0")
    
    print("\n📋 Este script verifica se tudo está instalado corretamente")
    print("   para o Sistema de Automação Servopa + Todoist")
    
    results = {}
    
    # Executa verificações
    results['Python'] = verify_python()
    results['Dependências'] = verify_dependencies()
    results['Arquivos'] = verify_files()
    results['Chrome'] = verify_chrome()
    results['Credenciais'] = verify_credentials()
    results['Documentação'] = verify_documentation()
    
    # Resumo final
    print_header("RESUMO DA VERIFICAÇÃO")
    
    all_ok = True
    for check, status in results.items():
        print_check(check, status)
        if not status:
            all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✅ TUDO OK! Sistema pronto para uso!")
        print("\n📝 Próximos passos:")
        print("   1. Execute: python main_gui.py")
        print("   2. Configure credenciais (se ainda não fez)")
        print("   3. Clique em 'Iniciar' na aba Automação")
        print("\n📚 Documentação:")
        print("   • QUICKSTART.md - Guia rápido")
        print("   • README_USER_GUIDE.md - Guia completo")
        return 0
    else:
        print("❌ Alguns problemas encontrados!")
        print("\n🔧 Como corrigir:")
        
        if not results['Python']:
            print("   • Instale Python 3.8 ou superior")
        
        if not results['Dependências']:
            print("   • Execute: pip install -r requirements.txt")
        
        if not results['Arquivos']:
            print("   • Baixe o projeto completo novamente")
            print("   • Certifique-se de estar no diretório correto")
        
        if not results['Chrome']:
            print("   • Instale o Google Chrome")
            print("   • Verifique conexão com internet")
        
        if not results['Credenciais']:
            print("   • Execute: python main_gui.py")
            print("   • Vá para aba 'Credenciais'")
            print("   • Preencha e salve as credenciais")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Verificação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
