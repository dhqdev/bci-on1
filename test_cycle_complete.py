#!/usr/bin/env python3
# test_cycle_complete.py
# Script de teste para o ciclo completo de automação

"""
Este script testa o sistema completo de automação v4.0
que faz o ciclo entre Servopa e Todoist.

REQUISITOS:
- Credenciais configuradas em credentials.json
- Google Chrome instalado
- Conexão com internet

USO:
    python test_cycle_complete.py
"""

import sys
import os
import time

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)

def print_step(step_num, text):
    """Imprime passo formatado"""
    print(f"\n🔹 PASSO {step_num}: {text}")
    print("-" * 60)

def test_cycle_complete():
    """Testa o ciclo completo de automação"""
    
    print_header("TESTE DO CICLO COMPLETO DE AUTOMAÇÃO V4.0")
    
    print("\n📋 Este teste irá:")
    print("  1. Fazer login no Servopa")
    print("  2. Abrir nova aba e fazer login no Todoist")
    print("  3. Extrair todas as colunas e linhas do board")
    print("  4. Processar cada lance (coluna por coluna, linha por linha)")
    print("  5. Marcar checkboxes no Todoist após cada lance")
    print("  6. Manter o navegador aberto ao final")
    
    input("\n⏸️  Pressione ENTER para iniciar o teste...")
    
    try:
        # Importa módulos necessários
        print_step(1, "Importando módulos")
        
        from auth.servopa_auth import create_driver, login_servopa
        from auth.todoist_auth import TODOIST_URL, TIMEOUT
        from utils.todoist_board_extractor import navigate_to_board_project, extract_complete_board
        from automation.cycle_orchestrator import executar_ciclo_completo
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import json
        
        print("✅ Módulos importados com sucesso")
        
        # Carrega credenciais
        print_step(2, "Carregando credenciais")
        
        if not os.path.exists('credentials.json'):
            print("❌ Arquivo credentials.json não encontrado!")
            print("📝 Por favor, execute a interface gráfica e configure as credenciais.")
            return False
        
        with open('credentials.json', 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        print(f"✅ Credenciais carregadas:")
        print(f"   Servopa: {credentials['servopa']['usuario']}")
        print(f"   Todoist: {credentials['todoist']['usuario']}")
        
        # Cria driver
        print_step(3, "Iniciando navegador Chrome")
        driver = create_driver()
        print("✅ Navegador iniciado")
        
        try:
            # Login Servopa
            print_step(4, "Fazendo login no Servopa")
            
            if login_servopa(driver, print, credentials['servopa']):
                print("✅ Login Servopa concluído!")
            else:
                raise Exception("Falha no login Servopa")
            
            # Abre nova aba para Todoist
            print_step(5, "Abrindo nova aba para Todoist")
            
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            print(f"✅ Nova aba aberta (Total: {len(driver.window_handles)} abas)")
            
            # Login Todoist
            print_step(6, "Fazendo login no Todoist")
            
            driver.get(TODOIST_URL)
            time.sleep(3)
            
            wait = WebDriverWait(driver, TIMEOUT)
            
            print("📋 Preenchendo email...")
            email_input = wait.until(EC.presence_of_element_located((By.ID, "element-0")))
            email_input.clear()
            for char in credentials['todoist']['usuario']:
                email_input.send_keys(char)
                time.sleep(0.05)
            
            time.sleep(1)
            
            print("🔐 Preenchendo senha...")
            password_input = wait.until(EC.presence_of_element_located((By.ID, "element-2")))
            password_input.clear()
            for char in credentials['todoist']['senha']:
                password_input.send_keys(char)
                time.sleep(0.05)
            
            time.sleep(1)
            
            print("🚀 Clicando em login...")
            login_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[type='submit']")
            ))
            login_button.click()
            
            print("⏳ Aguardando login processar...")
            time.sleep(10)
            
            print("✅ Login Todoist concluído!")
            
            # Navega para o board
            print_step(7, "Navegando para projeto do board")
            
            if navigate_to_board_project(driver, print):
                print("✅ Board aberto com sucesso")
            else:
                raise Exception("Falha ao abrir board")
            
            # Extrai board completo
            print_step(8, "Extraindo estrutura completa do board")
            
            board_data = extract_complete_board(driver, print)
            
            if not board_data or not board_data['sections']:
                raise Exception("Falha ao extrair board ou board vazio")
            
            total_tasks = sum(len(s['tasks']) for s in board_data['sections'])
            print(f"✅ Board extraído:")
            print(f"   📊 {len(board_data['sections'])} colunas")
            print(f"   📋 {total_tasks} tarefas")
            
            # Pergunta se deseja continuar
            print("\n" + "=" * 60)
            print("⚠️  ATENÇÃO: O próximo passo irá executar os lances!")
            print("=" * 60)
            
            resposta = input("\n❓ Deseja continuar com a execução dos lances? (s/N): ").strip().lower()
            
            if resposta != 's':
                print("\n⏹️  Teste cancelado pelo usuário")
                print("🔒 Navegador mantido aberto para verificação")
                input("\nPressione ENTER para fechar o navegador...")
                return True
            
            # Executa ciclo completo
            print_step(9, "Executando ciclo completo de lances")
            
            stats = executar_ciclo_completo(driver, board_data, print)
            
            if stats:
                print_header("TESTE CONCLUÍDO COM SUCESSO!")
                
                print("\n📊 ESTATÍSTICAS FINAIS:")
                print(f"   ✅ Tarefas concluídas: {stats['completed']}/{stats['total_tasks']}")
                print(f"   ❌ Tarefas com falha: {stats['failed']}/{stats['total_tasks']}")
                print(f"   📈 Taxa de sucesso: {(stats['completed']/stats['total_tasks']*100):.1f}%")
                
                print("\n🔒 Navegador mantido aberto para verificação")
                print("   Você pode verificar os lances manualmente")
                
                input("\nPressione ENTER para fechar o navegador...")
                
                return True
            else:
                raise Exception("Falha no ciclo de automação")
                
        finally:
            if driver:
                driver.quit()
                print("🔒 Navegador fechado")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        print("\n💡 Dicas:")
        print("  1. Verifique se as credenciais estão corretas em credentials.json")
        print("  2. Confirme que o Chrome está atualizado")
        print("  3. Verifique sua conexão com internet")
        print("  4. Veja os logs acima para mais detalhes")
        return False

def main():
    """Função principal"""
    try:
        success = test_cycle_complete()
        
        if success:
            print("\n✅ Teste finalizado com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Teste falhou!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido pelo usuário (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
