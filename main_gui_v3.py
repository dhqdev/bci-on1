# main_gui_v3.py
# Interface gráfica melhorada com abas e extração do Todolist

"""
🤖 Sistema de Automação Servopa + Todoist - Versão 3.0
========================================================

Sistema completo de automação com interface moderna:
- ✅ Interface com abas
- ✅ Seção de credenciais simplificada  
- ✅ Extração de dados do Todolist
- ✅ Análise de HTML com números de cota e nomes
- ✅ Tabelas interativas para resultados

Uso:
    python main_gui_v3.py

Desenvolvido para integração Servopa + Todoist + Extração
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

def main():
    """Função principal que inicia a interface gráfica melhorada"""
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
        
        # Importa e inicia a nova interface
        from ui.modern_automation_gui import ModernAutomationGUI
        
        print("🤖 Iniciando Sistema de Automação Servopa + Todoist v3.0")
        print("📱 Carregando interface gráfica moderna...")
        
        # Cria e executa a aplicação
        app = ModernAutomationGUI()
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
  - modern_automation_gui.py
  - __init__.py
/utils/
  - todolist_extractor.py
        """
        print(error_msg)
        return False
        
    except Exception as e:
        error_msg = f"❌ Erro inesperado: {e}"
        print(error_msg)
        return False

if __name__ == "__main__":
    main()