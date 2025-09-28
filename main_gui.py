# main_gui.py
# Arquivo principal com interface gráfica

"""
🤖 Sistema de Automação Servopa + Todoist
===========================================

Sistema completo de automação com interface gráfica moderna.

Funcionalidades:
- ✅ Login automático no Servopa 
- ✅ Login automático no Todoist
- ✅ Extração de número de tarefa
- ✅ Busca e seleção de clientes
- ✅ Navegação para página de lances
- ✅ Interface visual em tempo real
- ✅ Logs detalhados e screenshots

Uso:
    python main_gui.py

Requisitos:
    pip install selenium webdriver-manager

Desenvolvido para integração Servopa + Todoist
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def main():
    """Função principal que inicia a interface gráfica"""
    try:
        # Adiciona o diretório atual ao path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Verifica dependências
        try:
            import selenium
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as e:
            error_msg = f"""
❌ Dependências não encontradas!

Erro: {e}

Para instalar as dependências necessárias, execute:
pip install -r requirements.txt

Dependências necessárias:
- selenium >= 4.15.0
- webdriver-manager >= 4.0.1
            """
            
            if 'tkinter' in sys.modules:
                messagebox.showerror("Erro de Dependências", error_msg)
            else:
                print(error_msg)
            return False
        
        # Importa e inicia a interface
        from ui.automation_gui import AutomationGUI
        
        print("🤖 Iniciando Sistema de Automação Servopa + Todoist")
        print("📱 Carregando interface gráfica...")
        
        # Cria e executa a aplicação
        app = AutomationGUI()
        app.run()
        
        return True
        
    except ImportError as e:
        error_msg = f"""
❌ Erro ao importar módulos!

Erro: {e}

Verifique se todos os arquivos estão na estrutura correta:
/auth/
  - servopa_auth.py
  - todoist_auth.py
  - __init__.py
/automation/
  - servopa_automation.py
  - __init__.py
/ui/
  - automation_gui.py
  - __init__.py
        """
        print(error_msg)
        return False
        
    except Exception as e:
        error_msg = f"❌ Erro inesperado: {e}"
        print(error_msg)
        
        if 'tkinter' in sys.modules:
            messagebox.showerror("Erro", error_msg)
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SISTEMA DE AUTOMAÇÃO SERVOPA + TODOIST")
    print("=" * 60)
    print()
    print("📋 Funcionalidades:")
    print("   • Login automático no Servopa")
    print("   • Extração de dados do Todoist")  
    print("   • Busca e seleção de clientes")
    print("   • Navegação para página de lances")
    print("   • Interface visual moderna")
    print("   • Logs em tempo real")
    print()
    print("🚀 Iniciando aplicação...")
    print()
    
    success = main()
    
    if success:
        print("✅ Aplicação finalizada com sucesso!")
    else:
        print("❌ Aplicação finalizada com erro!")
        sys.exit(1)