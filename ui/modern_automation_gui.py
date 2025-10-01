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

class ModernAutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Sistema de Automação Servopa + Todoist v3.0")
        self.root.geometry("1100x800")
        self.root.configure(bg='#f8f9fa')
        
        # Estado da aplicação
        self.automation_running = False
        self.credentials_file = 'credentials.json'
        self.driver = None  # Armazena referência do driver
        
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
        # Header
        header = tk.Frame(self.root, bg='#0d6efd', height=80)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)
        
        tk.Label(header, text="🤖 Sistema de Automação Servopa + Todoist v3.0",
                font=('Arial', 16, 'bold'), bg='#0d6efd', fg='white').pack(pady=25)
        
        # Sistema de abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_automation_tab()
        self.create_credentials_tab()
        self.create_history_tab()
        
    def create_automation_tab(self):
        """Aba de automação"""
        tab_frame = tk.Frame(self.notebook)
        self.notebook.add(tab_frame, text='🚀 Automação')
        
        # Status cards
        status_frame = tk.LabelFrame(tab_frame, text="Status", font=('Arial', 12, 'bold'))
        status_frame.pack(fill='x', padx=10, pady=5)
        
        cards_container = tk.Frame(status_frame)
        cards_container.pack(fill='x', padx=5, pady=5)
        
        # Cards de status
        self.status_cards = {}
        for i, (text, key) in enumerate([("Servopa", "servopa"), ("Todoist", "todoist"), ("Cliente", "cliente"), ("Lances", "lances")]):
            card = tk.Frame(cards_container, bg='white', relief='solid', bd=1, width=150, height=60)
            card.pack_propagate(False)
            card.grid(row=0, column=i, padx=3, pady=3, sticky='ew')
            
            tk.Label(card, text=text, font=('Arial', 9, 'bold'), bg='white').pack(pady=5)
            status_label = tk.Label(card, text="Aguardando", font=('Arial', 8), bg='white', fg='gray')
            status_label.pack()
            self.status_cards[key] = status_label
            
        for i in range(4):
            cards_container.grid_columnconfigure(i, weight=1)
        
        # Progresso
        progress_frame = tk.LabelFrame(tab_frame, text="Progresso", font=('Arial', 12, 'bold'))
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="Sistema pronto", font=('Arial', 10))
        self.progress_label.pack(pady=2)
        
        # Log
        log_frame = tk.LabelFrame(tab_frame, text="Log", font=('Arial', 12, 'bold'))
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=('Consolas', 9),
                                                bg='#1e1e1e', fg='#d4d4d4', wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Botões
        button_frame = tk.Frame(tab_frame)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_button = tk.Button(button_frame, text="🚀 Iniciar", font=('Arial', 10, 'bold'),
                                    bg='#28a745', fg='white', command=self.start_automation, padx=20)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(button_frame, text="⏸️ Parar", font=('Arial', 10, 'bold'),
                                   bg='#dc3545', fg='white', command=self.stop_automation, padx=20, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.general_status = tk.Label(button_frame, text="Sistema pronto", font=('Arial', 10, 'bold'), fg='#28a745')
        self.general_status.pack(side='right', padx=10)
        
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
        columns = ('hora', 'grupo', 'cota', 'nome', 'valor_lance', 'status', 'observacao')
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
    
    def add_history_entry(self, grupo, cota, nome, valor_lance, status, observacao=""):
        """Adiciona entrada ao histórico"""
        entry = {
            'hora': datetime.now().strftime('%H:%M:%S'),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'grupo': str(grupo),
            'cota': str(cota),
            'nome': nome,
            'valor_lance': valor_lance,
            'status': status,
            'observacao': observacao
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
                
                self.history_tree.insert('', 'end', values=(hora, grupo, cota, nome, valor_lance, status, observacao),
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
                    writer = csv.DictWriter(f, fieldnames=['data', 'hora', 'grupo', 'cota', 'nome', 
                                                           'valor_lance', 'status', 'observacao'])
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
    app = ModernAutomationGUI()
    app.run()