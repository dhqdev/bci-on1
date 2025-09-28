# main.py
# Orquestrador principal da automação completa Servopa + Todoist

import time
import sys
from login_servopa import login_servopa, navigate_to_consorcio_selection_and_fill
from login_todoist import login_todoist_and_extract_number

def main():
    """
    Executa o fluxo completo de automação:
    1. Login no Servopa
    2. Login no Todoist (nova aba) e extração do número
    3. Retorno ao Servopa para preenchimento do consórcio
    """
    print("=" * 60)
    print("🚀 INICIANDO AUTOMAÇÃO COMPLETA SERVOPA + TODOIST")
    print("=" * 60)
    
    driver = None
    
    try:
        # ETAPA 1: Login no Servopa
        print("\n📋 ETAPA 1: Fazendo login no Servopa...")
        driver = login_servopa(return_driver=True)
        
        if not driver:
            print("❌ ERRO: Falha no login do Servopa. Abortando automação.")
            return False
        
        print("✅ Login no Servopa realizado com sucesso!")
        
        # ETAPA 2: Login no Todoist e extração do número
        print("\n📋 ETAPA 2: Abrindo Todoist em nova aba e extraindo número...")
        extracted_number = login_todoist_and_extract_number(driver)
        
        if not extracted_number:
            print("❌ ERRO: Falha ao extrair o número do Todoist. Abortando automação.")
            return False
        
        print(f"✅ Número extraído com sucesso do Todoist: {extracted_number}")
        
        # ETAPA 3: Retorno ao Servopa para preenchimento
        print(f"\n📋 ETAPA 3: Preenchendo consórcio no Servopa com o número {extracted_number}...")
        success = navigate_to_consorcio_selection_and_fill(driver, extracted_number)
        
        if not success:
            print("❌ ERRO: Falha ao preencher o consórcio no Servopa.")
            return False
        
        print("✅ Consórcio preenchido com sucesso!")
        
        # FINALIZAÇÃO
        print("\n🎉 AUTOMAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
        print(f"   ➤ Número extraído do Todoist: {extracted_number}")
        print(f"   ➤ Consórcio preenchido no Servopa")
        print("   ➤ Screenshots salvas para verificação")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO na automação: {e}")
        return False
    
    finally:
        if driver:
            print("\n⏳ Mantendo navegador aberto para verificação...")
            print("   (Pressione Enter para fechar o navegador)")
            input()
            driver.quit()
            print("🔒 Navegador fechado.")

def test_individual_components():
    """
    Testa cada componente individualmente para debug
    """
    print("=" * 50)
    print("🔧 MODO DE TESTE - COMPONENTES INDIVIDUAIS")
    print("=" * 50)
    
    while True:
        print("\nEscolha o teste:")
        print("1. Testar apenas login Servopa")
        print("2. Testar apenas login Todoist")
        print("3. Testar automação completa")
        print("4. Sair")
        
        choice = input("\nOpção (1-4): ").strip()
        
        if choice == "1":
            print("\n🧪 Testando login Servopa...")
            driver = login_servopa(return_driver=True)
            if driver:
                print("✅ Login Servopa: SUCESSO")
                input("Pressione Enter para fechar...")
                driver.quit()
            else:
                print("❌ Login Servopa: FALHA")
                
        elif choice == "2":
            print("\n🧪 Testando login Todoist...")
            from login_todoist import test_todoist_login
            result = test_todoist_login()
            if result:
                print(f"✅ Login Todoist: SUCESSO - Número: {result}")
            else:
                print("❌ Login Todoist: FALHA")
                
        elif choice == "3":
            print("\n🧪 Testando automação completa...")
            success = main()
            if success:
                print("✅ Automação completa: SUCESSO")
            else:
                print("❌ Automação completa: FALHA")
                
        elif choice == "4":
            print("👋 Saindo...")
            break
            
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    print("🤖 SISTEMA DE AUTOMAÇÃO SERVOPA + TODOIST")
    print("Desenvolvido para extrair números do Todoist e preencher consórcios")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_individual_components()
    else:
        print("Iniciando automação completa...")
        print("(Use 'python main.py --test' para modo de teste)")
        print()
        
        success = main()
        
        if success:
            print("\n✅ Processo finalizado com SUCESSO!")
            sys.exit(0)
        else:
            print("\n❌ Processo finalizado com ERRO!")
            sys.exit(1)