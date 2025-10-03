# web/app.py
"""
🚀 OXCASH Web Interface
Interface web moderna para o sistema de automação
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
import sys
import threading
from datetime import datetime

# Adiciona path para importar módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oxcash-automation-2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Estado global da aplicação
app_state = {
    'automation_dia8_running': False,
    'automation_dia16_running': False,
    'driver_dia8': None,
    'driver_dia16': None,
    'stats': {
        'dia8': {'total': 0, 'success': 0, 'failed': 0, 'running': 0},
        'dia16': {'total': 0, 'success': 0, 'failed': 0, 'running': 0}
    }
}

# ========== ROTAS PRINCIPAIS ==========

@app.route('/')
def index():
    """Dashboard principal"""
    return render_template('index.html')

@app.route('/automation/dia8')
def automation_dia8():
    """Página de automação Dia 8"""
    return render_template('automation_dia8.html')

@app.route('/automation/dia16')
def automation_dia16():
    """Página de automação Dia 16"""
    return render_template('automation_dia16.html')

@app.route('/whatsapp')
def whatsapp():
    """Página de envio WhatsApp"""
    return render_template('whatsapp.html')

@app.route('/history')
def history():
    """Página de histórico"""
    return render_template('history.html')

@app.route('/credentials')
def credentials():
    """Página de credenciais"""
    return render_template('credentials.html')

# ========== API REST ==========

@app.route('/api/stats')
def api_stats():
    """Retorna estatísticas gerais"""
    stats_dia8 = load_history_stats('history_dia8.json')
    stats_dia16 = load_history_stats('history_dia16.json')
    
    return jsonify({
        'dia8': stats_dia8,
        'dia16': stats_dia16,
        'running': {
            'dia8': app_state['automation_dia8_running'],
            'dia16': app_state['automation_dia16_running']
        }
    })

@app.route('/api/history/<dia>')
def api_history(dia):
    """Retorna histórico de um dia específico"""
    filename = f'history_{dia}.json'
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/credentials', methods=['GET', 'POST'])
def api_credentials():
    """Gerencia credenciais"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
    
    if request.method == 'GET':
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Retorna TUDO incluindo senhas (interface web é local/confiável)
                return jsonify({'success': True, 'data': data})
            else:
                return jsonify({'success': True, 'data': {}})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return jsonify({'success': True, 'message': 'Credenciais salvas com sucesso'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evolution-config', methods=['GET', 'POST'])
def api_evolution_config():
    """Gerencia configuração da Evolution API"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evolution_config.json')
    
    if request.method == 'GET':
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify({'success': True, 'data': data})
            else:
                return jsonify({'success': True, 'data': {}})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return jsonify({'success': True, 'message': 'Configuração salva com sucesso'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/history/clear/<dia>', methods=['POST'])
def api_clear_history(dia):
    """Limpa histórico de um dia específico"""
    if dia not in ['dia8', 'dia16', 'all', 'errors']:
        return jsonify({'success': False, 'error': 'Dia inválido'})
    
    try:
        if dia == 'errors':
            # Limpa APENAS registros com erro em ambos os dias
            dias_to_clean = ['dia8', 'dia16']
            total_removed = 0
            
            for d in dias_to_clean:
                filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'history_{d}.json')
                
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Filtra APENAS os que NÃO são erro
                    data_filtered = [
                        entry for entry in data 
                        if not ('❌' in entry.get('status', '') or 
                                'Erro' in entry.get('status', '') or 
                                'erro' in entry.get('status', '').lower())
                    ]
                    
                    removed = len(data) - len(data_filtered)
                    total_removed += removed
                    
                    # Salva apenas os não-erros
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data_filtered, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True, 
                'message': f'{total_removed} registros com erro removidos'
            })
        
        elif dia == 'all':
            # Limpa ambos os históricos COMPLETAMENTE
            dias = ['dia8', 'dia16']
        else:
            dias = [dia]
        
        for d in dias:
            filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'history_{d}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        
        msg = 'Todos os históricos limpos' if dia == 'all' else f'Histórico do {dia} limpo'
        return jsonify({'success': True, 'message': msg})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update-from-github', methods=['POST'])
def api_update_from_github():
    """Atualiza código do GitHub"""
    try:
        import subprocess
        
        # Obtém diretório do projeto
        project_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Primeiro, adiciona safe.directory para evitar dubious ownership
        try:
            safe_config_cmd = ['git', 'config', '--global', '--add', 'safe.directory', project_dir]
            subprocess.run(safe_config_cmd, cwd=project_dir, capture_output=True, text=True, timeout=10)
        except:
            pass  # Se falhar, continua mesmo assim
        
        # Guarda mudanças locais temporariamente usando stash
        stashed = False
        try:
            # Verifica se há mudanças
            status_cmd = ['git', 'status', '--porcelain']
            status_result = subprocess.run(status_cmd, cwd=project_dir, capture_output=True, text=True, timeout=10)
            
            if status_result.stdout.strip():  # Se há mudanças
                # Faz stash (guarda mudanças temporariamente)
                stash_cmd = ['git', 'stash', 'push', '-u', '-m', 'Auto-stash antes de atualizar do GitHub']
                subprocess.run(stash_cmd, cwd=project_dir, capture_output=True, text=True, timeout=10)
                stashed = True
        except:
            pass
        
        # Executa git pull
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Se fez stash, restaura mudanças
        if stashed:
            try:
                stash_pop_cmd = ['git', 'stash', 'pop']
                subprocess.run(stash_pop_cmd, cwd=project_dir, capture_output=True, text=True, timeout=10)
            except:
                pass
        
        if result.returncode == 0:
            msg = 'Atualização concluída com sucesso!'
            if stashed:
                msg += ' (Suas mudanças locais foram preservadas)'
            
            return jsonify({
                'success': True,
                'message': msg,
                'output': result.stdout,
                'stashed': stashed,
                'needs_restart': 'Already up to date' not in result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao executar git pull',
                'output': result.stderr,
                'stashed': stashed
            })
    
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout ao executar comando'})
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'Git não encontrado. Instale o Git primeiro.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/automation/status/<dia>', methods=['GET'])
def api_automation_status(dia):
    """Retorna status atual da automação"""
    if dia not in ['dia8', 'dia16']:
        return jsonify({'success': False, 'error': 'Dia inválido'})
    
    return jsonify({
        'success': True,
        'running': app_state[f'automation_{dia}_running'],
        'dia': dia
    })

@app.route('/api/automation/start/<dia>', methods=['POST'])
def api_start_automation(dia):
    """Inicia automação"""
    if dia not in ['dia8', 'dia16']:
        return jsonify({'success': False, 'error': 'Dia inválido'})
    
    if app_state[f'automation_{dia}_running']:
        return jsonify({'success': False, 'error': 'Automação já está rodando'})
    
    # Marca como rodando ANTES de iniciar thread
    app_state[f'automation_{dia}_running'] = True
    
    # Notifica interface IMEDIATAMENTE via WebSocket
    with app.app_context():
        socketio.emit('automation_status', {'dia': dia, 'running': True}, namespace='/')
        socketio.emit('log', {'dia': dia, 'message': '🚀 Iniciando automação...'}, namespace='/')
        socketio.emit('progress', {'dia': dia, 'value': 5, 'message': 'Preparando...'}, namespace='/')
    
    # Inicia thread de automação
    thread = threading.Thread(target=run_automation_thread, args=(dia,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': f'Automação {dia} iniciada'})

@app.route('/api/automation/stop/<dia>', methods=['POST'])
def api_stop_automation(dia):
    """Para automação"""
    if dia not in ['dia8', 'dia16']:
        return jsonify({'success': False, 'error': 'Dia inválido'})
    
    # Marca para parar PRIMEIRO
    app_state[f'automation_{dia}_running'] = False
    
    # Notifica IMEDIATAMENTE que está parando
    with app.app_context():
        socketio.emit('automation_status', {'dia': dia, 'running': False}, namespace='/')
        socketio.emit('log', {'dia': dia, 'message': '⏹️ Parando automação...'}, namespace='/')
        socketio.emit('progress', {'dia': dia, 'value': 0, 'message': 'Parando...'}, namespace='/')
    
    # Fecha driver se existir
    driver_key = f'driver_{dia}'
    if app_state[driver_key]:
        try:
            progress_callback(dia, "🔒 Fechando navegador Chrome...")
            app_state[driver_key].quit()
            app_state[driver_key] = None
            progress_callback(dia, "✅ Chrome fechado com sucesso!")
        except Exception as e:
            progress_callback(dia, f"⚠️ Navegador já estava fechado ou erro: {e}")
    
    # Confirma parada
    with app.app_context():
        socketio.emit('log', {'dia': dia, 'message': '⏹️ Automação parada pelo usuário - histórico não será afetado'}, namespace='/')
        socketio.emit('progress', {'dia': dia, 'value': 0, 'message': 'Parado'}, namespace='/')
    
    return jsonify({'success': True, 'message': f'Automação {dia} parada e Chrome fechado'})

@app.route('/api/whatsapp/send', methods=['POST'])
def api_whatsapp_send():
    """Envia mensagens WhatsApp"""
    try:
        data = request.json
        dia = data.get('dia')
        contacts_text = data.get('contacts', '')
        message_template = data.get('message', '')
        
        if not contacts_text or not message_template:
            return jsonify({'success': False, 'error': 'Contatos e mensagem são obrigatórios'})
        
        # Carrega config da Evolution API
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evolution_config.json')
        if not os.path.exists(config_file):
            return jsonify({'success': False, 'error': 'Configuração da Evolution API não encontrada'})
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'api' not in config:
            return jsonify({'success': False, 'error': 'Configuração da API incompleta'})
        
        # Importa módulo de envio
        from utils.evolution_api import EvolutionAPI, parse_contacts_from_text
        
        # Cria cliente API
        api = EvolutionAPI(
            config['api']['base_url'],
            config['api']['instance_name'],
            config['api']['api_key']
        )
        
        # Parse contatos
        contacts = parse_contacts_from_text(contacts_text)
        
        if not contacts:
            return jsonify({'success': False, 'error': 'Nenhum contato válido encontrado'})
        
        # Envia mensagens
        def progress_callback(msg):
            socketio.emit('log', {'dia': 'whatsapp', 'message': msg})
        
        results = api.send_bulk_messages(
            contacts,
            message_template,
            delay_between_messages=2.0,
            progress_callback=progress_callback
        )
        
        # Retorna resultado
        return jsonify({
            'success': True,
            'message': f'Envio concluído para {dia}',
            'stats': {
                'total': results['total'],
                'success': results['success'],
                'failed': results['failed']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== WEBSOCKET EVENTS ==========

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    emit('connected', {'message': 'Conectado ao servidor'})
    print('🔌 Cliente conectado')

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print('🔌 Cliente desconectado')

@socketio.on('test_connection')
def handle_test():
    """Teste de conexão"""
    emit('log', {'dia': 'general', 'message': '✅ Conexão WebSocket OK'})

# ========== FUNÇÕES AUXILIARES ==========

def load_history_stats(filename):
    """Carrega estatísticas do histórico"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'stopped': 0,
        'recent': []
    }
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stats['total'] = len(data)
            
            for entry in data:
                status = entry.get('status', '')
                if 'sucesso' in status.lower() or '✅' in status:
                    stats['success'] += 1
                elif 'erro' in status.lower() or '❌' in status or 'falha' in status.lower():
                    stats['failed'] += 1
                elif '⏹️' in status or 'parado' in status.lower():
                    stats['stopped'] += 1
            
            # Últimos 5 registros
            stats['recent'] = list(reversed(data[-5:]))
    except:
        pass
    
    return stats

def progress_callback(dia, message):
    """Callback para enviar progresso via WebSocket"""
    try:
        with app.app_context():
            socketio.emit('log', {'dia': dia, 'message': message}, namespace='/')
    except Exception as e:
        print(f"Erro ao enviar log: {e}")

def run_automation_thread(dia):
    """Thread de automação"""
    try:
        from auth.servopa_auth import create_driver, login_servopa
        from utils.todoist_board_extractor import navigate_to_board_project, navigate_to_board_project_dia16, extract_complete_board
        from automation.cycle_orchestrator import executar_ciclo_completo
        
        progress_callback(dia, f"🚀 Iniciando automação {dia.upper()}...")
        socketio.emit('progress', {'dia': dia, 'value': 10, 'message': 'Iniciando navegador...'})
        
        # Carrega credenciais
        creds_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        with open(creds_file, 'r') as f:
            credentials = json.load(f)
        
        # Cria driver em MODO VISÍVEL (janela Chrome visível na tela)
        progress_callback(dia, "🖥️ Abrindo navegador Chrome...")
        driver = create_driver(headless=False)
        app_state[f'driver_{dia}'] = driver
        
        try:
            # Login Servopa
            socketio.emit('progress', {'dia': dia, 'value': 20, 'message': 'Login Servopa...'})
            if not login_servopa(driver, lambda msg: progress_callback(dia, msg), credentials['servopa']):
                raise Exception("Falha no login Servopa")
            
            # Login Todoist
            socketio.emit('progress', {'dia': dia, 'value': 40, 'message': 'Login Todoist...'})
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get("https://todoist.com/auth/login")
            
            import time
            time.sleep(3)
            
            wait = WebDriverWait(driver, 20)
            email_input = wait.until(EC.presence_of_element_located((By.ID, "element-0")))
            email_input.send_keys(credentials['todoist']['usuario'])
            
            password_input = wait.until(EC.presence_of_element_located((By.ID, "element-2")))
            password_input.send_keys(credentials['todoist']['senha'])
            
            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            login_button.click()
            time.sleep(10)
            
            # Navega para board
            socketio.emit('progress', {'dia': dia, 'value': 60, 'message': 'Extraindo board...'})
            nav_func = navigate_to_board_project if dia == 'dia8' else navigate_to_board_project_dia16
            if not nav_func(driver, lambda msg: progress_callback(dia, msg)):
                raise Exception("Falha ao navegar para board")
            
            board_data = extract_complete_board(driver, lambda msg: progress_callback(dia, msg))
            if not board_data or not board_data['sections']:
                raise Exception("Board vazio ou inválido")
            
            # Executa ciclo
            socketio.emit('progress', {'dia': dia, 'value': 80, 'message': 'Executando ciclo...'})
            
            def history_callback(grupo, cota, nome, valor, status, obs="", **kwargs):
                # Salva no histórico via arquivo
                filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'history_{dia}.json')
                entry = {
                    'hora': datetime.now().strftime('%H:%M:%S'),
                    'data': datetime.now().strftime('%Y-%m-%d'),
                    'grupo': str(grupo) if grupo else '-',
                    'cota': str(cota) if cota else '-',
                    'nome': str(nome) if nome else '-',
                    'valor_lance': str(valor) if valor else '-',
                    'status': str(status) if status else 'Processado',
                    'observacao': str(obs) if obs else '',
                    'protocolo': str(kwargs.get('protocolo', '')) if kwargs.get('protocolo') else '-',
                    'documento_url': str(kwargs.get('documento_url', '')) if kwargs.get('documento_url') else ''
                }
                
                try:
                    # Lê histórico existente
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        data = []
                    
                    # Adiciona nova entrada
                    data.append(entry)
                    
                    # Salva de volta
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    # Log de confirmação
                    progress_callback(dia, f"📝 Histórico salvo: {nome} - {status}")
                    
                    # Notifica via WebSocket
                    socketio.emit('history_update', {'dia': dia, 'entry': entry})
                    
                except Exception as e:
                    progress_callback(dia, f"⚠️ Erro ao salvar histórico: {e}")
                    socketio.emit('history_update', {'dia': dia, 'entry': entry})
                except:
                    pass
            
            stats = executar_ciclo_completo(
                driver,
                board_data,
                lambda msg: progress_callback(dia, msg),
                history_callback,
                lambda: app_state[f'automation_{dia}_running']
            )
            
            if stats:
                socketio.emit('progress', {'dia': dia, 'value': 100, 'message': 'Concluído!'})
                progress_callback(dia, f"🎉 Automação finalizada: {stats['completed']}/{stats['total_tasks']} sucesso")
            
        finally:
            if app_state[f'automation_{dia}_running']:
                progress_callback(dia, "🔒 Navegador mantido aberto")
            else:
                if driver:
                    driver.quit()
                app_state[f'driver_{dia}'] = None
    
    except Exception as e:
        progress_callback(dia, f"❌ Erro: {e}")
        socketio.emit('progress', {'dia': dia, 'value': 0, 'message': 'Erro'})
    
    finally:
        app_state[f'automation_{dia}_running'] = False
        socketio.emit('automation_status', {'dia': dia, 'running': False})

# ========== MAIN ==========

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 OXCASH - Interface Web Moderna')
    print('=' * 60)
    print('📍 Servidor iniciado em: http://localhost:5000')
    print('🌐 Acesse pelo navegador para usar a interface')
    print('=' * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
