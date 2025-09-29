# ui/modern_automation_gui.py
# Interface moderna com abas e gerenciamento de credenciais - CORRIGIDA

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
from datetime import datetime
import queue

class ModernAutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Sistema de Automação Servopa + Todoist v3.0")
        self.root.geometry("1100x800")
        self.root.configure(bg='#f8f9fa')
        
        # Configuração de cores modernas
        self.colors = {
            'primary': '#0d6efd',
            'success': '#198754', 
            'warning': '#fd7e14',
            'danger': '#dc3545',
            'dark': '#212529',
            'light': '#f8f9fa',
            'secondary': '#6c757d',
            'white': '#ffffff',
            'gray_200': '#e9ecef',
        }
        
        # Estado da aplicação
        self.automation_running = False
        self.credentials_file = 'credentials.json'
        self.credential_entries = {}
        
        self.create_interface()
        self.message_queue = queue.Queue()
        self.setup_queue_processor()
        
        # Carrega credenciais após criar interface
        self.root.after(500, self.load_credentials)
        
    def create_interface(self):
        """Cria a interface completa"""
        # Container principal
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(main_frame, bg=self.colors['primary'], height=80)
        header.pack(fill='x', pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(header, text="🤖 Sistema de Automação Servopa + Todoist",
                font=('Arial', 16, 'bold'), bg=self.colors['primary'], fg='white').pack(pady=20)
        
        # Sistema de abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Criar abas
        self.create_automation_tab()
        self.create_credentials_tab()
        
    def create_automation_tab(self):
        """Cria aba de automação"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(tab_frame, text='🚀 Automação')
        
        # Cards de status
        status_frame = tk.LabelFrame(tab_frame, text="📊 Status do Sistema", font=('Arial', 12, 'bold'))
        status_frame.pack(fill='x', padx=20, pady=10)
        
        cards_container = tk.Frame(status_frame)
        cards_container.pack(fill='x', padx=10, pady=10)
        
        self.status_cards = {}
        status_items = [
            ("🌐 Servopa", "servopa"),
            ("📋 Todoist", "todoist"), 
            ("👤 Cliente", "cliente"),
            ("🎯 Lances", "lances")
        ]
        
        for i, (text, key) in enumerate(status_items):
            card = tk.Frame(cards_container, bg=self.colors['white'], relief='solid', bd=1, width=200, height=80)
            card.pack_propagate(False)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            
            tk.Label(card, text=text, font=('Arial', 10, 'bold'), bg=self.colors['white']).pack(pady=(10,5))
            status_label = tk.Label(card, text="⏳ Aguardando", font=('Arial', 9), 
                                  bg=self.colors['white'], fg=self.colors['secondary'])
            status_label.pack()
            self.status_cards[key] = status_label
            
        for i in range(4):
            cards_container.grid_columnconfigure(i, weight=1)
        
        # Progress
        progress_frame = tk.LabelFrame(tab_frame, text="⏳ Progresso", font=('Arial', 12, 'bold'))
        progress_frame.pack(fill='x', padx=20, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=10)
        
        self.progress_label = tk.Label(progress_frame, text="Sistema pronto", font=('Arial', 10))
        self.progress_label.pack(pady=5)
        
        # Dados extraídos
        self.data_frame = tk.Frame(progress_frame)
        self.data_frame.pack(fill='x', padx=10, pady=5)
        self.data_labels = {}
        
        # Log
        log_frame = tk.LabelFrame(tab_frame, text="📝 Log de Execução", font=('Arial', 12, 'bold'))
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=('Consolas', 9),
                                                bg='#1e1e1e', fg='#d4d4d4', wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure log tags
        self.log_text.tag_configure("SUCCESS", foreground="#4CAF50", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("ERROR", foreground="#F44336", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("WARNING", foreground="#FF9800", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("INFO", foreground="#2196F3", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("TIMESTAMP", foreground="#9E9E9E", font=('Consolas', 8))
        
        # Controles
        control_frame = tk.Frame(tab_frame, bg=self.colors['white'], relief='solid', bd=1, height=60)
        control_frame.pack(fill='x', padx=20, pady=10)
        control_frame.pack_propagate(False)
        
        # Botões
        button_frame = tk.Frame(control_frame, bg=self.colors['white'])
        button_frame.pack(side='left', padx=20, pady=15)
        
        self.start_button = tk.Button(button_frame, text="🚀 Iniciar Automação",
                                    font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white',
                                    command=self.start_automation, padx=20, pady=8, bd=0)
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = tk.Button(button_frame, text="⏸️ Parar",
                                   font=('Arial', 10, 'bold'), bg=self.colors['danger'], fg='white',
                                   command=self.stop_automation, padx=20, pady=8, bd=0, state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10))
        
        self.clear_button = tk.Button(button_frame, text="🗑️ Limpar Log",
                                    font=('Arial', 9), bg=self.colors['warning'], fg='white',
                                    command=self.clear_log, padx=15, pady=8, bd=0)
        self.clear_button.pack(side='left')
        
        # Status
        status_label_frame = tk.Frame(control_frame, bg=self.colors['white'])
        status_label_frame.pack(side='right', padx=20, pady=15)
        
        tk.Label(status_label_frame, text="Status:", font=('Arial', 10, 'bold'),
                bg=self.colors['white']).pack(side='left')
        
        self.general_status = tk.Label(status_label_frame, text="Sistema pronto",
                                     font=('Arial', 10, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['success'])
        self.general_status.pack(side='left', padx=(10, 0))
        
    def create_credentials_tab(self):
        """Cria aba de credenciais"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(tab_frame, text='🔐 Credenciais')
        
        # Container principal
        container = tk.Frame(tab_frame, bg=self.colors['light'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(container, text="🔐 Gerenciamento de Credenciais",
                font=('Arial', 14, 'bold'), bg=self.colors['light']).pack(anchor='w', pady=(0, 20))
        
        # Card Servopa
        servopa_frame = tk.LabelFrame(container, text="🌐 Servopa", font=('Arial', 12, 'bold'))
        servopa_frame.pack(fill='x', pady=(0, 20))
        
        servopa_content = tk.Frame(servopa_frame)
        servopa_content.pack(fill='x', padx=20, pady=15)
        
        tk.Label(servopa_content, text="👤 Usuário:", font=('Arial', 10, 'bold')).pack(anchor='w')
        servopa_user = tk.Entry(servopa_content, font=('Arial', 10), width=50)
        servopa_user.pack(fill='x', pady=(5, 10))
        
        tk.Label(servopa_content, text="🔒 Senha:", font=('Arial', 10, 'bold')).pack(anchor='w')
        servopa_pass = tk.Entry(servopa_content, font=('Arial', 10), width=50, show='*')
        servopa_pass.pack(fill='x', pady=(5, 0))
        
        self.credential_entries['servopa'] = {'user': servopa_user, 'pass': servopa_pass}
        
        # Card Todoist
        todoist_frame = tk.LabelFrame(container, text="📋 Todoist", font=('Arial', 12, 'bold'))
        todoist_frame.pack(fill='x', pady=(0, 20))
        
        todoist_content = tk.Frame(todoist_frame)
        todoist_content.pack(fill='x', padx=20, pady=15)
        
        tk.Label(todoist_content, text="👤 Usuário:", font=('Arial', 10, 'bold')).pack(anchor='w')
        todoist_user = tk.Entry(todoist_content, font=('Arial', 10), width=50)
        todoist_user.pack(fill='x', pady=(5, 10))
        
        tk.Label(todoist_content, text="🔒 Senha:", font=('Arial', 10, 'bold')).pack(anchor='w')
        todoist_pass = tk.Entry(todoist_content, font=('Arial', 10), width=50, show='*')
        todoist_pass.pack(fill='x', pady=(5, 0))
        
        self.credential_entries['todoist'] = {'user': todoist_user, 'pass': todoist_pass}
        
        # Botões de ação
        actions_frame = tk.Frame(container, bg=self.colors['light'])
        actions_frame.pack(fill='x', pady=20)
        
        save_button = tk.Button(actions_frame, text="💾 Salvar Credenciais",
                              font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white',
                              command=self.save_credentials, padx=20, pady=8, bd=0)
        save_button.pack(side='left', padx=(0, 10))
        
        reload_button = tk.Button(actions_frame, text="🔄 Recarregar",
                                font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white',
                                command=self.load_credentials, padx=20, pady=8, bd=0)
        reload_button.pack(side='left')
        
        # Status
        self.creds_status = tk.Label(actions_frame, text="", font=('Arial', 10),
                                   bg=self.colors['light'], fg=self.colors['success'])
        self.creds_status.pack(side='right')
        
    def load_credentials(self):
        """Carrega credenciais do arquivo JSON"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                
                # Preencher campos
                for service, data in credentials.items():
                    if service in self.credential_entries:
                        # Limpar e preencher usuário
                        user_entry = self.credential_entries[service]['user']
                        user_entry.delete(0, tk.END)
                        user_entry.insert(0, data.get('usuario', ''))
                        
                        # Limpar e preencher senha
                        pass_entry = self.credential_entries[service]['pass']
                        pass_entry.delete(0, tk.END)
                        pass_entry.insert(0, data.get('senha', ''))
                
                self.creds_status.config(text="✅ Credenciais carregadas", fg=self.colors['success'])
                print("✅ Credenciais carregadas com sucesso!")
            else:
                self.creds_status.config(text="⚠️ Arquivo não encontrado", fg=self.colors['warning'])
                
        except Exception as e:
            self.creds_status.config(text=f"❌ Erro ao carregar: {str(e)}", fg=self.colors['danger'])
            print(f"❌ Erro ao carregar credenciais: {e}")
            
    def save_credentials(self):
        """Salva credenciais no arquivo JSON"""
        try:
            credentials = {}
            
            for service, entries in self.credential_entries.items():
                credentials[service] = {
                    'usuario': entries['user'].get(),
                    'senha': entries['pass'].get()
                }
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2, ensure_ascii=False)
                
            self.creds_status.config(text="✅ Credenciais salvas com sucesso!", fg=self.colors['success'])
            print("✅ Credenciais salvas com sucesso!")
            
            # Limpar mensagem após 3 segundos
            self.root.after(3000, lambda: self.creds_status.config(text=""))
            
        except Exception as e:
            self.creds_status.config(text=f"❌ Erro ao salvar: {str(e)}", fg=self.colors['danger'])
            print(f"❌ Erro ao salvar credenciais: {e}")
    
    def setup_queue_processor(self):
        """Configura processador de mensagens da queue"""
        def process_queue():
            try:
                while True:
                    message = self.message_queue.get_nowait()
                    self.handle_message(message)
            except queue.Empty:
                pass
            finally:
                self.root.after(100, process_queue)
        
        process_queue()
        
    def handle_message(self, message):
        """Processa mensagens recebidas"""
        msg_type = message.get('type', 'info')
        content = message.get('content', '')
        
        if msg_type == 'log':
            self.add_log_message(content)
        elif msg_type == 'progress':
            self.update_progress(message.get('value', 0), content)
        elif msg_type == 'status':
            self.update_status(message.get('component'), message.get('status'))
        elif msg_type == 'data':
            self.update_extracted_data(message.get('key'), message.get('value'))
    
    def add_log_message(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determina o tipo de mensagem e tag
        tag = "INFO"
        if "✅" in message or "sucesso" in message.lower():
            tag = "SUCCESS"
        elif "❌" in message or "erro" in message.lower():
            tag = "ERROR"
        elif "⚠️" in message or "atenção" in message.lower():
            tag = "WARNING"
        
        # Adiciona ao log
        self.log_text.insert(tk.END, f"[{timestamp}] ", "TIMESTAMP")
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        
    def update_progress(self, value, message=""):
        """Atualiza barra de progresso"""
        self.progress_bar['value'] = value
        if message:
            self.progress_label.config(text=message)
        self.root.update_idletasks()
        
    def update_status(self, component, status):
        """Atualiza status de um componente"""
        if component in self.status_cards:
            self.status_cards[component].config(text=status)
            
            # Muda cor baseado no status
            if "✅" in status:
                self.status_cards[component].config(fg=self.colors['success'])
            elif "❌" in status:
                self.status_cards[component].config(fg=self.colors['danger'])
            elif "⏳" in status:
                self.status_cards[component].config(fg=self.colors['warning'])
                
    def update_extracted_data(self, key, value):
        """Atualiza dados extraídos"""
        if key not in self.data_labels:
            data_item = tk.Frame(self.data_frame)
            data_item.pack(side='left', padx=10)
            
            tk.Label(data_item, text=f"{key}:", font=('Arial', 9, 'bold')).pack(side='left')
            value_label = tk.Label(data_item, text=str(value), font=('Arial', 9), fg=self.colors['primary'])
            value_label.pack(side='left', padx=(5, 0))
            
            self.data_labels[key] = value_label
        else:
            self.data_labels[key].config(text=str(value))
    
    def progress_callback(self, message):
        """Callback para receber mensagens de progresso"""
        self.message_queue.put({
            'type': 'log',
            'content': message
        })
        
    def start_automation(self):
        """Inicia a automação"""
        self.automation_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.general_status.config(text="🚀 Executando...", fg=self.colors['warning'])
        
        # Inicia automação em thread separada
        self.automation_thread = threading.Thread(target=self.run_automation)
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def stop_automation(self):
        """Para a automação"""
        self.automation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.general_status.config(text="⏸️ Parado", fg=self.colors['danger'])
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)
        self.add_log_message("🗑️ Log limpo")
        
    def run_automation(self):
        """Executa a automação completa"""
        try:
            # Importa módulos necessários
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from auth.servopa_auth import create_driver, login_servopa
            from auth.todoist_auth import login_todoist_and_extract
            from automation.servopa_automation import complete_servopa_automation
            
            self.progress_callback("🚀 Iniciando Sistema de Automação...")
            self.update_progress(10, "Iniciando navegador Chrome...")
            
            # Cria driver
            driver = create_driver()
            
            try:
                # Login Servopa
                self.update_progress(20, "Fazendo login no Servopa...")
                self.message_queue.put({'type': 'status', 'component': 'servopa', 'status': '⏳ Fazendo login'})
                
                if login_servopa(driver, self.progress_callback):
                    self.message_queue.put({'type': 'status', 'component': 'servopa', 'status': '✅ Conectado'})
                    self.update_progress(40, "Login Servopa concluído")
                else:
                    raise Exception("Falha no login do Servopa")
                
                # Login Todoist
                self.update_progress(50, "Extraindo dados do Todoist...")
                self.message_queue.put({'type': 'status', 'component': 'todoist', 'status': '⏳ Extraindo dados'})
                
                numero_grupo = login_todoist_and_extract(driver, self.progress_callback)
                if numero_grupo:
                    self.message_queue.put({'type': 'status', 'component': 'todoist', 'status': '✅ Dados extraídos'})
                    self.message_queue.put({'type': 'data', 'key': 'Grupo', 'value': numero_grupo})
                    self.update_progress(70, f"Número {numero_grupo} extraído")
                else:
                    raise Exception("Falha na extração do Todoist")
                
                # Automação Servopa
                self.update_progress(80, "Executando automação no Servopa...")
                result = complete_servopa_automation(driver, numero_grupo, self.progress_callback)
                
                if result['success']:
                    self.message_queue.put({'type': 'status', 'component': 'cliente', 'status': '✅ Selecionado'})
                    self.message_queue.put({'type': 'status', 'component': 'lances', 'status': '✅ Acessado'})
                    
                    if result['client_name']:
                        self.message_queue.put({'type': 'data', 'key': 'Cliente', 'value': result['client_name']})
                    
                    self.update_progress(100, "Automação concluída!")
                    self.progress_callback("🎉 AUTOMAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
                    self.general_status.config(text="✅ Concluído", fg=self.colors['success'])
                else:
                    raise Exception("Falha na automação do Servopa")
                    
            finally:
                self.progress_callback("🔒 Navegador mantido aberto para verificação")
                
        except Exception as e:
            self.progress_callback(f"❌ Erro na automação: {e}")
            self.general_status.config(text="❌ Erro", fg=self.colors['danger'])
        finally:
            self.automation_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
    def run(self):
        """Executa a interface"""
        # Mensagens iniciais
        self.add_log_message("🤖 Sistema de Automação Servopa + Todoist v3.0 Iniciado")
        self.add_log_message("✨ Interface moderna carregada com sucesso")
        self.add_log_message("🔐 Aba de credenciais disponível - dados serão carregados automaticamente")
        self.add_log_message("⏳ Sistema pronto para iniciar automação")
        
        # Iniciar loop principal
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernAutomationGUI()
    app.run()
        
    def configure_styles(self):
        """Configura estilos personalizados modernos"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurações do Notebook (abas)
        style.configure('Modern.TNotebook', 
                       background=self.colors['light'],
                       borderwidth=0,
                       tabmargins=[0, 5, 0, 0])
        
        style.configure('Modern.TNotebook.Tab',
                       background=self.colors['gray_200'],
                       foreground=self.colors['dark'],
                       padding=[20, 12],
                       font=self.fonts['body_bold'],
                       borderwidth=0)
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['primary']),
                           ('active', self.colors['primary_light'])],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])
        
        # Botões modernos
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       font=self.fonts['body_bold'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_light']),
                           ('pressed', self.colors['primary'])])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       font=self.fonts['body_bold'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       font=self.fonts['body_bold'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       font=self.fonts['body_bold'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        # Frames modernos
        style.configure('Card.TFrame',
                       background=self.colors['white'],
                       relief='flat',
                       borderwidth=1)
        
        # Labels
        style.configure('Title.TLabel',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       font=self.fonts['title'])
        
        style.configure('Header.TLabel',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       font=self.fonts['header'])
        
        # Entradas
        style.configure('Modern.TEntry',
                       padding=8,
                       font=self.fonts['body'])
        
        # Progress bar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['gray_200'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
        
    def create_widgets(self):
        """Cria todos os widgets da interface moderna"""
        # Container principal
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header moderno
        self.create_modern_header(main_container)
        
        # Sistema de abas
        self.create_notebook(main_container)
        
    def create_modern_header(self, parent):
        """Cria cabeçalho moderno com gradiente simulado"""
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Container do conteúdo do header
        header_content = tk.Frame(header_frame, bg=self.colors['primary'])
        header_content.pack(expand=True, fill='both', padx=30, pady=20)
        
        # Título principal
        title_label = tk.Label(header_content,
                              text="🤖 Sistema de Automação Servopa + Todoist",
                              font=self.fonts['title'],
                              bg=self.colors['primary'],
                              fg='white')
        title_label.pack(anchor='w')
        
        # Subtítulo
        subtitle_label = tk.Label(header_content,
                                 text="Versão 3.0 - Interface Moderna com Gerenciamento de Credenciais",
                                 font=self.fonts['subtitle'],
                                 bg=self.colors['primary'],
                                 fg='white')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
    def create_notebook(self, parent):
        """Cria o sistema de abas moderno"""
        # Container para as abas
        notebook_container = tk.Frame(parent, bg=self.colors['light'])
        notebook_container.pack(fill='both', expand=True)
        
        # Notebook (sistema de abas)
        self.notebook = ttk.Notebook(notebook_container, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Aba 1: Automação
        self.create_automation_tab()
        
        # Aba 2: Credenciais  
        self.create_credentials_tab()
        
    def create_automation_tab(self):
        """Cria aba de automação"""
        # Frame principal da aba
        automation_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(automation_frame, text='🚀 Automação')
        
        # Container com padding
        container = tk.Frame(automation_frame, bg=self.colors['light'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Status cards
        self.create_status_cards(container)
        
        # Progress section
        self.create_progress_section(container)
        
        # Log section
        self.create_log_section(container)
        
        # Control panel
        self.create_control_panel(container)
        
    def create_status_cards(self, parent):
        """Cria cards de status modernos"""
        status_container = tk.Frame(parent, bg=self.colors['light'])
        status_container.pack(fill='x', pady=(0, 20))
        
        # Título da seção
        section_title = tk.Label(status_container,
                                text="📊 Status do Sistema",
                                font=self.fonts['header'],
                                bg=self.colors['light'],
                                fg=self.colors['dark'])
        section_title.pack(anchor='w', pady=(0, 15))
        
        # Grid de cards
        cards_frame = tk.Frame(status_container, bg=self.colors['light'])
        cards_frame.pack(fill='x')
        
        # Configuração dos cards
        self.status_cards = {}
        cards_config = [
            ("🌐 Servopa", "servopa", self.colors['info']),
            ("📋 Todoist", "todoist", self.colors['success']),
            ("👤 Cliente", "cliente", self.colors['warning']),
            ("🎯 Lances", "lances", self.colors['primary'])
        ]
        
        for i, (title, key, color) in enumerate(cards_config):
            card = self.create_status_card(cards_frame, title, key, color)
            card.grid(row=0, column=i, padx=(0, 15) if i < 3 else 0, sticky='ew', pady=10)
            
        # Configurar grid
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
            
    def create_status_card(self, parent, title, key, color):
        """Cria um card de status individual"""
        card_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1, height=120, width=200)
        card_frame.pack_propagate(False)
        
        # Header do card
        header = tk.Frame(card_frame, bg=color, height=8)
        header.pack(fill='x')
        
        # Conteúdo do card
        content = tk.Frame(card_frame, bg=self.colors['white'])
        content.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título
        title_label = tk.Label(content,
                              text=title,
                              font=self.fonts['body_bold'],
                              bg=self.colors['white'],
                              fg=self.colors['dark'])
        title_label.pack(anchor='w')
        
        # Status
        status_label = tk.Label(content,
                               text="⏳ Aguardando",
                               font=self.fonts['body'],
                               bg=self.colors['white'],
                               fg=self.colors['secondary'])
        status_label.pack(anchor='w', pady=(5, 0))
        
        self.status_cards[key] = status_label
        
        return card_frame
        
    def create_progress_section(self, parent):
        """Cria seção de progresso moderna"""
        progress_container = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        progress_container.pack(fill='x', pady=(0, 20))
        
        # Padding interno
        progress_content = tk.Frame(progress_container, bg=self.colors['white'])
        progress_content.pack(fill='x', padx=20, pady=20)
        
        # Título
        title_label = tk.Label(progress_content,
                              text="⏳ Progresso da Automação",
                              font=self.fonts['header'],
                              bg=self.colors['white'],
                              fg=self.colors['dark'])
        title_label.pack(anchor='w', pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_content,
                                          mode='determinate',
                                          style='Modern.Horizontal.TProgressbar',
                                          length=400)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        # Progress label
        self.progress_label = tk.Label(progress_content,
                                     text="Sistema pronto para iniciar",
                                     font=self.fonts['body'],
                                     bg=self.colors['white'],
                                     fg=self.colors['secondary'])
        self.progress_label.pack(anchor='w')
        
        # Dados extraídos
        self.data_frame = tk.Frame(progress_content, bg=self.colors['white'])
        self.data_frame.pack(fill='x', pady=(15, 0))
        
        self.data_labels = {}
        
    def create_log_section(self, parent):
        """Cria seção de log moderna"""
        log_container = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        log_container.pack(fill='both', expand=True, pady=(0, 20))
        
        # Header do log
        log_header = tk.Frame(log_container, bg=self.colors['gray_100'])
        log_header.pack(fill='x', padx=1, pady=(1, 0))
        
        # Título do log
        log_title = tk.Label(log_header,
                           text="📝 Log de Execução",
                           font=self.fonts['header'],
                           bg=self.colors['gray_100'],
                           fg=self.colors['dark'])
        log_title.pack(side='left', padx=20, pady=10)
        
        # Botão limpar log
        clear_btn = ttk.Button(log_header,
                             text="🗑️ Limpar",
                             command=self.clear_log,
                             style='Warning.TButton')
        clear_btn.pack(side='right', padx=20, pady=10)
        
        # Área de texto do log
        log_content = tk.Frame(log_container, bg=self.colors['white'])
        log_content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(log_content,
                                                height=12,
                                                font=self.fonts['code'],
                                                bg='#1e1e1e',
                                                fg='#d4d4d4',
                                                wrap=tk.WORD,
                                                relief='flat',
                                                bd=0)
        self.log_text.pack(fill='both', expand=True)
        
        # Configurar tags de cores para o log
        self.configure_log_tags()
        
    def configure_log_tags(self):
        """Configura tags de cores para o log"""
        self.log_text.tag_configure("SUCCESS", 
                                  foreground="#4CAF50", 
                                  font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("ERROR", 
                                  foreground="#F44336", 
                                  font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("WARNING", 
                                  foreground="#FF9800", 
                                  font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("INFO", 
                                  foreground="#2196F3", 
                                  font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("TIMESTAMP", 
                                  foreground="#9E9E9E", 
                                  font=('Consolas', 8))
        
    def create_control_panel(self, parent):
        """Cria painel de controle moderno"""
        control_container = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        control_container.pack(fill='x')
        
        # Conteúdo com padding
        control_content = tk.Frame(control_container, bg=self.colors['white'])
        control_content.pack(fill='x', padx=20, pady=20)
        
        # Frame dos botões
        buttons_frame = tk.Frame(control_content, bg=self.colors['white'])
        buttons_frame.pack(side='left')
        
        # Botões de controle
        self.start_button = ttk.Button(buttons_frame,
                                     text="🚀 Iniciar Automação",
                                     style='Success.TButton',
                                     command=self.start_automation)
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(buttons_frame,
                                    text="⏸️ Parar",
                                    style='Danger.TButton',
                                    command=self.stop_automation,
                                    state='disabled')
        self.stop_button.pack(side='left')
        
        # Status geral
        status_frame = tk.Frame(control_content, bg=self.colors['white'])
        status_frame.pack(side='right')
        
        status_label = tk.Label(status_frame,
                              text="Status:",
                              font=self.fonts['body_bold'],
                              bg=self.colors['white'],
                              fg=self.colors['dark'])
        status_label.pack(side='left', padx=(0, 10))
        
        self.general_status = tk.Label(status_frame,
                                     text="Sistema pronto",
                                     font=self.fonts['body_bold'],
                                     bg=self.colors['white'],
                                     fg=self.colors['success'])
        self.general_status.pack(side='left')
        
    def create_credentials_tab(self):
        """Cria aba de credenciais"""
        # Frame principal da aba
        credentials_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(credentials_frame, text='🔐 Credenciais')
        
        # Container com padding
        container = tk.Frame(credentials_frame, bg=self.colors['light'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título da seção
        title_label = tk.Label(container,
                              text="🔐 Gerenciamento de Credenciais",
                              font=self.fonts['header'],
                              bg=self.colors['light'],
                              fg=self.colors['dark'])
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Container principal das credenciais
        creds_container = tk.Frame(container, bg=self.colors['light'])
        creds_container.pack(fill='both', expand=True)
        
        # Cards de credenciais
        self.create_credentials_cards(creds_container)
        
    def create_credentials_cards(self, parent):
        """Cria cards para gerenciar credenciais"""
        # Container dos cards
        cards_container = tk.Frame(parent, bg=self.colors['light'])
        cards_container.pack(fill='x')
        
        # Variáveis para armazenar as entradas
        self.credential_entries = {}
        
        # Card Servopa
        servopa_card = self.create_credential_card(
            cards_container, 
            "🌐 Servopa", 
            "servopa",
            "Credenciais para acesso ao sistema Servopa"
        )
        servopa_card.pack(fill='x', pady=(0, 20))
        
        # Card Todoist
        todoist_card = self.create_credential_card(
            cards_container,
            "📋 Todoist", 
            "todoist",
            "Credenciais para acesso ao Todoist"
        )
        todoist_card.pack(fill='x', pady=(0, 20))
        
        # Botões de ação
        actions_frame = tk.Frame(cards_container, bg=self.colors['light'])
        actions_frame.pack(fill='x', pady=20)
        
        save_button = ttk.Button(actions_frame,
                               text="💾 Salvar Credenciais",
                               style='Success.TButton',
                               command=self.save_credentials)
        save_button.pack(side='left', padx=(0, 10))
        
        reload_button = ttk.Button(actions_frame,
                                 text="🔄 Recarregar",
                                 style='Primary.TButton',
                                 command=self.load_credentials)
        reload_button.pack(side='left')
        
        # Status das credenciais
        self.creds_status = tk.Label(actions_frame,
                                   text="",
                                   font=self.fonts['body'],
                                   bg=self.colors['light'],
                                   fg=self.colors['success'])
        self.creds_status.pack(side='right')
        
    def create_credential_card(self, parent, title, service, description):
        """Cria um card individual para credenciais"""
        # Card principal
        card = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        
        # Header do card
        header = tk.Frame(card, bg=self.colors['primary'], height=8)
        header.pack(fill='x')
        
        # Conteúdo do card
        content = tk.Frame(card, bg=self.colors['white'])
        content.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Título e descrição
        title_label = tk.Label(content,
                              text=title,
                              font=self.fonts['header'],
                              bg=self.colors['white'],
                              fg=self.colors['dark'])
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(content,
                             text=description,
                             font=self.fonts['small'],
                             bg=self.colors['white'],
                             fg=self.colors['secondary'])
        desc_label.pack(anchor='w', pady=(5, 15))
        
        # Frame dos campos
        fields_frame = tk.Frame(content, bg=self.colors['white'])
        fields_frame.pack(fill='x')
        
        # Campo usuário
        user_frame = tk.Frame(fields_frame, bg=self.colors['white'])
        user_frame.pack(fill='x', pady=(0, 15))
        
        user_label = tk.Label(user_frame,
                             text="👤 Usuário:",
                             font=self.fonts['body_bold'],
                             bg=self.colors['white'],
                             fg=self.colors['dark'])
        user_label.pack(anchor='w', pady=(0, 5))
        
        user_entry = ttk.Entry(user_frame,
                              font=self.fonts['body'],
                              style='Modern.TEntry',
                              width=50)
        user_entry.pack(fill='x')
        
        # Campo senha
        pass_frame = tk.Frame(fields_frame, bg=self.colors['white'])
        pass_frame.pack(fill='x')
        
        pass_label = tk.Label(pass_frame,
                             text="🔒 Senha:",
                             font=self.fonts['body_bold'],
                             bg=self.colors['white'],
                             fg=self.colors['dark'])
        pass_label.pack(anchor='w', pady=(0, 5))
        
        pass_entry = ttk.Entry(pass_frame,
                              font=self.fonts['body'],
                              style='Modern.TEntry',
                              width=50,
                              show='*')
        pass_entry.pack(fill='x')
        
        # Botão toggle senha
        toggle_frame = tk.Frame(pass_frame, bg=self.colors['white'])
        toggle_frame.pack(fill='x', pady=(5, 0))
        
        def toggle_password():
            if pass_entry['show'] == '*':
                pass_entry.configure(show='')
                toggle_btn.configure(text='🙈 Ocultar')
            else:
                pass_entry.configure(show='*')
                toggle_btn.configure(text='👁️ Mostrar')
        
        toggle_btn = tk.Button(toggle_frame,
                              text='👁️ Mostrar',
                              font=self.fonts['small'],
                              bg=self.colors['gray_200'],
                              fg=self.colors['dark'],
                              relief='flat',
                              bd=0,
                              command=toggle_password)
        toggle_btn.pack(side='left')
        
        # Armazenar referências
        self.credential_entries[service] = {
            'user': user_entry,
            'pass': pass_entry
        }
        
        return card
        
    def load_credentials(self):
        """Carrega credenciais do arquivo JSON"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                
                # Preencher campos
                for service, data in credentials.items():
                    if service in self.credential_entries:
                        self.credential_entries[service]['user'].delete(0, tk.END)
                        self.credential_entries[service]['user'].insert(0, data.get('usuario', ''))
                        
                        self.credential_entries[service]['pass'].delete(0, tk.END) 
                        self.credential_entries[service]['pass'].insert(0, data.get('senha', ''))
                
                self.creds_status.config(text="✅ Credenciais carregadas", fg=self.colors['success'])
            else:
                self.creds_status.config(text="⚠️ Arquivo não encontrado", fg=self.colors['warning'])
                
        except Exception as e:
            self.creds_status.config(text=f"❌ Erro ao carregar: {str(e)}", fg=self.colors['danger'])
            
    def save_credentials(self):
        """Salva credenciais no arquivo JSON"""
        try:
            credentials = {}
            
            for service, entries in self.credential_entries.items():
                credentials[service] = {
                    'usuario': entries['user'].get(),
                    'senha': entries['pass'].get()
                }
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2, ensure_ascii=False)
                
            self.creds_status.config(text="✅ Credenciais salvas com sucesso!", fg=self.colors['success'])
            
            # Limpar mensagem após 3 segundos
            self.root.after(3000, lambda: self.creds_status.config(text=""))
            
        except Exception as e:
            self.creds_status.config(text=f"❌ Erro ao salvar: {str(e)}", fg=self.colors['danger'])
    
    def setup_queue_processor(self):
        """Configura processador de mensagens da queue"""
        def process_queue():
            try:
                while True:
                    message = self.message_queue.get_nowait()
                    self.handle_message(message)
            except queue.Empty:
                pass
            finally:
                self.root.after(100, process_queue)
        
        process_queue()
        
    def handle_message(self, message):
        """Processa mensagens recebidas"""
        msg_type = message.get('type', 'info')
        content = message.get('content', '')
        
        if msg_type == 'log':
            self.add_log_message(content)
        elif msg_type == 'progress':
            self.update_progress(message.get('value', 0), content)
        elif msg_type == 'status':
            self.update_status(message.get('component'), message.get('status'))
        elif msg_type == 'data':
            self.update_extracted_data(message.get('key'), message.get('value'))
    
    def add_log_message(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determina o tipo de mensagem e tag
        tag = "INFO"
        if "✅" in message or "sucesso" in message.lower():
            tag = "SUCCESS"
        elif "❌" in message or "erro" in message.lower():
            tag = "ERROR"
        elif "⚠️" in message or "atenção" in message.lower():
            tag = "WARNING"
        
        # Adiciona ao log
        self.log_text.insert(tk.END, f"[{timestamp}] ", "TIMESTAMP")
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        
    def update_progress(self, value, message=""):
        """Atualiza barra de progresso"""
        self.progress_bar['value'] = value
        if message:
            self.progress_label.config(text=message)
        self.root.update_idletasks()
        
    def update_status(self, component, status):
        """Atualiza status de um componente"""
        if component in self.status_cards:
            self.status_cards[component].config(text=status)
            
            # Muda cor baseado no status
            if "✅" in status:
                self.status_cards[component].config(fg=self.colors['success'])
            elif "❌" in status:
                self.status_cards[component].config(fg=self.colors['danger'])
            elif "⏳" in status:
                self.status_cards[component].config(fg=self.colors['warning'])
                
    def update_extracted_data(self, key, value):
        """Atualiza dados extraídos"""
        if key not in self.data_labels:
            # Criar novo badge de dados
            badge_frame = tk.Frame(self.data_frame, bg=self.colors['primary'], relief='flat')
            badge_frame.pack(side='left', padx=(0, 10), pady=2)
            
            key_label = tk.Label(badge_frame,
                               text=f"{key}:",
                               font=self.fonts['small'],
                               bg=self.colors['primary'],
                               fg='white',
                               padx=8, pady=4)
            key_label.pack(side='left')
            
            value_label = tk.Label(badge_frame,
                                 text=str(value),
                                 font=('Segoe UI', 9, 'bold'),
                                 bg=self.colors['white'],
                                 fg=self.colors['primary'],
                                 padx=8, pady=4)
            value_label.pack(side='left')
            
            self.data_labels[key] = value_label
        else:
            self.data_labels[key].config(text=str(value))
    
    def progress_callback(self, message):
        """Callback para receber mensagens de progresso"""
        self.message_queue.put({
            'type': 'log',
            'content': message
        })
        
    def start_automation(self):
        """Inicia a automação"""
        self.automation_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.general_status.config(text="🚀 Executando...", fg=self.colors['warning'])
        
        # Inicia automação em thread separada
        self.automation_thread = threading.Thread(target=self.run_automation)
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def stop_automation(self):
        """Para a automação"""
        self.automation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.general_status.config(text="⏸️ Parado", fg=self.colors['danger'])
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)
        self.add_log_message("🗑️ Log limpo")
        
    def run_automation(self):
        """Executa a automação completa"""
        try:
            # Importa módulos necessários
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from auth.servopa_auth import create_driver, login_servopa
            from auth.todoist_auth import login_todoist_and_extract
            from automation.servopa_automation import complete_servopa_automation
            
            self.progress_callback("🚀 Iniciando Sistema de Automação Moderna...")
            self.update_progress(10, "Iniciando navegador Chrome...")
            
            # Cria driver
            driver = create_driver()
            
            try:
                # Login Servopa
                self.update_progress(20, "Fazendo login no Servopa...")
                self.message_queue.put({'type': 'status', 'component': 'servopa', 'status': '⏳ Fazendo login'})
                
                if login_servopa(driver, self.progress_callback):
                    self.message_queue.put({'type': 'status', 'component': 'servopa', 'status': '✅ Conectado'})
                    self.update_progress(40, "Login Servopa concluído com sucesso")
                else:
                    raise Exception("Falha no login do Servopa")
                
                # Login Todoist
                self.update_progress(50, "Extraindo dados do Todoist...")
                self.message_queue.put({'type': 'status', 'component': 'todoist', 'status': '⏳ Extraindo dados'})
                
                numero_grupo = login_todoist_and_extract(driver, self.progress_callback)
                if numero_grupo:
                    self.message_queue.put({'type': 'status', 'component': 'todoist', 'status': '✅ Dados extraídos'})
                    self.message_queue.put({'type': 'data', 'key': 'Grupo', 'value': numero_grupo})
                    self.update_progress(70, f"Número do grupo {numero_grupo} extraído")
                else:
                    raise Exception("Falha na extração do Todoist")
                
                # Automação Servopa
                self.update_progress(80, "Executando automação no Servopa...")
                result = complete_servopa_automation(driver, numero_grupo, self.progress_callback)
                
                if result['success']:
                    self.message_queue.put({'type': 'status', 'component': 'cliente', 'status': '✅ Selecionado'})
                    self.message_queue.put({'type': 'status', 'component': 'lances', 'status': '✅ Acessado'})
                    
                    if result['client_name']:
                        self.message_queue.put({'type': 'data', 'key': 'Cliente', 'value': result['client_name']})
                    
                    self.update_progress(100, "🎉 Automação concluída com sucesso!")
                    self.progress_callback("🎉 AUTOMAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
                    self.general_status.config(text="✅ Concluído", fg=self.colors['success'])
                else:
                    raise Exception("Falha na automação do Servopa")
                    
            finally:
                # Mantém navegador aberto para verificação
                self.progress_callback("🔒 Navegador mantido aberto - TODAS as abas disponíveis para verificação")
                self.progress_callback("📋 Aba do Todoist: Disponível para consulta")
                self.progress_callback("🌐 Aba do Servopa: Pronta para uso")
                
        except Exception as e:
            self.progress_callback(f"❌ Erro na automação: {e}")
            self.general_status.config(text="❌ Erro", fg=self.colors['danger'])
        finally:
            self.automation_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
    def run(self):
        """Executa a interface"""
        # Mensagens iniciais
        self.add_log_message("🤖 Sistema de Automação Servopa + Todoist v3.0 Iniciado")
        self.add_log_message("✨ Interface moderna com abas carregada com sucesso")
        self.add_log_message("🔐 Sistema de credenciais disponível na aba 'Credenciais'")
        self.add_log_message("⏳ Sistema pronto para iniciar automação")
        
        # Iniciar loop principal
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernAutomationGUI()
    app.run()
