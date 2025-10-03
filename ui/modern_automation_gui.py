# ui/modern_automation_gui.py
# Interface moderna com abas e gerenciamento de credenciais

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
from datetime import datetime
import queue
import sys

# Bloqueia acesso direto ao sistema desktop
ALLOW_DESKTOP_ACCESS = False

class ModernAutomationGUI:
    def __init__(self):
        if not ALLOW_DESKTOP_ACCESS:
            print("=" * 80)
            print("⚠️  AVISO: Interface Desktop Desabilitada")
            print("=" * 80)
            print()
            print("🌐 O sistema agora funciona apenas via interface WEB.")
            print()
            print("📌 Para usar o sistema, execute:")
            print("   cd web && python app.py")
            print()
            print("🌍 Depois acesse: http://localhost:5000")
            print()
            print("=" * 80)
            sys.exit(0)
        
        self.root = tk.Tk()
        self.root.title("🏆 OXCASH - Sistema de Automação Profissional")
        self.root.geometry("1200x850")
        
        # Configurar ícone da janela (se existir)
        try:
            # self.root.iconbitmap('icon.ico')  # Descomente se tiver ícone
            pass
        except:
            pass
        
        # Cores modernas e profissionais
        self.colors = {
            'primary': '#1e3a8a',      # Azul escuro profissional
            'secondary': '#3b82f6',     # Azul médio
            'success': '#10b981',       # Verde
            'warning': '#f59e0b',       # Laranja
            'danger': '#ef4444',        # Vermelho
            'light': '#f8fafc',         # Cinza muito claro
            'dark': '#1e293b',          # Cinza escuro
            'white': '#ffffff',
            'border': '#e2e8f0',
            'text': '#334155',
            'text_light': '#64748b'
        }
        
        self.root.configure(bg=self.colors['light'])
        
        # Estado da aplicação
        self.automation_running = False
        self.automation_running_dia16 = False
        self.credentials_file = 'credentials.json'
        self.driver = None  # Armazena referência do driver
        self.driver_dia16 = None  # Armazena referência do driver para Dia 16
        
        # Variáveis para credenciais
        self.servopa_login_var = tk.StringVar()
        self.servopa_senha_var = tk.StringVar()
        self.todoist_login_var = tk.StringVar()
        self.todoist_senha_var = tk.StringVar()
        
        self.create_interface()
        self.message_queue = queue.Queue()
        self.setup_queue_processor()
        
        # Carrega credenciais após criar interface
        self.root.after(500, self.load_credentials)
        
    def create_interface(self):
        """Cria a interface com abas"""
        # ========== HEADER PROFISSIONAL ==========
        header = tk.Frame(self.root, bg=self.colors['primary'], height=120)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Container centralizado do header
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo/Ícone (usando emoji grande)
        logo_frame = tk.Frame(header_content, bg=self.colors['primary'])
        logo_frame.pack(side='left', padx=(0, 20))
        
        tk.Label(logo_frame, text="🏆", font=('Arial', 48), bg=self.colors['primary']).pack()
        
        # Textos do header
        text_frame = tk.Frame(header_content, bg=self.colors['primary'])
        text_frame.pack(side='left')
        
        tk.Label(text_frame, 
                text="AUTOMAÇÕES PARA OXCASH",
                font=('Arial', 24, 'bold'), 
                bg=self.colors['primary'], 
                fg=self.colors['white']).pack(anchor='w')
        
        tk.Label(text_frame, 
                text="Sistema Profissional de Automação • Servopa + Todoist + WhatsApp",
                font=('Arial', 11), 
                bg=self.colors['primary'], 
                fg=self.colors['light']).pack(anchor='w', pady=(5, 0))
        
        # Linha decorativa abaixo do header
        separator = tk.Frame(self.root, bg=self.colors['secondary'], height=4)
        separator.pack(fill='x')
        
        # ========== SISTEMA DE ABAS ESTILIZADO ==========
        # Container para abas com padding
        tabs_container = tk.Frame(self.root, bg=self.colors['light'])
        tabs_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Estilo customizado para as abas
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilo das abas
        style.configure('Custom.TNotebook', 
                       background=self.colors['light'],
                       borderwidth=0)
        style.configure('Custom.TNotebook.Tab', 
                       background=self.colors['white'],
                       foreground=self.colors['text'],
                       padding=[20, 10],
                       font=('Arial', 10, 'bold'),
                       borderwidth=1)
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', self.colors['secondary'])],
                 foreground=[('selected', self.colors['white'])],
                 expand=[('selected', [1, 1, 1, 0])])
        
        self.notebook = ttk.Notebook(tabs_container, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Criar todas as abas
        self.create_automation_tab()
        self.create_automation_tab_dia16()
        self.create_boletos_tab()  # NOVA: Aba de Boletos
        self.create_credentials_tab()
        self.create_whatsapp_tab()  # Aba unificada de WhatsApp
        self.create_history_tab()
        self.create_history_tab_dia16()
        
    def create_automation_tab(self):
        """Aba de automação com visual moderno"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(tab_frame, text='🚀 Automação Dia 8')
        
        # Container principal com padding
        main_container = tk.Frame(tab_frame, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ========== CARDS DE STATUS MODERNOS ==========
        status_section = tk.Frame(main_container, bg=self.colors['light'])
        status_section.pack(fill='x', pady=(0, 20))
        
        tk.Label(status_section, text="📊 Status em Tempo Real", 
                font=('Arial', 14, 'bold'), 
                bg=self.colors['light'],
                fg=self.colors['dark']).pack(anchor='w', pady=(0, 15))
        
        cards_container = tk.Frame(status_section, bg=self.colors['light'])
        cards_container.pack(fill='x')
        
        # Cards de status com ícones e cores
        self.status_cards = {}
        card_configs = [
            ("🌐", "Servopa", "servopa", self.colors['secondary']),
            ("📋", "Todoist", "todoist", self.colors['success']),
            ("👤", "Cliente", "cliente", self.colors['warning']),
            ("🎯", "Lances", "lances", self.colors['primary'])
        ]
        
        for i, (icon, text, key, color) in enumerate(card_configs):
            # Card com sombra simulada
            card_outer = tk.Frame(cards_container, bg=self.colors['border'], 
                                 relief='flat', bd=0)
            card_outer.grid(row=0, column=i, padx=8, pady=5, sticky='ew')
            
            card = tk.Frame(card_outer, bg=self.colors['white'], 
                           relief='flat', bd=0)
            card.pack(padx=1, pady=1, fill='both', expand=True)
            
            # Barra de cor no topo
            color_bar = tk.Frame(card, bg=color, height=4)
            color_bar.pack(fill='x')
            
            # Conteúdo do card
            content = tk.Frame(card, bg=self.colors['white'])
            content.pack(fill='both', expand=True, padx=15, pady=12)
            
            # Ícone e título
            header = tk.Frame(content, bg=self.colors['white'])
            header.pack(fill='x')
            
            tk.Label(header, text=icon, font=('Arial', 20), 
                    bg=self.colors['white']).pack(side='left', padx=(0, 10))
            tk.Label(header, text=text, font=('Arial', 11, 'bold'), 
                    bg=self.colors['white'], fg=self.colors['dark']).pack(side='left')
            
            # Status
            status_label = tk.Label(content, text="Aguardando", 
                                   font=('Arial', 9), 
                                   bg=self.colors['white'], 
                                   fg=self.colors['text_light'])
            status_label.pack(anchor='w', pady=(8, 0))
            self.status_cards[key] = status_label
            
        for i in range(4):
            cards_container.grid_columnconfigure(i, weight=1)
        
        # ========== BARRA DE PROGRESSO MODERNA ==========
        progress_section = tk.Frame(main_container, bg=self.colors['white'], 
                                    relief='flat', bd=0)
        progress_section.pack(fill='x', pady=(0, 20))
        
        # Borda simulando sombra
        progress_border = tk.Frame(main_container, bg=self.colors['border'])
        progress_border.pack(fill='x', pady=(0, 20))
        progress_inner = tk.Frame(progress_border, bg=self.colors['white'])
        progress_inner.pack(padx=1, pady=1, fill='x')
        
        progress_content = tk.Frame(progress_inner, bg=self.colors['white'])
        progress_content.pack(fill='x', padx=20, pady=20)
        
        tk.Label(progress_content, text="⚡ Progresso da Automação", 
                font=('Arial', 12, 'bold'), 
                bg=self.colors['white'],
                fg=self.colors['dark']).pack(anchor='w', pady=(0, 10))
        
        # Estilo da barra de progresso
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", 
                       background=self.colors['secondary'],
                       troughcolor=self.colors['light'],
                       borderwidth=0,
                       thickness=20)
        
        self.progress_bar = ttk.Progressbar(progress_content, 
                                           style="Custom.Horizontal.TProgressbar",
                                           mode='determinate')
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        self.progress_label = tk.Label(progress_content, 
                                      text="Sistema pronto para iniciar", 
                                      font=('Arial', 10),
                                      bg=self.colors['white'],
                                      fg=self.colors['text_light'])
        self.progress_label.pack(anchor='w')
        
        # ========== LOG MODERNO ==========
        log_section = tk.Frame(main_container, bg=self.colors['white'])
        log_section.pack(fill='both', expand=True)
        
        # Borda do log
        log_border = tk.Frame(main_container, bg=self.colors['border'])
        log_border.pack(fill='both', expand=True)
        log_inner = tk.Frame(log_border, bg=self.colors['white'])
        log_inner.pack(padx=1, pady=1, fill='both', expand=True)
        
        log_header = tk.Frame(log_inner, bg=self.colors['white'])
        log_header.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(log_header, text="📝 Log de Atividades", 
                font=('Arial', 12, 'bold'), 
                bg=self.colors['white'],
                fg=self.colors['dark']).pack(side='left')
        
        self.log_text = scrolledtext.ScrolledText(log_inner, height=12, 
                                                font=('Consolas', 9),
                                                bg='#0f172a', 
                                                fg='#e2e8f0', 
                                                wrap=tk.WORD,
                                                relief='flat',
                                                borderwidth=0)
        self.log_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # ========== BOTÕES DE AÇÃO MODERNOS ==========
        button_section = tk.Frame(main_container, bg=self.colors['light'])
        button_section.pack(fill='x', pady=(20, 0))
        
        button_container = tk.Frame(button_section, bg=self.colors['light'])
        button_container.pack(fill='x')
        
        # Botão Iniciar
        self.start_button = tk.Button(button_container, 
                                     text="🚀 INICIAR AUTOMAÇÃO", 
                                     font=('Arial', 11, 'bold'),
                                     bg=self.colors['success'], 
                                     fg=self.colors['white'],
                                     activebackground='#059669',
                                     activeforeground=self.colors['white'],
                                     command=self.start_automation, 
                                     padx=30,
                                     pady=12,
                                     relief='flat',
                                     cursor='hand2')
        self.start_button.pack(side='left', padx=(0, 10))
        
        # Botão Parar
        self.stop_button = tk.Button(button_container, 
                                    text="⏸️ PARAR", 
                                    font=('Arial', 11, 'bold'),
                                    bg=self.colors['danger'], 
                                    fg=self.colors['white'],
                                    activebackground='#dc2626',
                                    activeforeground=self.colors['white'],
                                    command=self.stop_automation, 
                                    padx=30,
                                    pady=12,
                                    relief='flat',
                                    cursor='hand2',
                                    state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10))
        
        # Status geral
        status_container = tk.Frame(button_container, bg=self.colors['white'],
                                   relief='flat', bd=0)
        status_container.pack(side='right', padx=10)
        
        status_inner = tk.Frame(status_container, bg=self.colors['white'])
        status_inner.pack(padx=15, pady=10)
        
        self.general_status = tk.Label(status_inner, 
                                      text="✓ Sistema Pronto", 
                                      font=('Arial', 11, 'bold'), 
                                      bg=self.colors['white'],
                                      fg=self.colors['success'])
        self.general_status.pack()
    
    def create_automation_tab_dia16(self):
        """Aba de automação para Dia 16"""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text='🚀 Lances Dia 16')
        
        # Status cards
        status_frame = tk.LabelFrame(tab_frame, text="Status", font=('Arial', 12, 'bold'))
        status_frame.pack(fill='x', padx=10, pady=5)
        
        cards_container = tk.Frame(status_frame)
        cards_container.pack(fill='x', padx=5, pady=5)
        
        # Cards de status
        self.status_cards_dia16 = {}
        for i, (text, key) in enumerate([("Servopa", "servopa"), ("Todoist", "todoist"), ("Cliente", "cliente"), ("Lances", "lances")]):
            card = tk.Frame(cards_container, bg='white', relief='solid', bd=1, width=150, height=60)
            card.pack_propagate(False)
            card.grid(row=0, column=i, padx=3, pady=3, sticky='ew')
            
            tk.Label(card, text=text, font=('Arial', 9, 'bold'), bg='white').pack(pady=5)
            status_label = tk.Label(card, text="Aguardando", font=('Arial', 8), bg='white', fg='gray')
            status_label.pack()
            self.status_cards_dia16[key] = status_label
            
        for i in range(4):
            cards_container.grid_columnconfigure(i, weight=1)
        
        # Progresso
        progress_frame = tk.LabelFrame(tab_frame, text="Progresso", font=('Arial', 12, 'bold'))
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        self.progress_bar_dia16 = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar_dia16.pack(fill='x', padx=10, pady=5)
        
        self.progress_label_dia16 = tk.Label(progress_frame, text="Sistema pronto", font=('Arial', 10))
        self.progress_label_dia16.pack(pady=2)
        
        # Log
        log_frame = tk.LabelFrame(tab_frame, text="Log", font=('Arial', 12, 'bold'))
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text_dia16 = scrolledtext.ScrolledText(log_frame, height=15, font=('Consolas', 9),
                                                bg='#1e1e1e', fg='#d4d4d4', wrap=tk.WORD)
        self.log_text_dia16.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Botões
        button_frame = tk.Frame(tab_frame)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_button_dia16 = tk.Button(button_frame, text="🚀 Iniciar Lances Dia 16", font=('Arial', 10, 'bold'),
                                    bg='#28a745', fg='white', command=self.start_automation_dia16, padx=20)
        self.start_button_dia16.pack(side='left', padx=5)
        
        self.stop_button_dia16 = tk.Button(button_frame, text="⏸️ Parar", font=('Arial', 10, 'bold'),
                                   bg='#dc3545', fg='white', command=self.stop_automation_dia16, padx=20, state='disabled')
        self.stop_button_dia16.pack(side='left', padx=5)
        
        self.general_status_dia16 = tk.Label(button_frame, text="Sistema pronto", font=('Arial', 10, 'bold'), fg='#28a745')
        self.general_status_dia16.pack(side='right', padx=10)
    
    def create_boletos_tab(self):
        """Aba de Boletos - Kanban com 2 colunas (Dia 8 e Dia 16)"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(tab_frame, text='📄 Boletos')
        
        # Container principal com padding
        main_container = tk.Frame(tab_frame, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ========== HEADER ==========
        header_border = tk.Frame(main_container, bg=self.colors['border'])
        header_border.pack(fill='x', pady=(0, 15))
        header_inner = tk.Frame(header_border, bg=self.colors['white'])
        header_inner.pack(padx=1, pady=1, fill='x')
        
        header_content = tk.Frame(header_inner, bg=self.colors['white'])
        header_content.pack(fill='x', padx=20, pady=15)
        
        tk.Label(header_content, text="📄 Kanban de Boletos Servopa Outubro", 
                font=('Arial', 16, 'bold'), bg=self.colors['white'], fg=self.colors['primary']).pack(anchor='w')
        tk.Label(header_content, 
                text="Visualização sincronizada com o Todoist - Duas colunas: Vencimento dia 08 e Vencimento dia 16",
                font=('Arial', 10), bg=self.colors['white'], fg=self.colors['text_light']).pack(anchor='w', pady=(5, 0))
        
        # ========== BOTÃO DE IMPORTAÇÃO ==========
        import_frame = tk.Frame(main_container, bg=self.colors['light'])
        import_frame.pack(fill='x', pady=(0, 15))
        
        tk.Button(import_frame, text="🔄 Importar do Todoist", font=('Arial', 11, 'bold'),
                 bg=self.colors['success'], fg='white', command=self.import_boletos_from_todoist,
                 padx=30, pady=10, relief='flat', cursor='hand2').pack(side='left')
        
        self.boletos_status_label = tk.Label(import_frame, text="Clique em Importar para sincronizar", 
                                             font=('Arial', 10), bg=self.colors['light'], fg=self.colors['text_light'])
        self.boletos_status_label.pack(side='left', padx=15)
        
        # ========== KANBAN DE 2 COLUNAS ==========
        kanban_container = tk.Frame(main_container, bg=self.colors['light'])
        kanban_container.pack(fill='both', expand=True)
        
        # COLUNA DIA 08
        dia08_border = tk.Frame(kanban_container, bg=self.colors['border'])
        dia08_border.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        dia08_frame = tk.Frame(dia08_border, bg=self.colors['white'])
        dia08_frame.pack(padx=1, pady=1, fill='both', expand=True)
        
        # Header Dia 08
        dia08_header = tk.Frame(dia08_frame, bg=self.colors['secondary'], height=50)
        dia08_header.pack(fill='x')
        dia08_header.pack_propagate(False)
        
        tk.Label(dia08_header, text="📅 Vencimento dia 08", font=('Arial', 14, 'bold'), 
                bg=self.colors['secondary'], fg='white').pack(pady=12)
        
        # Container scrollável para cards Dia 08
        dia08_canvas_frame = tk.Frame(dia08_frame, bg=self.colors['white'])
        dia08_canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        dia08_canvas = tk.Canvas(dia08_canvas_frame, bg=self.colors['white'], highlightthickness=0)
        dia08_scrollbar = ttk.Scrollbar(dia08_canvas_frame, orient="vertical", command=dia08_canvas.yview)
        
        self.dia08_cards_container = tk.Frame(dia08_canvas, bg=self.colors['white'])
        self.dia08_cards_container.bind(
            "<Configure>",
            lambda e: dia08_canvas.configure(scrollregion=dia08_canvas.bbox("all"))
        )
        
        dia08_canvas.create_window((0, 0), window=self.dia08_cards_container, anchor="nw")
        dia08_canvas.configure(yscrollcommand=dia08_scrollbar.set)
        
        dia08_canvas.pack(side="left", fill="both", expand=True)
        dia08_scrollbar.pack(side="right", fill="y")
        
        # COLUNA DIA 16
        dia16_border = tk.Frame(kanban_container, bg=self.colors['border'])
        dia16_border.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        dia16_frame = tk.Frame(dia16_border, bg=self.colors['white'])
        dia16_frame.pack(padx=1, pady=1, fill='both', expand=True)
        
        # Header Dia 16
        dia16_header = tk.Frame(dia16_frame, bg=self.colors['warning'], height=50)
        dia16_header.pack(fill='x')
        dia16_header.pack_propagate(False)
        
        tk.Label(dia16_header, text="📅 Vencimento dia 16", font=('Arial', 14, 'bold'), 
                bg=self.colors['warning'], fg='white').pack(pady=12)
        
        # Container scrollável para cards Dia 16
        dia16_canvas_frame = tk.Frame(dia16_frame, bg=self.colors['white'])
        dia16_canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        dia16_canvas = tk.Canvas(dia16_canvas_frame, bg=self.colors['white'], highlightthickness=0)
        dia16_scrollbar = ttk.Scrollbar(dia16_canvas_frame, orient="vertical", command=dia16_canvas.yview)
        
        self.dia16_cards_container = tk.Frame(dia16_canvas, bg=self.colors['white'])
        self.dia16_cards_container.bind(
            "<Configure>",
            lambda e: dia16_canvas.configure(scrollregion=dia16_canvas.bbox("all"))
        )
        
        dia16_canvas.create_window((0, 0), window=self.dia16_cards_container, anchor="nw")
        dia16_canvas.configure(yscrollcommand=dia16_scrollbar.set)
        
        dia16_canvas.pack(side="left", fill="both", expand=True)
        dia16_scrollbar.pack(side="right", fill="y")
        
        # Carregar dados salvos se existirem
        self.load_boletos_data()
        
    def import_boletos_from_todoist(self):
        """Importa dados do board de Boletos do Todoist"""
        self.boletos_status_label.config(text="⏳ Importando do Todoist...", fg=self.colors['warning'])
        
        def import_thread():
            try:
                from auth.servopa_auth import create_driver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from utils.todoist_board_extractor import navigate_to_board_project_boletos, extract_boletos_board
                import time
                
                # Carrega credenciais
                credentials = {
                    'todoist': {
                        'usuario': self.todoist_login_var.get().strip(),
                        'senha': self.todoist_senha_var.get().strip()
                    }
                }
                
                if not credentials['todoist']['usuario'] or not credentials['todoist']['senha']:
                    raise Exception("Credenciais do Todoist não informadas")
                
                # Cria driver
                driver = create_driver(headless=False)
                
                try:
                    # Login Todoist
                    driver.get("https://todoist.com/auth/login")
                    time.sleep(3)
                    
                    wait = WebDriverWait(driver, 20)
                    
                    email_input = wait.until(EC.presence_of_element_located((By.ID, "element-0")))
                    email_input.send_keys(credentials['todoist']['usuario'])
                    
                    password_input = wait.until(EC.presence_of_element_located((By.ID, "element-2")))
                    password_input.send_keys(credentials['todoist']['senha'])
                    
                    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
                    login_button.click()
                    time.sleep(10)
                    
                    # Navega para board de Boletos
                    def progress_callback(msg):
                        self.root.after(0, lambda: self.boletos_status_label.config(text=msg, fg=self.colors['primary']))
                    
                    if not navigate_to_board_project_boletos(driver, progress_callback):
                        raise Exception("Falha ao navegar para board de Boletos")
                    
                    # Extrai dados
                    boletos_data = extract_boletos_board(driver, progress_callback)
                    
                    if not boletos_data:
                        raise Exception("Falha ao extrair dados do board")
                    
                    # Salva dados
                    self.save_boletos_data(boletos_data)
                    
                    # Atualiza interface
                    self.root.after(0, lambda: self.display_boletos_cards(boletos_data))
                    
                    total_dia08 = len(boletos_data['dia08'])
                    total_dia16 = len(boletos_data['dia16'])
                    
                    self.root.after(0, lambda: self.boletos_status_label.config(
                        text=f"✅ Importado: {total_dia08} boletos (dia 08) e {total_dia16} boletos (dia 16)", 
                        fg=self.colors['success']))
                    
                finally:
                    driver.quit()
                    
            except Exception as e:
                self.root.after(0, lambda: self.boletos_status_label.config(
                    text=f"❌ Erro: {str(e)[:50]}", fg=self.colors['danger']))
        
        thread = threading.Thread(target=import_thread)
        thread.daemon = True
        thread.start()
    
    def display_boletos_cards(self, boletos_data):
        """Exibe cards de boletos no kanban"""
        # Limpa containers
        for widget in self.dia08_cards_container.winfo_children():
            widget.destroy()
        for widget in self.dia16_cards_container.winfo_children():
            widget.destroy()
        
        # Cria cards para Dia 08
        for idx, boleto in enumerate(boletos_data['dia08']):
            self.create_boleto_card(self.dia08_cards_container, boleto, idx)
        
        # Cria cards para Dia 16
        for idx, boleto in enumerate(boletos_data['dia16']):
            self.create_boleto_card(self.dia16_cards_container, boleto, idx)
    
    def create_boleto_card(self, parent, boleto, index):
        """Cria um card de boleto"""
        # Card container com borda
        card_border = tk.Frame(parent, bg=self.colors['border'])
        card_border.pack(fill='x', pady=5)
        
        card = tk.Frame(card_border, bg=self.colors['white'])
        card.pack(padx=1, pady=1, fill='x')
        
        # Cor de destaque no topo
        color = self.colors['success'] if boleto.get('is_completed') else self.colors['secondary']
        color_bar = tk.Frame(card, bg=color, height=3)
        color_bar.pack(fill='x')
        
        # Conteúdo do card
        content = tk.Frame(card, bg=self.colors['white'])
        content.pack(fill='x', padx=12, pady=10)
        
        # Nome do cliente
        tk.Label(content, text=boleto['nome'], font=('Arial', 11, 'bold'), 
                bg=self.colors['white'], fg=self.colors['dark'], anchor='w').pack(fill='x')
        
        # Informação de cotas
        if boleto.get('cotas'):
            tk.Label(content, text=boleto['cotas'], font=('Arial', 9), 
                    bg=self.colors['white'], fg=self.colors['text_light'], anchor='w').pack(fill='x', pady=(5, 0))
        
        # Status
        status_text = "✅ Concluído" if boleto.get('is_completed') else "⬜ Pendente"
        status_color = self.colors['success'] if boleto.get('is_completed') else self.colors['text_light']
        tk.Label(content, text=status_text, font=('Arial', 8), 
                bg=self.colors['white'], fg=status_color, anchor='w').pack(fill='x', pady=(3, 0))
    
    def save_boletos_data(self, boletos_data):
        """Salva dados dos boletos em arquivo JSON"""
        import json
        boletos_file = 'boletos_data.json'
        
        # Remove elementos não serializáveis
        clean_data = {
            'dia08': [],
            'dia16': [],
            'last_import': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for boleto in boletos_data['dia08']:
            clean_data['dia08'].append({
                'nome': boleto['nome'],
                'cotas': boleto.get('cotas', ''),
                'is_completed': boleto.get('is_completed', False)
            })
        
        for boleto in boletos_data['dia16']:
            clean_data['dia16'].append({
                'nome': boleto['nome'],
                'cotas': boleto.get('cotas', ''),
                'is_completed': boleto.get('is_completed', False)
            })
        
        with open(boletos_file, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
    
    def load_boletos_data(self):
        """Carrega dados salvos dos boletos"""
        import json
        import os
        boletos_file = 'boletos_data.json'
        
        if os.path.exists(boletos_file):
            try:
                with open(boletos_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.display_boletos_cards(data)
                
                total_dia08 = len(data.get('dia08', []))
                total_dia16 = len(data.get('dia16', []))
                last_import = data.get('last_import', 'Desconhecida')
                
                self.boletos_status_label.config(
                    text=f"📊 Dados carregados: {total_dia08} boletos (dia 08), {total_dia16} boletos (dia 16) | Última importação: {last_import}", 
                    fg=self.colors['primary'])
            except Exception as e:
                self.boletos_status_label.config(text=f"⚠️ Erro ao carregar dados: {e}", fg=self.colors['warning'])
        
    def create_credentials_tab(self):
        """Aba de credenciais"""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text='🔐 Credenciais')
        
        container = tk.Frame(tab_frame)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Servopa
        servopa_frame = tk.LabelFrame(container, text="Servopa", font=('Arial', 12, 'bold'))
        servopa_frame.pack(fill='x', pady=10)
        
        servopa_content = tk.Frame(servopa_frame)
        servopa_content.pack(fill='x', padx=15, pady=10)
        
        tk.Label(servopa_content, text="Usuário:", font=('Arial', 10, 'bold')).pack(anchor='w')
        tk.Entry(servopa_content, font=('Arial', 10), width=50, textvariable=self.servopa_login_var).pack(fill='x', pady=(2, 8))
        
        tk.Label(servopa_content, text="Senha:", font=('Arial', 10, 'bold')).pack(anchor='w')
        tk.Entry(servopa_content, font=('Arial', 10), width=50, show='*', textvariable=self.servopa_senha_var).pack(fill='x', pady=2)
        
        # Todoist
        todoist_frame = tk.LabelFrame(container, text="Todoist", font=('Arial', 12, 'bold'))
        todoist_frame.pack(fill='x', pady=10)
        
        todoist_content = tk.Frame(todoist_frame)
        todoist_content.pack(fill='x', padx=15, pady=10)
        
        tk.Label(todoist_content, text="Usuário:", font=('Arial', 10, 'bold')).pack(anchor='w')
        tk.Entry(todoist_content, font=('Arial', 10), width=50, textvariable=self.todoist_login_var).pack(fill='x', pady=(2, 8))
        
        tk.Label(todoist_content, text="Senha:", font=('Arial', 10, 'bold')).pack(anchor='w')
        tk.Entry(todoist_content, font=('Arial', 10), width=50, show='*', textvariable=self.todoist_senha_var).pack(fill='x', pady=2)
        
        # Botões de ação
        actions_frame = tk.Frame(container)
        actions_frame.pack(fill='x', pady=20)
        
        tk.Button(actions_frame, text="💾 Salvar", font=('Arial', 10, 'bold'),
                 bg='#28a745', fg='white', command=self.save_credentials, padx=20).pack(side='left', padx=5)
        
        tk.Button(actions_frame, text="🔄 Recarregar", font=('Arial', 10, 'bold'),
                 bg='#007bff', fg='white', command=self.load_credentials, padx=20).pack(side='left', padx=5)
        
        self.creds_status = tk.Label(actions_frame, text="", font=('Arial', 10))
        self.creds_status.pack(side='right')
        
    def load_credentials(self):
        """Carrega credenciais"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'servopa' in data:
                    self.servopa_login_var.set(data['servopa'].get('usuario', ''))
                    self.servopa_senha_var.set(data['servopa'].get('senha', ''))
                    
                if 'todoist' in data:
                    self.todoist_login_var.set(data['todoist'].get('usuario', ''))
                    self.todoist_senha_var.set(data['todoist'].get('senha', ''))
                
                self.creds_status.config(text="✅ Carregado", fg='green')
        except Exception as e:
            self.creds_status.config(text=f"❌ Erro: {str(e)[:30]}", fg='red')
            
    def save_credentials(self):
        """Salva credenciais"""
        try:
            data = {
                'servopa': {'usuario': self.servopa_login_var.get(), 'senha': self.servopa_senha_var.get()},
                'todoist': {'usuario': self.todoist_login_var.get(), 'senha': self.todoist_senha_var.get()}
            }
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.creds_status.config(text="✅ Salvo", fg='green')
            self.root.after(2000, lambda: self.creds_status.config(text=""))
        except Exception as e:
            self.creds_status.config(text=f"❌ Erro: {str(e)[:30]}", fg='red')
    

    def create_whatsapp_tab(self):
        """Aba unificada de envio de mensagens WhatsApp - Dia 8 e Dia 16"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['light'])
        self.notebook.add(tab_frame, text='📱 WhatsApp')
        
        # Inicializa variáveis compartilhadas (apenas uma vez)
        if not hasattr(self, 'evolution_config_file'):
            self.evolution_config_file = 'evolution_config.json'
            self.evo_api_url_var = tk.StringVar(value="https://zap.tekvosoft.com")
            self.evo_instance_var = tk.StringVar(value="david -tekvo")
            self.evo_api_key_var = tk.StringVar(value="634A7E882CE5-4314-8C5B-BC79C0A9EBBA")
        
        # Container principal com scroll
        main_container = tk.Frame(tab_frame, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ========== TÍTULO E DESCRIÇÃO ==========
        header_border = tk.Frame(main_container, bg=self.colors['border'])
        header_border.pack(fill='x', pady=(0, 10))
        header_inner = tk.Frame(header_border, bg=self.colors['white'])
        header_inner.pack(padx=1, pady=1, fill='x')
        
        header_content = tk.Frame(header_inner, bg=self.colors['white'])
        header_content.pack(fill='x', padx=20, pady=15)
        
        tk.Label(header_content, text="📱 Disparo em Massa via WhatsApp", 
                font=('Arial', 16, 'bold'), bg=self.colors['white'], fg=self.colors['primary']).pack(anchor='w')
        tk.Label(header_content, 
                text="Configure os contatos e mensagens para envio automático nos dias 8 e 16 de cada mês",
                font=('Arial', 10), bg=self.colors['white'], fg=self.colors['text_light'], wraplength=900, justify='left').pack(anchor='w', pady=(5, 0))
        
        # ========== CONFIGURAÇÃO DA API (URL BLOQUEADA) ==========
        api_frame = tk.LabelFrame(main_container, text="🔧 Configuração da Evolution API (URL Bloqueada)", 
                                  font=('Arial', 12, 'bold'), bg=self.colors['light'])
        api_frame.pack(fill='x', pady=5)
        
        api_content = tk.Frame(api_frame, bg=self.colors['light'])
        api_content.pack(fill='x', padx=15, pady=10)
        
        # URL da API (BLOQUEADA - READ ONLY)
        tk.Label(api_content, text="URL da API:", font=('Arial', 10, 'bold'), bg=self.colors['light']).pack(anchor='w')
        url_entry = tk.Entry(api_content, font=('Arial', 10), width=60, textvariable=self.evo_api_url_var, 
                            state='readonly', readonlybackground='#f0f0f0', fg='#555555')
        url_entry.pack(fill='x', pady=(2, 8))
        
        # Nome da Instância
        tk.Label(api_content, text="Nome da Instância:", font=('Arial', 10, 'bold'), bg=self.colors['light']).pack(anchor='w')
        instance_entry = tk.Entry(api_content, font=('Arial', 10), width=60, textvariable=self.evo_instance_var)
        instance_entry.pack(fill='x', pady=(2, 8))
        
        # API Key
        tk.Label(api_content, text="API Key:", font=('Arial', 10, 'bold'), bg=self.colors['light']).pack(anchor='w')
        apikey_entry = tk.Entry(api_content, font=('Arial', 10), width=60, textvariable=self.evo_api_key_var)
        apikey_entry.pack(fill='x', pady=(2, 8))
        
        # Botão de teste
        test_button_frame = tk.Frame(api_content, bg=self.colors['light'])
        test_button_frame.pack(fill='x')
        
        tk.Button(test_button_frame, text="🧪 Testar Conexão", font=('Arial', 9, 'bold'),
                 bg='#007bff', fg='white', command=self.test_evolution_connection, padx=15, relief='flat', cursor='hand2').pack(side='left', padx=5)
        
        if not hasattr(self, 'evo_test_status'):
            self.evo_test_status = tk.Label(test_button_frame, text="", font=('Arial', 9), bg=self.colors['light'])
        self.evo_test_status.pack(side='left', padx=10)
        
        # ========== CONTAINER PARA GRUPOS DIA 8 E DIA 16 (LADO A LADO) ==========
        groups_container = tk.Frame(main_container, bg=self.colors['light'])
        groups_container.pack(fill='both', expand=True, pady=5)
        
        # ========== GRUPO DIA 8 ==========
        dia8_border = tk.Frame(groups_container, bg=self.colors['border'])
        dia8_border.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        dia8_frame = tk.Frame(dia8_border, bg=self.colors['white'])
        dia8_frame.pack(padx=1, pady=1, fill='both', expand=True)
        
        # Header Dia 8
        dia8_header = tk.Frame(dia8_frame, bg=self.colors['secondary'], height=40)
        dia8_header.pack(fill='x')
        dia8_header.pack_propagate(False)
        
        tk.Label(dia8_header, text="📅 GRUPO DIA 8", font=('Arial', 12, 'bold'), 
                bg=self.colors['secondary'], fg='white').pack(pady=10)
        
        dia8_content = tk.Frame(dia8_frame, bg=self.colors['white'])
        dia8_content.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Contatos Dia 8
        tk.Label(dia8_content, text="👥 Contatos (um por linha):", font=('Arial', 10, 'bold'), bg=self.colors['white']).pack(anchor='w')
        tk.Label(dia8_content, text="Formato: 5519995378302 - Nome Cliente", 
                font=('Arial', 8), fg='gray', bg=self.colors['white']).pack(anchor='w')
        
        self.contacts_text_dia8 = scrolledtext.ScrolledText(dia8_content, height=10, font=('Consolas', 9), wrap=tk.WORD)
        self.contacts_text_dia8.pack(fill='both', expand=True, pady=5)
        self.contacts_text_dia8.insert('1.0', "5519995378302 - Cliente Exemplo Dia 8")
        
        # Mensagem Dia 8
        tk.Label(dia8_content, text="💬 Mensagem do Dia 8:", font=('Arial', 10, 'bold'), bg=self.colors['white']).pack(anchor='w', pady=(10, 0))
        tk.Label(dia8_content, text="Use {nome} para personalizar", 
                font=('Arial', 8), fg='gray', bg=self.colors['white']).pack(anchor='w')
        
        self.message_text_dia8 = scrolledtext.ScrolledText(dia8_content, height=6, font=('Consolas', 9), wrap=tk.WORD)
        self.message_text_dia8.pack(fill='both', expand=True, pady=5)
        self.message_text_dia8.insert('1.0', "Olá {nome}! 🎉\n\nMensagem para envio no dia 8")
        
        # Botões Dia 8
        action_frame_dia8 = tk.Frame(dia8_content, bg=self.colors['white'])
        action_frame_dia8.pack(fill='x', pady=10)
        
        tk.Button(action_frame_dia8, text="📤 Enviar Agora", font=('Arial', 9, 'bold'),
                 bg='#28a745', fg='white', command=lambda: self.send_simple_messages('dia8'), padx=15, relief='flat', cursor='hand2').pack(side='left', padx=3)
        
        tk.Button(action_frame_dia8, text="🗑️ Limpar", font=('Arial', 8),
                 bg='#6c757d', fg='white', command=lambda: self.clear_simple_fields('dia8'), padx=10, relief='flat', cursor='hand2').pack(side='left', padx=3)
        
        self.send_status_dia8 = tk.Label(action_frame_dia8, text="", font=('Arial', 9), bg=self.colors['white'])
        self.send_status_dia8.pack(side='left', padx=10)
        
        # ========== GRUPO DIA 16 ==========
        dia16_border = tk.Frame(groups_container, bg=self.colors['border'])
        dia16_border.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        dia16_frame = tk.Frame(dia16_border, bg=self.colors['white'])
        dia16_frame.pack(padx=1, pady=1, fill='both', expand=True)
        
        # Header Dia 16
        dia16_header = tk.Frame(dia16_frame, bg=self.colors['warning'], height=40)
        dia16_header.pack(fill='x')
        dia16_header.pack_propagate(False)
        
        tk.Label(dia16_header, text="📅 GRUPO DIA 16", font=('Arial', 12, 'bold'), 
                bg=self.colors['warning'], fg='white').pack(pady=10)
        
        dia16_content = tk.Frame(dia16_frame, bg=self.colors['white'])
        dia16_content.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Contatos Dia 16
        tk.Label(dia16_content, text="👥 Contatos (um por linha):", font=('Arial', 10, 'bold'), bg=self.colors['white']).pack(anchor='w')
        tk.Label(dia16_content, text="Formato: 5519995378302 - Nome Cliente", 
                font=('Arial', 8), fg='gray', bg=self.colors['white']).pack(anchor='w')
        
        self.contacts_text_dia16 = scrolledtext.ScrolledText(dia16_content, height=10, font=('Consolas', 9), wrap=tk.WORD)
        self.contacts_text_dia16.pack(fill='both', expand=True, pady=5)
        self.contacts_text_dia16.insert('1.0', "5519995378302 - Cliente Exemplo Dia 16")
        
        # Mensagem Dia 16
        tk.Label(dia16_content, text="💬 Mensagem do Dia 16:", font=('Arial', 10, 'bold'), bg=self.colors['white']).pack(anchor='w', pady=(10, 0))
        tk.Label(dia16_content, text="Use {nome} para personalizar", 
                font=('Arial', 8), fg='gray', bg=self.colors['white']).pack(anchor='w')
        
        self.message_text_dia16 = scrolledtext.ScrolledText(dia16_content, height=6, font=('Consolas', 9), wrap=tk.WORD)
        self.message_text_dia16.pack(fill='both', expand=True, pady=5)
        self.message_text_dia16.insert('1.0', "Olá {nome}! 🎉\n\nMensagem para envio no dia 16")
        
        # Botões Dia 16
        action_frame_dia16 = tk.Frame(dia16_content, bg=self.colors['white'])
        action_frame_dia16.pack(fill='x', pady=10)
        
        tk.Button(action_frame_dia16, text="📤 Enviar Agora", font=('Arial', 9, 'bold'),
                 bg='#28a745', fg='white', command=lambda: self.send_simple_messages('dia16'), padx=15, relief='flat', cursor='hand2').pack(side='left', padx=3)
        
        tk.Button(action_frame_dia16, text="🗑️ Limpar", font=('Arial', 8),
                 bg='#6c757d', fg='white', command=lambda: self.clear_simple_fields('dia16'), padx=10, relief='flat', cursor='hand2').pack(side='left', padx=3)
        
        self.send_status_dia16 = tk.Label(action_frame_dia16, text="", font=('Arial', 9), bg=self.colors['white'])
        self.send_status_dia16.pack(side='left', padx=10)
        
        # ========== LOG DE ENVIO (COMPARTILHADO) ==========
        if not hasattr(self, 'message_log_text'):
            log_frame = tk.LabelFrame(main_container, text="📝 Log de Envio", font=('Arial', 12, 'bold'), bg=self.colors['light'])
            log_frame.pack(fill='both', expand=True, pady=10)
            
            self.message_log_text = scrolledtext.ScrolledText(log_frame, height=8, font=('Consolas', 9),
                                                              bg='#1e1e1e', fg='#d4d4d4', wrap=tk.WORD)
            self.message_log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Carrega configurações (apenas uma vez)
        if not hasattr(self, '_config_loaded'):
            self._config_loaded = True
            self.root.after(500, self.load_evolution_config)

    def load_evolution_config(self):
        """Carrega configurações da Evolution API"""
        try:
            if os.path.exists(self.evolution_config_file):
                with open(self.evolution_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'api' in data:
                    self.evo_api_url_var.set(data['api'].get('base_url', ''))
                    self.evo_instance_var.set(data['api'].get('instance_name', ''))
                    self.evo_api_key_var.set(data['api'].get('api_key', ''))
                
                self.add_message_log("✅ Configurações carregadas do arquivo")
        except Exception as e:
            self.add_message_log(f"⚠️ Erro ao carregar configurações: {e}")
    
    def save_evolution_config(self):
        """Salva configurações da Evolution API"""
        try:
            # Carrega config existente ou cria novo
            if os.path.exists(self.evolution_config_file):
                with open(self.evolution_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Atualiza seção API
            data['api'] = {
                'base_url': self.evo_api_url_var.get().strip(),
                'instance_name': self.evo_instance_var.get().strip(),
                'api_key': self.evo_api_key_var.get().strip()
            }
            
            with open(self.evolution_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.add_message_log(f"❌ Erro ao salvar configurações: {e}")
            return False
    
    def test_evolution_connection(self):
        """Testa conexão com a Evolution API"""
        self.evo_test_status.config(text="🔄 Testando...", fg='orange')
        
        def test_thread():
            try:
                from utils.evolution_api import EvolutionAPI
                
                api = EvolutionAPI(
                    self.evo_api_url_var.get().strip(),
                    self.evo_instance_var.get().strip(),
                    self.evo_api_key_var.get().strip()
                )
                
                success, message = api.test_connection()
                
                if success:
                    self.root.after(0, lambda: self.evo_test_status.config(
                        text="✅ Conexão OK", fg='green'))
                    self.root.after(0, lambda: self.add_message_log(f"✅ {message}"))
                    self.save_evolution_config()
                else:
                    self.root.after(0, lambda: self.evo_test_status.config(
                        text="❌ Falhou", fg='red'))
                    self.root.after(0, lambda: self.add_message_log(f"❌ {message}"))
            except Exception as e:
                self.root.after(0, lambda: self.evo_test_status.config(
                    text="❌ Erro", fg='red'))
                self.root.after(0, lambda: self.add_message_log(f"❌ Erro: {e}"))
        
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()
    
    def add_message_log(self, message):
        """Adiciona mensagem ao log de envio"""
        if hasattr(self, 'message_log_text'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.message_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.message_log_text.see(tk.END)
    
    def clear_simple_fields(self, dia):
        """Limpa campos de mensagem para dia específico"""
        if dia == 'dia8':
            self.contacts_text_dia8.delete('1.0', tk.END)
            self.message_text_dia8.delete('1.0', tk.END)
        elif dia == 'dia16':
            self.contacts_text_dia16.delete('1.0', tk.END)
            self.message_text_dia16.delete('1.0', tk.END)
        self.add_message_log(f"🗑️ Campos do {dia} limpos")
    
    def send_simple_messages(self, dia):
        """Envia mensagens para dia específico (8 ou 16)"""
        # Define qual status usar
        status_label = self.send_status_dia8 if dia == 'dia8' else self.send_status_dia16
        status_label.config(text="📤 Enviando...", fg='orange')
        
        def send_thread():
            try:
                from utils.evolution_api import EvolutionAPI, parse_contacts_from_text
                
                # Cria cliente API
                api = EvolutionAPI(
                    self.evo_api_url_var.get().strip(),
                    self.evo_instance_var.get().strip(),
                    self.evo_api_key_var.get().strip()
                )
                
                # Pega contatos e mensagem do dia correto
                if dia == 'dia8':
                    contacts_text = self.contacts_text_dia8.get('1.0', tk.END).strip()
                    message = self.message_text_dia8.get('1.0', tk.END).strip()
                else:  # dia16
                    contacts_text = self.contacts_text_dia16.get('1.0', tk.END).strip()
                    message = self.message_text_dia16.get('1.0', tk.END).strip()
                
                # Parse contatos
                contacts = parse_contacts_from_text(contacts_text)
                
                if not contacts:
                    self.root.after(0, lambda: status_label.config(
                        text="❌ Nenhum contato", fg='red'))
                    self.root.after(0, lambda: self.add_message_log("❌ Nenhum contato válido encontrado"))
                    return
                
                if not message:
                    self.root.after(0, lambda: status_label.config(
                        text="❌ Mensagem vazia", fg='red'))
                    self.root.after(0, lambda: self.add_message_log("❌ Mensagem não pode estar vazia"))
                    return
                
                # Envia mensagens
                self.root.after(0, lambda: self.add_message_log(
                    f"📤 Iniciando envio {dia.upper()} para {len(contacts)} contato(s)..."))
                
                results = api.send_bulk_messages(
                    contacts,
                    message,
                    delay_between_messages=2.0,
                    progress_callback=lambda msg: self.root.after(0, lambda m=msg: self.add_message_log(m))
                )
                
                # Atualiza status
                if results['failed'] == 0:
                    self.root.after(0, lambda: status_label.config(
                        text=f"✅ {results['success']} enviadas", fg='green'))
                else:
                    self.root.after(0, lambda: status_label.config(
                        text=f"⚠️ {results['success']}/{results['total']}", fg='orange'))
                
                # Salva config
                self.save_evolution_config()
                
            except Exception as e:
                self.root.after(0, lambda: status_label.config(
                    text="❌ Erro", fg='red'))
                self.root.after(0, lambda: self.add_message_log(f"❌ Erro ao enviar: {e}"))
        
        thread = threading.Thread(target=send_thread)
        thread.daemon = True
        thread.start()

    
    def create_history_tab(self):
        """Aba de histórico - Já feito do dia 8"""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text='📊 Já feito do dia 8')
        
        # Arquivo para salvar histórico
        self.history_file = 'history_dia8.json'
        self.history_data = []
        
        # Header com informações
        header_frame = tk.Frame(tab_frame, bg='#e9ecef', height=60)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📊 Registro de Lances Processados",
                font=('Arial', 14, 'bold'), bg='#e9ecef').pack(pady=5)
        
        info_container = tk.Frame(header_frame, bg='#e9ecef')
        info_container.pack(fill='x', padx=10)
        
        self.history_stats_label = tk.Label(info_container,
                                            text="Total: 0 | ✅ Sucesso: 0 | ❌ Erro: 0",
                                            font=('Arial', 10), bg='#e9ecef')
        self.history_stats_label.pack(side='left')
        
        # Botões de ação
        button_container = tk.Frame(tab_frame)
        button_container.pack(fill='x', padx=10, pady=5)
        
        tk.Button(button_container, text="🔄 Atualizar", font=('Arial', 9, 'bold'),
                 bg='#007bff', fg='white', command=self.refresh_history, padx=15).pack(side='left', padx=3)
        
        tk.Button(button_container, text="📥 Exportar Excel", font=('Arial', 9, 'bold'),
                 bg='#28a745', fg='white', command=self.export_to_excel, padx=15).pack(side='left', padx=3)
        
        tk.Button(button_container, text="🗑️ Limpar Histórico", font=('Arial', 9, 'bold'),
                 bg='#dc3545', fg='white', command=self.clear_history, padx=15).pack(side='left', padx=3)
        
        # Frame para a tabela com scrollbars
        table_frame = tk.Frame(tab_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')
        
        # Treeview (Tabela)
        columns = ('hora', 'grupo', 'cota', 'nome', 'valor_lance', 'protocolo', 'status', 'observacao')
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configura scrollbars
        vsb.config(command=self.history_tree.yview)
        hsb.config(command=self.history_tree.xview)
        
        # Define cabeçalhos e larguras
        headers = {
            'hora': ('Hora', 80),
            'grupo': ('Grupo', 80),
            'cota': ('Cota', 80),
            'nome': ('Nome Cliente', 200),
            'valor_lance': ('Valor Lance', 100),
            'protocolo': ('Protocolo', 120),
            'status': ('Status', 100),
            'observacao': ('Observação', 250)
        }
        
        for col, (header, width) in headers.items():
            self.history_tree.heading(col, text=header, command=lambda c=col: self.sort_history_column(c))
            self.history_tree.column(col, width=width, anchor='center' if col != 'nome' and col != 'observacao' else 'w')
        
        self.history_tree.pack(fill='both', expand=True)
        
        # Estilo zebrado e por status
        self.history_tree.tag_configure('success', background='#d4edda')  # Verde claro para sucesso
        self.history_tree.tag_configure('error', background='#f8d7da')    # Vermelho claro para erro
        self.history_tree.tag_configure('stopped', background='#fff3cd')  # Laranja claro para parado
        self.history_tree.tag_configure('odd', background='#f8f9fa')
        self.history_tree.tag_configure('even', background='white')
        
        # Carrega histórico existente
        self.load_history()
    
    def create_history_tab_dia16(self):
        """Aba de histórico - Já feito do dia 16"""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text='📊 Já feito do dia 16')
        
        # Arquivo para salvar histórico
        self.history_file_dia16 = 'history_dia16.json'
        self.history_data_dia16 = []
        
        # Header com informações
        header_frame = tk.Frame(tab_frame, bg='#e9ecef', height=60)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📊 Registro de Lances Processados - Dia 16",
                font=('Arial', 14, 'bold'), bg='#e9ecef').pack(pady=5)
        
        info_container = tk.Frame(header_frame, bg='#e9ecef')
        info_container.pack(fill='x', padx=10)
        
        self.history_stats_label_dia16 = tk.Label(info_container,
                                            text="Total: 0 | ✅ Sucesso: 0 | ❌ Erro: 0",
                                            font=('Arial', 10), bg='#e9ecef')
        self.history_stats_label_dia16.pack(side='left')
        
        # Botões de ação
        button_container = tk.Frame(tab_frame)
        button_container.pack(fill='x', padx=10, pady=5)
        
        tk.Button(button_container, text="🔄 Atualizar", font=('Arial', 9, 'bold'),
                 bg='#007bff', fg='white', command=self.refresh_history_dia16, padx=15).pack(side='left', padx=3)
        
        tk.Button(button_container, text="📥 Exportar Excel", font=('Arial', 9, 'bold'),
                 bg='#28a745', fg='white', command=self.export_to_excel_dia16, padx=15).pack(side='left', padx=3)
        
        tk.Button(button_container, text="🗑️ Limpar Histórico", font=('Arial', 9, 'bold'),
                 bg='#dc3545', fg='white', command=self.clear_history_dia16, padx=15).pack(side='left', padx=3)
        
        # Frame para a tabela com scrollbars
        table_frame = tk.Frame(tab_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')
        
        # Treeview (Tabela)
        columns = ('hora', 'grupo', 'cota', 'nome', 'valor_lance', 'protocolo', 'status', 'observacao')
        self.history_tree_dia16 = ttk.Treeview(table_frame, columns=columns, show='headings',
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configura scrollbars
        vsb.config(command=self.history_tree_dia16.yview)
        hsb.config(command=self.history_tree_dia16.xview)
        
        # Define cabeçalhos e larguras
        headers = {
            'hora': ('Hora', 80),
            'grupo': ('Grupo', 80),
            'cota': ('Cota', 80),
            'nome': ('Nome Cliente', 200),
            'valor_lance': ('Valor Lance', 100),
            'protocolo': ('Protocolo', 120),
            'status': ('Status', 100),
            'observacao': ('Observação', 250)
        }
        
        for col, (header, width) in headers.items():
            self.history_tree_dia16.heading(col, text=header, command=lambda c=col: self.sort_history_column_dia16(c))
            self.history_tree_dia16.column(col, width=width, anchor='center' if col != 'nome' and col != 'observacao' else 'w')
        
        self.history_tree_dia16.pack(fill='both', expand=True)
        
        # Estilo zebrado e por status
        self.history_tree_dia16.tag_configure('success', background='#d4edda')
        self.history_tree_dia16.tag_configure('error', background='#f8d7da')
        self.history_tree_dia16.tag_configure('stopped', background='#fff3cd')
        self.history_tree_dia16.tag_configure('odd', background='#f8f9fa')
        self.history_tree_dia16.tag_configure('even', background='white')
        
        # Carrega histórico existente
        self.load_history_dia16()
    
    def load_history(self):
        """Carrega histórico do arquivo JSON"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
                print(f"✅ Histórico carregado: {len(self.history_data)} registros")
            else:
                self.history_data = []
                print(f"⚠️ Arquivo de histórico não existe: {self.history_file}")
            
            self.refresh_history()
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar histórico: {e}")
            self.history_data = []
    
    def save_history(self):
        """Salva histórico no arquivo JSON"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def add_history_entry(self, grupo, cota, nome, valor_lance, status, observacao="", protocolo=None, documento_url=None, **_extra):
        """Adiciona entrada ao histórico"""
        entry = {
            'hora': datetime.now().strftime('%H:%M:%S'),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'grupo': str(grupo),
            'cota': str(cota),
            'nome': nome,
            'valor_lance': valor_lance,
            'status': status,
            'observacao': observacao,
            'protocolo': protocolo or "",
            'documento_url': documento_url,
        }
        
        self.history_data.append(entry)
        self.save_history()
        
        # Atualiza a tabela na interface (thread-safe)
        self.root.after(0, self.refresh_history)
    
    def refresh_history(self):
        """Atualiza a exibição da tabela de histórico"""
        try:
            # Limpa tabela
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Adiciona dados
            success_count = 0
            error_count = 0
            stopped_count = 0
            
            print(f"📊 Atualizando histórico com {len(self.history_data)} registros...")
            
            for idx, entry in enumerate(reversed(self.history_data)):  # Mais recentes primeiro
                hora = entry.get('hora', '')
                grupo = entry.get('grupo', '')
                cota = entry.get('cota', '')
                nome = entry.get('nome', '')
                valor_lance = entry.get('valor_lance', '')
                protocolo = entry.get('protocolo', '')
                status = entry.get('status', '')
                observacao = entry.get('observacao', '')
                
                # Determina cor baseado no status
                if '⏹️' in status or 'parado' in status.lower():
                    stopped_count += 1
                    tag = 'stopped'  # Laranja para parado
                elif 'sucesso' in status.lower() or '✅' in status:
                    success_count += 1
                    tag = 'success'  # Verde para sucesso
                elif 'erro' in status.lower() or '❌' in status or 'falha' in status.lower():
                    error_count += 1
                    tag = 'error'  # Vermelho para erro
                else:
                    tag = 'odd' if idx % 2 else 'even'
                
                self.history_tree.insert('', 'end', values=(hora, grupo, cota, nome, valor_lance, protocolo, status, observacao),
                                        tags=(tag,))
            
            # Atualiza estatísticas
            total = len(self.history_data)
            stats_text = f"Total: {total} | ✅ Sucesso: {success_count}"
            if stopped_count > 0:
                stats_text += f" | ⏹️ Parado: {stopped_count}"
            stats_text += f" | ❌ Erro: {error_count}"
            
            self.history_stats_label.config(text=stats_text)
            print(f"✅ Histórico atualizado: {stats_text}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar histórico: {e}")
            import traceback
            traceback.print_exc()
    
    def sort_history_column(self, col):
        """Ordena tabela por coluna"""
        items = [(self.history_tree.set(item, col), item) for item in self.history_tree.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.history_tree.move(item, '', index)
    
    def export_to_excel(self):
        """Exporta histórico para Excel/CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            if not self.history_data:
                messagebox.showwarning("Aviso", "Não há dados para exportar!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"historico_dia8_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            'data',
                            'hora',
                            'grupo',
                            'cota',
                            'nome',
                            'valor_lance',
                            'protocolo',
                            'documento_url',
                            'status',
                            'observacao',
                        ],
                    )
                    writer.writeheader()
                    writer.writerows(self.history_data)
                
                messagebox.showinfo("Sucesso", f"Dados exportados para:\n{filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")
    
    def clear_history(self):
        """Limpa todo o histórico"""
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar TODO o histórico?\n\nEsta ação não pode ser desfeita!"):
            self.history_data = []
            self.save_history()
            self.refresh_history()
            messagebox.showinfo("Sucesso", "Histórico limpo com sucesso!")
    
    # ========== MÉTODOS PARA DIA 16 ==========
    
    def load_history_dia16(self):
        """Carrega histórico do Dia 16 do arquivo JSON"""
        try:
            if os.path.exists(self.history_file_dia16):
                with open(self.history_file_dia16, 'r', encoding='utf-8') as f:
                    self.history_data_dia16 = json.load(f)
                print(f"✅ Histórico Dia 16 carregado: {len(self.history_data_dia16)} registros")
            else:
                self.history_data_dia16 = []
                print(f"⚠️ Arquivo de histórico Dia 16 não existe: {self.history_file_dia16}")
            
            self.refresh_history_dia16()
        except Exception as e:
            print(f"❌ Erro ao carregar histórico Dia 16: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar histórico Dia 16: {e}")
            self.history_data_dia16 = []
    
    def save_history_dia16(self):
        """Salva histórico do Dia 16 no arquivo JSON"""
        try:
            with open(self.history_file_dia16, 'w', encoding='utf-8') as f:
                json.dump(self.history_data_dia16, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico Dia 16: {e}")
    
    def add_history_entry_dia16(self, grupo, cota, nome, valor_lance, status, observacao="", protocolo=None, documento_url=None, **_extra):
        """Adiciona entrada ao histórico do Dia 16"""
        entry = {
            'hora': datetime.now().strftime('%H:%M:%S'),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'grupo': str(grupo),
            'cota': str(cota),
            'nome': nome,
            'valor_lance': valor_lance,
            'status': status,
            'observacao': observacao,
            'protocolo': protocolo or "",
            'documento_url': documento_url,
        }
        
        self.history_data_dia16.append(entry)
        self.save_history_dia16()
        
        # Atualiza a tabela na interface (thread-safe)
        self.root.after(0, self.refresh_history_dia16)
    
    def refresh_history_dia16(self):
        """Atualiza a exibição da tabela de histórico do Dia 16"""
        try:
            # Limpa tabela
            for item in self.history_tree_dia16.get_children():
                self.history_tree_dia16.delete(item)
            
            # Adiciona dados
            success_count = 0
            error_count = 0
            stopped_count = 0
            
            print(f"📊 Atualizando histórico Dia 16 com {len(self.history_data_dia16)} registros...")
            
            for idx, entry in enumerate(reversed(self.history_data_dia16)):
                hora = entry.get('hora', '')
                grupo = entry.get('grupo', '')
                cota = entry.get('cota', '')
                nome = entry.get('nome', '')
                valor_lance = entry.get('valor_lance', '')
                protocolo = entry.get('protocolo', '')
                status = entry.get('status', '')
                observacao = entry.get('observacao', '')
                
                # Determina cor baseado no status
                if '⏹️' in status or 'parado' in status.lower():
                    stopped_count += 1
                    tag = 'stopped'
                elif 'sucesso' in status.lower() or '✅' in status:
                    success_count += 1
                    tag = 'success'
                elif 'erro' in status.lower() or '❌' in status or 'falha' in status.lower():
                    error_count += 1
                    tag = 'error'
                else:
                    tag = 'odd' if idx % 2 else 'even'
                
                self.history_tree_dia16.insert('', 'end', values=(hora, grupo, cota, nome, valor_lance, protocolo, status, observacao),
                                        tags=(tag,))
            
            # Atualiza estatísticas
            total = len(self.history_data_dia16)
            stats_text = f"Total: {total} | ✅ Sucesso: {success_count}"
            if stopped_count > 0:
                stats_text += f" | ⏹️ Parado: {stopped_count}"
            stats_text += f" | ❌ Erro: {error_count}"
            
            self.history_stats_label_dia16.config(text=stats_text)
            print(f"✅ Histórico Dia 16 atualizado: {stats_text}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar histórico Dia 16: {e}")
            import traceback
            traceback.print_exc()
    
    def sort_history_column_dia16(self, col):
        """Ordena tabela por coluna - Dia 16"""
        items = [(self.history_tree_dia16.set(item, col), item) for item in self.history_tree_dia16.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.history_tree_dia16.move(item, '', index)
    
    def export_to_excel_dia16(self):
        """Exporta histórico do Dia 16 para Excel/CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            if not self.history_data_dia16:
                messagebox.showwarning("Aviso", "Não há dados para exportar!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"historico_dia16_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            'data',
                            'hora',
                            'grupo',
                            'cota',
                            'nome',
                            'valor_lance',
                            'protocolo',
                            'documento_url',
                            'status',
                            'observacao',
                        ],
                    )
                    writer.writeheader()
                    writer.writerows(self.history_data_dia16)
                
                messagebox.showinfo("Sucesso", f"Dados exportados para:\n{filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")
    
    def clear_history_dia16(self):
        """Limpa todo o histórico do Dia 16"""
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar TODO o histórico do Dia 16?\n\nEsta ação não pode ser desfeita!"):
            self.history_data_dia16 = []
            self.save_history_dia16()
            self.refresh_history_dia16()
            messagebox.showinfo("Sucesso", "Histórico Dia 16 limpo com sucesso!")
    
    def setup_queue_processor(self):
        """Processa mensagens da queue"""
        def process():
            try:
                while True:
                    msg = self.message_queue.get_nowait()
                    self.handle_message(msg)
            except queue.Empty:
                pass
            finally:
                self.root.after(100, process)
        process()
        
    def handle_message(self, msg):
        """Processa mensagem"""
        if msg.get('type') == 'log':
            self.add_log_message(msg.get('content', ''))
        elif msg.get('type') == 'progress':
            self.update_progress(msg.get('value', 0), msg.get('content', ''))
        elif msg.get('type') == 'status':
            self.update_status(msg.get('component'), msg.get('status'))
    
    def add_log_message(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def update_progress(self, value, message=""):
        """Atualiza progresso"""
        self.progress_bar['value'] = value
        if message:
            self.progress_label.config(text=message)
        self.root.update_idletasks()
        
    def update_status(self, component, status):
        """Atualiza status"""
        if component in self.status_cards:
            self.status_cards[component].config(text=status)
    
    def progress_callback(self, message):
        """Callback para progresso"""
        self.message_queue.put({'type': 'log', 'content': message})
    
    def add_log_message_dia16(self, message):
        """Adiciona mensagem ao log do Dia 16"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text_dia16.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text_dia16.see(tk.END)
        
    def update_progress_dia16(self, value, message=""):
        """Atualiza progresso do Dia 16"""
        self.progress_bar_dia16['value'] = value
        if message:
            self.progress_label_dia16.config(text=message)
        self.root.update_idletasks()
        
    def update_status_dia16(self, component, status):
        """Atualiza status do Dia 16"""
        if component in self.status_cards_dia16:
            self.status_cards_dia16[component].config(text=status)
    
    def progress_callback_dia16(self, message):
        """Callback para progresso do Dia 16"""
        self.root.after(0, lambda: self.add_log_message_dia16(message))
        
    def start_automation(self):
        """Inicia automação"""
        self.automation_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.general_status.config(text="🚀 Executando...", fg='orange')
        
        self.automation_thread = threading.Thread(target=self.run_automation)
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def stop_automation(self):
        """Para automação e fecha navegador"""
        self.automation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.general_status.config(text="⏹️ Parando...", fg='red')
        self.add_log_message("⏹️ Solicitação de parada recebida")
        
        # Fecha o navegador se existir
        if self.driver:
            try:
                self.add_log_message("🔒 Fechando navegador...")
                self.driver.quit()
                self.driver = None
                self.add_log_message("✅ Navegador fechado com sucesso")
            except Exception as e:
                self.add_log_message(f"⚠️ Erro ao fechar navegador: {e}")
        
        self.general_status.config(text="⏹️ Parado", fg='gray')
    
    def start_automation_dia16(self):
        """Inicia automação do Dia 16"""
        self.automation_running_dia16 = True
        self.start_button_dia16.config(state='disabled')
        self.stop_button_dia16.config(state='normal')
        self.general_status_dia16.config(text="🚀 Executando...", fg='orange')
        
        self.automation_thread_dia16 = threading.Thread(target=self.run_automation_dia16)
        self.automation_thread_dia16.daemon = True
        self.automation_thread_dia16.start()
        
    def stop_automation_dia16(self):
        """Para automação do Dia 16 e fecha navegador"""
        self.automation_running_dia16 = False
        self.start_button_dia16.config(state='normal')
        self.stop_button_dia16.config(state='disabled')
        self.general_status_dia16.config(text="⏹️ Parando...", fg='red')
        self.add_log_message_dia16("⏹️ Solicitação de parada recebida")
        
        # Fecha o navegador se existir
        if self.driver_dia16:
            try:
                self.add_log_message_dia16("🔒 Fechando navegador...")
                self.driver_dia16.quit()
                self.driver_dia16 = None
                self.add_log_message_dia16("✅ Navegador fechado com sucesso")
            except Exception as e:
                self.add_log_message_dia16(f"⚠️ Erro ao fechar navegador: {e}")
        
        self.general_status_dia16.config(text="⏹️ Parado", fg='gray')
        
    def run_automation(self):
        """Executa automação completa com ciclo entre sites"""
        driver = None
        try:
            if not self.automation_running:
                return
                
            # Importa módulos
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from auth.servopa_auth import create_driver, login_servopa
            from auth.todoist_auth import login_todoist_and_extract
            from utils.todoist_board_extractor import navigate_to_board_project, extract_complete_board
            from automation.cycle_orchestrator import executar_ciclo_completo
            
            # Obtém credenciais
            credentials = {
                'servopa': {
                    'usuario': self.servopa_login_var.get().strip(),
                    'senha': self.servopa_senha_var.get().strip()
                },
                'todoist': {
                    'usuario': self.todoist_login_var.get().strip(),
                    'senha': self.todoist_senha_var.get().strip()
                }
            }
            
            # Valida credenciais
            if not credentials['servopa']['usuario'] or not credentials['servopa']['senha']:
                raise Exception("Credenciais do Servopa não informadas")
            if not credentials['todoist']['usuario'] or not credentials['todoist']['senha']:
                raise Exception("Credenciais do Todoist não informadas")
            
            # Log das credenciais (mascarando senha)
            self.progress_callback(f"🔐 Usando Servopa: {credentials['servopa']['usuario']}")
            self.progress_callback(f"🔐 Usando Todoist: {credentials['todoist']['usuario']}")
            
            self.progress_callback("🚀 Iniciando sistema de automação completo...")
            self.update_progress(5, "Iniciando navegador...")
            
            if not self.automation_running:
                return
            
            driver = create_driver()
            self.driver = driver  # Armazena referência global
            
            try:
                # ========== ETAPA 1: LOGIN SERVOPA ==========
                if not self.automation_running:
                    return
                    
                self.progress_callback("=" * 60)
                self.progress_callback("ETAPA 1: LOGIN NO SERVOPA")
                self.progress_callback("=" * 60)
                
                self.update_progress(10, "Fazendo login no Servopa...")
                self.update_status('servopa', '⏳ Login')
                
                if login_servopa(driver, self.progress_callback, credentials['servopa']):
                    self.update_status('servopa', '✅ Conectado')
                    self.update_progress(20, "Servopa conectado")
                    self.progress_callback("✅ Login Servopa concluído!")
                else:
                    raise Exception("Falha no login Servopa")
                
                # ========== ETAPA 2: LOGIN TODOIST (NOVA ABA) ==========
                if not self.automation_running:
                    return
                
                self.progress_callback("")
                self.progress_callback("=" * 60)
                self.progress_callback("ETAPA 2: LOGIN NO TODOIST (NOVA ABA)")
                self.progress_callback("=" * 60)
                
                self.update_progress(30, "Abrindo Todoist em nova aba...")
                self.update_status('todoist', '⏳ Login')
                
                # Salva janela original do Servopa
                servopa_window = driver.current_window_handle
                
                # Abre nova aba para Todoist
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                
                # Faz login no Todoist
                from auth.todoist_auth import TODOIST_URL, TIMEOUT
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                driver.get(TODOIST_URL)
                time.sleep(3)
                
                wait = WebDriverWait(driver, TIMEOUT)
                
                # Login Todoist
                email_input = wait.until(EC.presence_of_element_located((By.ID, "element-0")))
                email_input.clear()
                for char in credentials['todoist']['usuario']:
                    email_input.send_keys(char)
                    time.sleep(0.05)
                
                time.sleep(1)
                
                password_input = wait.until(EC.presence_of_element_located((By.ID, "element-2")))
                password_input.clear()
                for char in credentials['todoist']['senha']:
                    password_input.send_keys(char)
                    time.sleep(0.05)
                
                time.sleep(1)
                
                login_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[type='submit']")
                ))
                login_button.click()
                
                self.progress_callback("⏳ Aguardando login processar...")
                time.sleep(10)
                
                self.update_status('todoist', '✅ Conectado')
                self.update_progress(40, "Todoist conectado")
                self.progress_callback("✅ Login Todoist concluído!")
                
                # ========== ETAPA 3: NAVEGAR PARA BOARD E EXTRAIR ==========
                if not self.automation_running:
                    return
                
                self.progress_callback("")
                self.progress_callback("=" * 60)
                self.progress_callback("ETAPA 3: EXTRAINDO BOARD DO TODOIST")
                self.progress_callback("=" * 60)
                
                self.update_progress(50, "Navegando para board...")
                
                # Navega para o projeto do board
                if not navigate_to_board_project(driver, self.progress_callback):
                    raise Exception("Falha ao navegar para o board")
                
                self.update_progress(60, "Extraindo dados do board...")
                
                # Extrai estrutura completa do board
                board_data = extract_complete_board(driver, self.progress_callback)
                
                if not board_data or not board_data['sections']:
                    raise Exception("Falha ao extrair dados do board ou board vazio")
                
                total_tasks = sum(len(s['tasks']) for s in board_data['sections'])
                
                self.update_status('todoist', '✅ Extraído')
                self.update_progress(70, f"Board extraído: {total_tasks} tarefas")
                self.progress_callback(f"✅ Board extraído: {len(board_data['sections'])} colunas, {total_tasks} tarefas")
                
                # ========== ETAPA 4: CICLO COMPLETO ==========
                if not self.automation_running:
                    return
                
                self.progress_callback("")
                self.progress_callback("=" * 60)
                self.progress_callback("ETAPA 4: EXECUTANDO CICLO COMPLETO")
                self.progress_callback("=" * 60)
                
                self.update_progress(75, "Iniciando ciclo de automação...")
                self.update_status('cliente', '⏳ Processando')
                self.update_status('lances', '⏳ Processando')
                
                # Executa ciclo completo com callback de histórico e função de verificação
                stats = executar_ciclo_completo(
                    driver, 
                    board_data, 
                    self.progress_callback, 
                    self.add_history_entry,
                    lambda: self.automation_running  # Função que verifica se deve continuar
                )
                
                if stats:
                    self.update_status('cliente', '✅ OK')
                    self.update_status('lances', '✅ OK')
                    
                    self.update_progress(100, "Ciclo concluído!")
                    self.progress_callback("")
                    self.progress_callback("🎉 AUTOMAÇÃO COMPLETA FINALIZADA!")
                    self.progress_callback(f"✅ {stats['completed']}/{stats['total_tasks']} tarefas concluídas")
                    self.progress_callback(f"❌ {stats['failed']} falhas")
                    self.general_status.config(text=f"✅ Concluído: {stats['completed']}/{stats['total_tasks']}", fg='green')
                else:
                    raise Exception("Falha no ciclo de automação")
                    
            finally:
                if self.automation_running:
                    self.progress_callback("")
                    self.progress_callback("🔒 Navegador mantido aberto para verificação")
                    self.progress_callback("   (Feche manualmente quando terminar)")
                else:
                    self.progress_callback("⏹️ Automação interrompida")
                    if self.driver:
                        try:
                            self.progress_callback("🔒 Fechando navegador...")
                            self.driver.quit()
                            self.driver = None
                            self.progress_callback("✅ Navegador fechado")
                        except Exception as e:
                            self.progress_callback(f"⚠️ Aviso ao fechar navegador: {e}")
                
        except Exception as e:
            self.progress_callback(f"❌ Erro crítico: {e}")
            self.general_status.config(text="❌ Erro", fg='red')
            if self.driver:
                try:
                    self.progress_callback("🔒 Fechando navegador devido ao erro...")
                    self.driver.quit()
                    self.driver = None
                    self.progress_callback("✅ Navegador fechado")
                except Exception as cleanup_error:
                    self.progress_callback(f"⚠️ Aviso ao fechar navegador: {cleanup_error}")
        finally:
            self.automation_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
    
    def run_automation_dia16(self):
        """Executa automação completa do Dia 16 com ciclo entre sites"""
        driver = None
        try:
            if not self.automation_running_dia16:
                return
                
            # Importa módulos
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from auth.servopa_auth import create_driver, login_servopa
            from auth.todoist_auth import login_todoist_and_extract
            from utils.todoist_board_extractor import navigate_to_board_project_dia16, extract_complete_board
            from automation.cycle_orchestrator import executar_ciclo_completo
            
            # Obtém credenciais
            credentials = {
                'servopa': {
                    'usuario': self.servopa_login_var.get().strip(),
                    'senha': self.servopa_senha_var.get().strip()
                },
                'todoist': {
                    'usuario': self.todoist_login_var.get().strip(),
                    'senha': self.todoist_senha_var.get().strip()
                }
            }
            
            # Valida credenciais
            if not credentials['servopa']['usuario'] or not credentials['servopa']['senha']:
                raise Exception("Credenciais do Servopa não informadas")
            if not credentials['todoist']['usuario'] or not credentials['todoist']['senha']:
                raise Exception("Credenciais do Todoist não informadas")
            
            # Log das credenciais (mascarando senha)
            self.progress_callback_dia16(f"🔐 Usando Servopa: {credentials['servopa']['usuario']}")
            self.progress_callback_dia16(f"🔐 Usando Todoist: {credentials['todoist']['usuario']}")
            
            self.progress_callback_dia16("🚀 Iniciando sistema de automação DIA 16...")
            self.update_progress_dia16(5, "Iniciando navegador...")
            
            if not self.automation_running_dia16:
                return
            
            driver = create_driver()
            self.driver_dia16 = driver  # Armazena referência global
            
            try:
                # ========== ETAPA 1: LOGIN SERVOPA ==========
                if not self.automation_running_dia16:
                    return
                    
                self.progress_callback_dia16("=" * 60)
                self.progress_callback_dia16("ETAPA 1: LOGIN NO SERVOPA")
                self.progress_callback_dia16("=" * 60)
                
                self.update_progress_dia16(10, "Fazendo login no Servopa...")
                self.update_status_dia16('servopa', '⏳ Login')
                
                if login_servopa(driver, self.progress_callback_dia16, credentials['servopa']):
                    self.update_status_dia16('servopa', '✅ Conectado')
                    self.update_progress_dia16(20, "Servopa conectado")
                    self.progress_callback_dia16("✅ Login Servopa concluído!")
                else:
                    raise Exception("Falha no login Servopa")
                
                # ========== ETAPA 2: LOGIN TODOIST (NOVA ABA) ==========
                if not self.automation_running_dia16:
                    return
                
                self.progress_callback_dia16("")
                self.progress_callback_dia16("=" * 60)
                self.progress_callback_dia16("ETAPA 2: LOGIN NO TODOIST (NOVA ABA)")
                self.progress_callback_dia16("=" * 60)
                
                self.update_progress_dia16(30, "Abrindo Todoist em nova aba...")
                self.update_status_dia16('todoist', '⏳ Login')
                
                # Salva janela original do Servopa
                servopa_window = driver.current_window_handle
                
                # Abre nova aba para Todoist
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                
                # Faz login no Todoist
                from auth.todoist_auth import TODOIST_URL, TIMEOUT
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                driver.get(TODOIST_URL)
                time.sleep(3)
                
                wait = WebDriverWait(driver, TIMEOUT)
                
                # Login Todoist
                email_input = wait.until(EC.presence_of_element_located((By.ID, "element-0")))
                email_input.clear()
                for char in credentials['todoist']['usuario']:
                    email_input.send_keys(char)
                    time.sleep(0.05)
                
                time.sleep(1)
                
                password_input = wait.until(EC.presence_of_element_located((By.ID, "element-2")))
                password_input.clear()
                for char in credentials['todoist']['senha']:
                    password_input.send_keys(char)
                    time.sleep(0.05)
                
                time.sleep(1)
                
                login_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[type='submit']")
                ))
                login_button.click()
                
                self.progress_callback_dia16("⏳ Aguardando login processar...")
                time.sleep(10)
                
                self.update_status_dia16('todoist', '✅ Conectado')
                self.update_progress_dia16(40, "Todoist conectado")
                self.progress_callback_dia16("✅ Login Todoist concluído!")
                
                # ========== ETAPA 3: NAVEGAR PARA BOARD DIA 16 E EXTRAIR ==========
                if not self.automation_running_dia16:
                    return
                
                self.progress_callback_dia16("")
                self.progress_callback_dia16("=" * 60)
                self.progress_callback_dia16("ETAPA 3: EXTRAINDO BOARD DIA 16 DO TODOIST")
                self.progress_callback_dia16("=" * 60)
                
                self.update_progress_dia16(50, "Navegando para board Dia 16...")
                
                # Navega para o projeto do board DIA 16
                if not navigate_to_board_project_dia16(driver, self.progress_callback_dia16):
                    raise Exception("Falha ao navegar para o board Dia 16")
                
                self.update_progress_dia16(60, "Extraindo dados do board Dia 16...")
                
                # Extrai estrutura completa do board
                board_data = extract_complete_board(driver, self.progress_callback_dia16)
                
                if not board_data or not board_data['sections']:
                    raise Exception("Falha ao extrair dados do board Dia 16 ou board vazio")
                
                total_tasks = sum(len(s['tasks']) for s in board_data['sections'])
                
                self.update_status_dia16('todoist', '✅ Extraído')
                self.update_progress_dia16(70, f"Board Dia 16 extraído: {total_tasks} tarefas")
                self.progress_callback_dia16(f"✅ Board Dia 16 extraído: {len(board_data['sections'])} colunas, {total_tasks} tarefas")
                
                # ========== ETAPA 4: CICLO COMPLETO ==========
                if not self.automation_running_dia16:
                    return
                
                self.progress_callback_dia16("")
                self.progress_callback_dia16("=" * 60)
                self.progress_callback_dia16("ETAPA 4: EXECUTANDO CICLO COMPLETO DIA 16")
                self.progress_callback_dia16("=" * 60)
                
                self.update_progress_dia16(75, "Iniciando ciclo de automação Dia 16...")
                self.update_status_dia16('cliente', '⏳ Processando')
                self.update_status_dia16('lances', '⏳ Processando')
                
                # Executa ciclo completo com callback de histórico e função de verificação
                stats = executar_ciclo_completo(
                    driver, 
                    board_data, 
                    self.progress_callback_dia16, 
                    self.add_history_entry_dia16,
                    lambda: self.automation_running_dia16  # Função que verifica se deve continuar
                )
                
                if stats:
                    self.update_status_dia16('cliente', '✅ OK')
                    self.update_status_dia16('lances', '✅ OK')
                    
                    self.update_progress_dia16(100, "Ciclo Dia 16 concluído!")
                    self.progress_callback_dia16("")
                    self.progress_callback_dia16("🎉 AUTOMAÇÃO DIA 16 COMPLETA FINALIZADA!")
                    self.progress_callback_dia16(f"✅ {stats['completed']}/{stats['total_tasks']} tarefas concluídas")
                    self.progress_callback_dia16(f"❌ {stats['failed']} falhas")
                    self.general_status_dia16.config(text=f"✅ Concluído: {stats['completed']}/{stats['total_tasks']}", fg='green')
                else:
                    raise Exception("Falha no ciclo de automação Dia 16")
                    
            finally:
                if self.automation_running_dia16:
                    self.progress_callback_dia16("")
                    self.progress_callback_dia16("🔒 Navegador mantido aberto para verificação")
                    self.progress_callback_dia16("   (Feche manualmente quando terminar)")
                else:
                    self.progress_callback_dia16("⏹️ Automação Dia 16 interrompida")
                    if self.driver_dia16:
                        try:
                            self.progress_callback_dia16("🔒 Fechando navegador...")
                            self.driver_dia16.quit()
                            self.driver_dia16 = None
                            self.progress_callback_dia16("✅ Navegador fechado")
                        except Exception as e:
                            self.progress_callback_dia16(f"⚠️ Aviso ao fechar navegador: {e}")
                
        except Exception as e:
            self.progress_callback_dia16(f"❌ Erro crítico: {e}")
            self.general_status_dia16.config(text="❌ Erro", fg='red')
            if self.driver_dia16:
                try:
                    self.progress_callback_dia16("🔒 Fechando navegador devido ao erro...")
                    self.driver_dia16.quit()
                    self.driver_dia16 = None
                    self.progress_callback_dia16("✅ Navegador fechado")
                except Exception as cleanup_error:
                    self.progress_callback_dia16(f"⚠️ Aviso ao fechar navegador: {cleanup_error}")
        finally:
            self.automation_running_dia16 = False
            self.start_button_dia16.config(state='normal')
            self.stop_button_dia16.config(state='disabled')
            
    def run(self):
        """Executa interface"""
        self.add_log_message("🤖 Sistema iniciado")
        self.add_log_message("✨ Interface moderna carregada")
        self.add_log_message("🔐 Configure as credenciais na aba respectiva")
        self.add_log_message("⏳ Sistema pronto")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernAutomationGUI()
    app.run()
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Sistema de Automação Servopa + Todoist")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Configuração de cores e estilos
        self.colors = {
            'primary': '#3498db',
            'success': '#2ecc71', 
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'dark': '#2c3e50',
            'light': '#ecf0f1',
            'secondary': '#95a5a6'
        }
        
        self.configure_styles()
        self.create_widgets()
        self.message_queue = queue.Queue()
        self.setup_queue_processor()
        
    def configure_styles(self):
        """Configura estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para botões
        style.configure('Primary.TButton', 
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(10, 5))
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(10, 5))
        
        # Estilo para labels
        style.configure('Title.TLabel',
                       background=self.colors['dark'],
                       foreground=self.colors['light'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Status.TLabel',
                       background=self.colors['dark'],
                       foreground=self.colors['light'],
                       font=('Segoe UI', 11))
        
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Header
        self.create_header()
        
        # Status Panel
        self.create_status_panel()
        
        # Progress Panel  
        self.create_progress_panel()
        
        # Log Panel
        self.create_log_panel()
        
        # Control Panel
        self.create_control_panel()
        
    def create_header(self):
        """Cria o cabeçalho da aplicação"""
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(header_frame, 
                              text="🤖 Sistema de Automação Servopa + Todoist",
                              font=('Segoe UI', 20, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.pack(pady=15)
        
        # Subtítulo
        subtitle_label = tk.Label(header_frame,
                                 text="Automação completa com interface em tempo real",
                                 font=('Segoe UI', 11),
                                 bg=self.colors['primary'],
                                 fg='white')
        subtitle_label.pack()
        
    def create_status_panel(self):
        """Cria painel de status"""
        status_frame = tk.LabelFrame(self.root, text="📊 Status do Sistema", 
                                    font=('Segoe UI', 12, 'bold'),
                                    bg=self.colors['light'], fg=self.colors['dark'],
                                    padx=10, pady=5)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        # Grid de status
        status_grid = tk.Frame(status_frame, bg=self.colors['light'])
        status_grid.pack(fill='x')
        
        # Status items
        self.status_items = {}
        
        statuses = [
            ("🌐 Servopa", "servopa"),
            ("📋 Todoist", "todoist"), 
            ("👤 Cliente", "cliente"),
            ("🎯 Lances", "lances")
        ]
        
        for i, (text, key) in enumerate(statuses):
            frame = tk.Frame(status_grid, bg=self.colors['light'])
            frame.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            
            label = tk.Label(frame, text=text, font=('Segoe UI', 10, 'bold'),
                           bg=self.colors['light'], fg=self.colors['dark'])
            label.pack()
            
            status = tk.Label(frame, text="⏳ Aguardando", font=('Segoe UI', 9),
                            bg=self.colors['light'], fg=self.colors['secondary'])
            status.pack()
            
            self.status_items[key] = status
            
        # Configura grid
        for i in range(4):
            status_grid.grid_columnconfigure(i, weight=1)
    
    def create_progress_panel(self):
        """Cria painel de progresso"""
        progress_frame = tk.LabelFrame(self.root, text="⏳ Progresso da Automação",
                                      font=('Segoe UI', 12, 'bold'),
                                      bg=self.colors['light'], fg=self.colors['dark'],
                                      padx=10, pady=5)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        # Barra de progresso principal
        self.main_progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.main_progress.pack(pady=5)
        
        # Label de progresso
        self.progress_label = tk.Label(progress_frame, text="Sistema pronto para iniciar",
                                      font=('Segoe UI', 10),
                                      bg=self.colors['light'], fg=self.colors['dark'])
        self.progress_label.pack()
        
        # Dados extraídos
        self.data_frame = tk.Frame(progress_frame, bg=self.colors['light'])
        self.data_frame.pack(fill='x', pady=5)
        
        self.data_labels = {}
        
    def create_log_panel(self):
        """Cria painel de logs"""
        log_frame = tk.LabelFrame(self.root, text="📝 Log de Execução",
                                 font=('Segoe UI', 12, 'bold'),
                                 bg=self.colors['light'], fg=self.colors['dark'],
                                 padx=10, pady=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Área de texto com scroll
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 height=15,
                                                 font=('Consolas', 9),
                                                 bg='#1e1e1e', fg='#d4d4d4',
                                                 wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True)
        
        # Configuração de tags de cores
        self.log_text.tag_configure("SUCCESS", foreground="#4CAF50", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("ERROR", foreground="#F44336", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("WARNING", foreground="#FF9800", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("INFO", foreground="#2196F3", font=('Consolas', 9, 'bold'))
        self.log_text.tag_configure("TIMESTAMP", foreground="#9E9E9E", font=('Consolas', 8))
        
    def create_control_panel(self):
        """Cria painel de controle"""
        control_frame = tk.Frame(self.root, bg=self.colors['light'], height=60)
        control_frame.pack(fill='x', padx=10, pady=(5, 10))
        control_frame.pack_propagate(False)
        
        # Botões de controle
        button_frame = tk.Frame(control_frame, bg=self.colors['light'])
        button_frame.pack(expand=True)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Iniciar Automação",
                                      style='Primary.TButton',
                                      command=self.start_automation)
        self.start_button.pack(side='left', padx=5, pady=10)
        
        self.stop_button = ttk.Button(button_frame, text="⏸️ Parar",
                                     style='Warning.TButton',
                                     command=self.stop_automation,
                                     state='disabled')
        self.stop_button.pack(side='left', padx=5, pady=10)
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Limpar Log",
                                      command=self.clear_log)
        self.clear_button.pack(side='left', padx=5, pady=10)
        
        # Status geral
        self.general_status = tk.Label(button_frame, text="Sistema pronto",
                                      font=('Segoe UI', 10, 'bold'),
                                      bg=self.colors['light'], fg=self.colors['success'])
        self.general_status.pack(side='right', padx=10, pady=10)
        
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
                self.root.after(100, process_queue)  # Verifica novamente em 100ms
        
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
        self.log_text.insert(tk.END, f"{message}\\n", tag)
        self.log_text.see(tk.END)  # Scroll para o final
        
    def update_progress(self, value, message=""):
        """Atualiza barra de progresso"""
        self.main_progress['value'] = value
        if message:
            self.progress_label.config(text=message)
        self.root.update_idletasks()
        
    def update_status(self, component, status):
        """Atualiza status de um componente"""
        if component in self.status_items:
            self.status_items[component].config(text=status)
            
            # Muda cor baseado no status
            if "✅" in status:
                self.status_items[component].config(fg=self.colors['success'])
            elif "❌" in status:
                self.status_items[component].config(fg=self.colors['danger'])
            elif "⏳" in status:
                self.status_items[component].config(fg=self.colors['warning'])
                
    def update_extracted_data(self, key, value):
        """Atualiza dados extraídos"""
        if key not in self.data_labels:
            frame = tk.Frame(self.data_frame, bg=self.colors['light'])
            frame.pack(side='left', padx=10, pady=2)
            
            label_key = tk.Label(frame, text=f"{key}:", font=('Segoe UI', 9, 'bold'),
                               bg=self.colors['light'], fg=self.colors['dark'])
            label_key.pack(side='left')
            
            label_value = tk.Label(frame, text=str(value), font=('Segoe UI', 9),
                                 bg=self.colors['light'], fg=self.colors['primary'])
            label_value.pack(side='left', padx=(5, 0))
            
            self.data_labels[key] = label_value
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
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.general_status.config(text="Executando...", fg=self.colors['warning'])
        
        # Inicia automação em thread separada
        self.automation_thread = threading.Thread(target=self.run_automation)
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
    def stop_automation(self):
        """Para a automação"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.general_status.config(text="Parado", fg=self.colors['danger'])
        
    def clear_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)
        
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
            self.update_progress(10, "Iniciando navegador...")
            
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
                    self.message_queue.put({'type': 'data', 'key': 'Número do Grupo', 'value': numero_grupo})
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
                    
                    self.update_progress(100, "Automação concluída com sucesso!")
                    self.progress_callback("🎉 AUTOMAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
                    self.general_status.config(text="✅ Concluído", fg=self.colors['success'])
                else:
                    raise Exception("Falha na automação do Servopa")
                    
            finally:
                # Mantém navegador aberto para verificação
                self.progress_callback("🔒 Navegador mantido aberto para verificação")
                
        except Exception as e:
            self.progress_callback(f"❌ Erro na automação: {e}")
            self.general_status.config(text="❌ Erro", fg=self.colors['danger'])
        finally:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
    def run(self):
        """Executa a interface"""
        self.add_log_message("🤖 Sistema de Automação Servopa + Todoist Iniciado")
        self.add_log_message("📋 Interface gráfica carregada com sucesso")
        self.add_log_message("⏳ Pronto para iniciar automação")
        
        self.root.mainloop()

if __name__ == "__main__":
    print("=" * 80)
    print("⚠️  AVISO: Interface Desktop Desabilitada")
    print("=" * 80)
    print()
    print("🌐 O sistema agora funciona apenas via interface WEB.")
    print()
    print("📌 Para usar o sistema, execute:")
    print("   cd web && python app.py")
    print()
    print("🌍 Depois acesse: http://localhost:5000")
    print()
    print("=" * 80)
    import sys
    sys.exit(0)