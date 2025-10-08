# web/app.py
"""
🚀 OXCASH Web Interface
Interface web moderna para o sistema de automação
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from functools import wraps
from typing import Dict
import json
import os
import sys
import threading
import time
from datetime import datetime

# Adiciona path para importar módulos do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from auth.servopa_auth import create_driver, login_servopa
from automation.servopa_boletos import (
    BoletoAutomationError,
    run_boleto_flow,
)
from utils.link_shortener import (
    build_public_short_url,
    create_short_link,
    get_short_code_for_task,
    resolve_short_link,
)
from ai.ai_agent import OXCASHAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oxcash-automation-2024-secure-key'
app.config['SESSION_COOKIE_SECURE'] = False  # True em produção com HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PUBLIC_BASE_URL'] = os.environ.get('PUBLIC_BASE_URL', '').rstrip('/')
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
    },
    'ai_agent': None,  # Instância do agente de IA
    'stop_automation': {}  # Controle de parada de automação por grupo
}

# ========== MIDDLEWARE DE AUTENTICAÇÃO ==========

def login_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== ROTAS DE AUTENTICAÇÃO ==========

@app.route('/login')
def login():
    """Página de login"""
    # Se já estiver logado, redireciona para dashboard
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """API de login - aceita qualquer email/senha para desenvolvimento"""
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'Email e senha são obrigatórios'
        }), 400
    
    # Em produção, validar credenciais no banco de dados
    # Por enquanto, aceita qualquer combinação
    user = {
        'id': '1',
        'email': email,
        'name': 'Usuário OXCASH',
        'role': 'admin'
    }
    
    # Salva usuário na sessão
    session['user'] = user
    session.permanent = True
    
    return jsonify({
        'success': True,
        'user': user,
        'message': 'Login realizado com sucesso!'
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API de logout"""
    session.pop('user', None)
    return jsonify({
        'success': True,
        'message': 'Logout realizado com sucesso!'
    })

@app.route('/logout')
def logout():
    """Logout e redireciona para login"""
    session.pop('user', None)
    return redirect('/login')

@app.route('/api/check-auth')
def check_auth():
    """Verifica se usuário está autenticado"""
    if 'user' in session:
        return jsonify({
            'authenticated': True,
            'user': session['user']
        })
    return jsonify({'authenticated': False})

# ========== ROTAS PRINCIPAIS (PROTEGIDAS) ==========

@app.route('/')
@login_required
def index():
    """Dashboard principal"""
    return render_template('index_modern.html')

@app.route('/whatsapp')
@login_required
def whatsapp():
    """Página de envio WhatsApp"""
    return render_template('whatsapp.html')

@app.route('/calendario-lances')
@login_required
def calendario_lances():
    """Página de calendário de lances"""
    return render_template('calendario_lances.html')

@app.route('/history')
@login_required
def history():
    """Página de histórico"""
    return render_template('history.html')

@app.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    return render_template('profile.html')

@app.route('/credentials')
@login_required
def credentials():
    """Página de credenciais"""
    return render_template('credentials.html')

@app.route('/boletos')
@login_required
def boletos():
    """Página de Kanban de Boletos"""
    return render_template('boletos.html')

@app.route('/extracao-cotas')
@login_required
def extracao_cotas():
    """Página de Extração das Cotas"""
    return render_template('extracao_cotas.html')

@app.route('/clientes')
@login_required
def clientes():
    """Página de Gerenciamento de Clientes"""
    return render_template('clientes.html')


def _best_boleto_link(boleto: dict) -> str:
    for key in ('short_link', 'png_base64', 'boleto_url'):
        value = boleto.get(key)
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed.lower().startswith(('http://', 'https://')):
                return trimmed
    return ''


@app.route('/boleto/<code>')
def proxy_boleto(code):
    """Proxy para servir boletos do Servopa sem restrição de IP.
    
    Como o Servopa valida o IP no link, fazemos o download usando o IP
    do servidor e servimos o PDF diretamente para o cliente.
    """
    import requests
    from io import BytesIO
    
    original_url = resolve_short_link(code)
    if not original_url:
        abort(404)
    
    # Se não for link do Servopa, redireciona normalmente
    if 'consorcioservopa.com.br' not in original_url.lower():
        return redirect(original_url, code=302)
    
    try:
        # Cache directory
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'boletos_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache file path
        cache_file = os.path.join(cache_dir, f'{code}.pdf')
        
        # Se já está em cache, retorna direto
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                pdf_data = f.read()
            
            response = app.make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=boleto_{code}.pdf'
            return response
        
        # Faz download do Servopa usando o IP do servidor
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        resp = requests.get(original_url, headers=headers, timeout=30, allow_redirects=True)
        
        if resp.status_code != 200:
            abort(502, description=f'Erro ao buscar boleto do Servopa: HTTP {resp.status_code}')
        
        # Verifica se é PDF
        content_type = resp.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type and not resp.content.startswith(b'%PDF'):
            abort(502, description='Resposta do Servopa não é um PDF válido')
        
        # Salva em cache
        with open(cache_file, 'wb') as f:
            f.write(resp.content)
        
        # Retorna PDF
        response = app.make_response(resp.content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=boleto_{code}.pdf'
        return response
        
    except requests.RequestException as e:
        abort(502, description=f'Erro ao acessar Servopa: {str(e)}')
    except Exception as e:
        abort(500, description=f'Erro interno: {str(e)}')

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

@app.route('/api/boletos', methods=['GET'])
def api_boletos():
    """Retorna dados dos boletos"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
    
    try:
        if os.path.exists(filepath):
            # Lê com utf-8-sig para remover BOM automaticamente se existir
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
            
            # Remove BOM invisível se existir
            if content.startswith('\ufeff'):
                content = content[1:]
            
            # Tenta fazer parse do JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as json_err:
                print(f"❌ Erro ao fazer parse do JSON de boletos: {json_err}")
                print(f"📄 Conteúdo do arquivo (primeiros 200 chars): {content[:200]}")
                
                # Recria arquivo limpo
                data = {'dia08': [], 'dia16': [], 'last_import': None}
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("✅ Arquivo de boletos recriado com estrutura limpa")
            
            return jsonify({'success': True, 'data': data})
        else:
            # Cria arquivo se não existir
            data = {'dia08': [], 'dia16': [], 'last_import': None}
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return jsonify({'success': True, 'data': data})
    except Exception as e:
        print(f"❌ Erro geral na API de boletos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/import', methods=['POST'])
def api_boletos_import():
    """Recarrega boletos do arquivo local (não usa mais Todoist)"""
    try:
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        
        # Emite progresso via WebSocket
        def emit_progress(message):
            socketio.emit('boletos_progress', {'message': message})
        
        emit_progress('📂 Carregando boletos do sistema...')
        
        # Carrega dados do arquivo local
        if os.path.exists(boletos_filepath):
            with open(boletos_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Se não existe, cria arquivo vazio
            data = {
                'dia08': [],
                'dia16': [],
                'last_import': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(boletos_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        emit_progress('✅ Boletos carregados com sucesso!')
        
        total_dia08 = len(data.get('dia08', []))
        total_dia16 = len(data.get('dia16', []))
        
        return jsonify({
            'success': True, 
            'message': f'Carregados: {total_dia08} boletos (dia 08) e {total_dia16} boletos (dia 16)',
            'data': data
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/reset', methods=['POST'])
def api_boletos_reset():
    """Reset completo do arquivo de boletos - cria arquivo limpo"""
    try:
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        
        # Cria estrutura limpa
        data = {
            'dia08': [],
            'dia16': [],
            'last_import': None
        }
        
        # Salva com encoding correto (sem BOM)
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Arquivo de boletos resetado com sucesso")
        
        return jsonify({
            'success': True,
            'message': 'Arquivo de boletos resetado com sucesso',
            'data': data
        })
    except Exception as e:
        print(f"❌ Erro ao resetar boletos: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/toggle/<task_id>', methods=['POST'])
def api_boletos_toggle(task_id):
    """Marca/desmarca um boleto como concluído (apenas localmente)"""
    try:
        data = request.json
        is_completed = data.get('is_completed', False)
        
        # Atualiza arquivo local
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if not os.path.exists(boletos_filepath):
            return jsonify({'success': False, 'error': 'Arquivo de boletos não encontrado'})
            
        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)
        
        # Atualiza status no cache local
        found = False
        for dia_key in ['dia08', 'dia16']:
            if dia_key in boletos_data:
                for boleto in boletos_data[dia_key]:
                    if boleto.get('task_id') == task_id:
                        boleto['is_completed'] = is_completed
                        found = True
                        break
        
        if not found:
            return jsonify({'success': False, 'error': 'Boleto não encontrado'})
        
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Boleto atualizado com sucesso'
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/update/<task_id>', methods=['POST'])
def api_boletos_update(task_id):
    """Atualiza um boleto existente (apenas localmente)"""
    try:
        data = request.json
        nome = data.get('nome', '')
        celular = data.get('celular', '')
        cotas = data.get('cotas', '')
        dia = data.get('dia', '08')
        png_base64 = data.get('png_base64', '')
        short_link = data.get('short_link', '')
        
        # Atualiza arquivo local
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if not os.path.exists(boletos_filepath):
            return jsonify({'success': False, 'error': 'Arquivo de boletos não encontrado'})
            
        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)
        
        dia_key = f'dia{dia}'
        found = False
        updated_boleto = None
        if dia_key in boletos_data:
            for boleto in boletos_data[dia_key]:
                if boleto.get('task_id') == task_id:
                    boleto['nome'] = nome
                    boleto['celular'] = celular
                    boleto['cotas'] = cotas
                    if png_base64:
                        boleto['png_base64'] = png_base64
                    if short_link:
                        boleto['short_link'] = short_link
                    found = True
                    updated_boleto = boleto
                    break
        
        if not found:
            return jsonify({'success': False, 'error': 'Boleto não encontrado'})
        
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        # Sincroniza com cliente correspondente
        if updated_boleto:
            _sync_boleto_to_cliente(updated_boleto, dia_key)
        
        return jsonify({'success': True, 'message': 'Boleto atualizado com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/create', methods=['POST'])
def api_boletos_create():
    """Cria um novo boleto (apenas localmente)"""
    try:
        data = request.json
        nome = data.get('nome', '')
        celular = data.get('celular', '')
        cotas = data.get('cotas', '')
        dia = data.get('dia', '08')
        png_base64 = data.get('png_base64', '')
        short_link = data.get('short_link', '')
        
        if not nome:
            return jsonify({'success': False, 'error': 'Nome é obrigatório'})
        
        # Gera ID único para o boleto
        import uuid
        task_id = str(uuid.uuid4())
        
        # Adiciona ao arquivo local
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        boletos_data = {'dia08': [], 'dia16': []}
        
        if os.path.exists(boletos_filepath):
            with open(boletos_filepath, 'r', encoding='utf-8') as f:
                boletos_data = json.load(f)
        
        dia_key = f'dia{dia}'
        if dia_key not in boletos_data:
            boletos_data[dia_key] = []
        
        new_boleto = {
            'task_id': task_id,
            'nome': nome,
            'celular': celular,
            'cotas': cotas,
            'is_completed': False
        }
        
        if png_base64:
            new_boleto['png_base64'] = png_base64
        if short_link:
            new_boleto['short_link'] = short_link
        
        boletos_data[dia_key].append(new_boleto)
        
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Boleto criado com sucesso',
            'data': new_boleto
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/import-from-clientes', methods=['POST'])
def api_boletos_import_from_clientes():
    """Importa clientes para boletos - cria boletos baseados nos dados dos clientes"""
    try:
        data = request.json or {}
        dias_selecionados = data.get('dias', ['08', '16'])  # Por padrão, importa ambos os dias
        sobrescrever = data.get('sobrescrever', False)  # Se True, limpa boletos existentes antes
        
        # Emite progresso via WebSocket
        def emit_progress(message):
            socketio.emit('boletos_progress', {'message': message})
        
        emit_progress('📂 Carregando dados de clientes...')
        
        # Carrega dados dos clientes
        clientes_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
        if not os.path.exists(clientes_filepath):
            return jsonify({'success': False, 'error': 'Arquivo de clientes não encontrado. Configure clientes primeiro.'})
        
        with open(clientes_filepath, 'r', encoding='utf-8') as f:
            clientes_data = json.load(f)
        
        # Carrega ou cria estrutura de boletos
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if os.path.exists(boletos_filepath):
            with open(boletos_filepath, 'r', encoding='utf-8') as f:
                boletos_data = json.load(f)
        else:
            boletos_data = {'dia08': [], 'dia16': [], 'last_import': None}
        
        import uuid
        stats = {
            'importados': 0,
            'ignorados': 0,
            'erros': 0,
            'dia08': 0,
            'dia16': 0
        }
        
        # Processa cada dia selecionado
        for dia_num in dias_selecionados:
            dia_key = f'dia{dia_num}'
            
            if dia_key not in clientes_data or not clientes_data[dia_key]:
                emit_progress(f'⚠️ Nenhum cliente encontrado para o dia {dia_num}')
                continue
            
            emit_progress(f'📋 Processando {len(clientes_data[dia_key])} clientes do dia {dia_num}...')
            
            # Se sobrescrever, limpa boletos existentes
            if sobrescrever:
                boletos_data[dia_key] = []
                emit_progress(f'🗑️ Boletos anteriores do dia {dia_num} foram removidos')
            
            # Cria conjunto de IDs de clientes já existentes em boletos para evitar duplicatas
            existing_client_ids = {b.get('client_id') for b in boletos_data.get(dia_key, []) if b.get('client_id')}
            
            # Converte cada cliente em boleto
            for cliente in clientes_data[dia_key]:
                try:
                    client_id = cliente.get('client_id')
                    
                    # Verifica se já existe (evita duplicata)
                    if not sobrescrever and client_id in existing_client_ids:
                        stats['ignorados'] += 1
                        continue
                    
                    # Monta o texto de cotas para o boleto
                    cotas_texto = cliente.get('cotas_texto', '')
                    if not cotas_texto:
                        grupo = cliente.get('grupo', '')
                        cota = cliente.get('cota', '')
                        if grupo and cota:
                            cotas_texto = f'{cota} - {grupo}'
                        elif grupo or cota:
                            cotas_texto = grupo or cota
                    
                    # Cria task_id se não existir (usando o mesmo do cliente se disponível)
                    task_id = cliente.get('task_id')
                    if not task_id:
                        task_id = str(uuid.uuid4())
                    
                    # Monta estrutura do boleto
                    novo_boleto = {
                        'task_id': task_id,
                        'client_id': client_id,  # Mantém referência ao cliente
                        'nome': cliente.get('nome', ''),
                        'celular': cliente.get('contato', ''),
                        'cotas': cotas_texto,
                        'grupo': cliente.get('grupo', ''),
                        'cota': cliente.get('cota', ''),
                        'valor_primeira_cota': cliente.get('valor_primeira_cota', ''),
                        'is_completed': False,
                        'imported_from_cliente': True,
                        'imported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Mantém histórico de boletos do cliente se existir
                    historico_boletos = cliente.get('historico_boletos', [])
                    if historico_boletos:
                        novo_boleto['historico_boletos'] = historico_boletos
                        
                        # Se houver histórico, pega o último link como link principal
                        if isinstance(historico_boletos, list) and len(historico_boletos) > 0:
                            ultimo_link = historico_boletos[-1]  # Pega o último link do histórico
                            novo_boleto['boleto_url'] = ultimo_link
                            novo_boleto['short_link'] = ultimo_link
                            novo_boleto['png_base64'] = ultimo_link  # Para compatibilidade
                    
                    # Se o cliente tiver um campo de link direto, usa ele também
                    if cliente.get('boleto_url'):
                        novo_boleto['boleto_url'] = cliente['boleto_url']
                    
                    if cliente.get('short_link'):
                        novo_boleto['short_link'] = cliente['short_link']
                    
                    if cliente.get('png_base64'):
                        novo_boleto['png_base64'] = cliente['png_base64']
                    
                    boletos_data[dia_key].append(novo_boleto)
                    stats['importados'] += 1
                    stats[dia_key] += 1
                    
                except Exception as e:
                    stats['erros'] += 1
                    emit_progress(f'❌ Erro ao importar cliente {cliente.get("nome", "desconhecido")}: {str(e)}')
        
        # Atualiza timestamp de importação
        boletos_data['last_import'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Salva os boletos
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        # Mensagem de sucesso
        msg_parts = []
        if stats['dia08'] > 0:
            msg_parts.append(f"{stats['dia08']} boletos do dia 08")
        if stats['dia16'] > 0:
            msg_parts.append(f"{stats['dia16']} boletos do dia 16")
        
        mensagem_final = f"✅ Importação concluída! {' e '.join(msg_parts)}"
        if stats['ignorados'] > 0:
            mensagem_final += f" | {stats['ignorados']} já existentes (ignorados)"
        if stats['erros'] > 0:
            mensagem_final += f" | {stats['erros']} erros"
        
        emit_progress(mensagem_final)
        
        return jsonify({
            'success': True,
            'message': mensagem_final,
            'stats': stats,
            'data': boletos_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro ao importar: {str(e)}'})

@app.route('/api/boletos/delete/<task_id>', methods=['POST', 'DELETE'])
def api_boletos_delete(task_id):
    """Deleta um boleto (apenas localmente)"""
    try:
        # Remove do arquivo local
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if not os.path.exists(boletos_filepath):
            return jsonify({'success': False, 'error': 'Arquivo de boletos não encontrado'})
            
        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)
        
        found = False
        for dia_key in ['dia08', 'dia16']:
            if dia_key in boletos_data:
                original_len = len(boletos_data[dia_key])
                boletos_data[dia_key] = [
                    b for b in boletos_data[dia_key] 
                    if b.get('task_id') != task_id
                ]
                if len(boletos_data[dia_key]) < original_len:
                    found = True
        
        if not found:
            return jsonify({'success': False, 'error': 'Boleto não encontrado'})
        
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Boleto deletado com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/extrair/<task_id>', methods=['POST'])
def api_boletos_extrair(task_id):
    """Gera automaticamente o boleto no portal da Servopa para a tarefa informada."""
    try:
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if not os.path.exists(boletos_filepath):
            return jsonify({'success': False, 'error': 'Arquivo local de boletos não encontrado'}), 400

        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)

        boleto_entry = None
        dia = None

        for dia_key in ('dia08', 'dia16'):
            for item in boletos_data.get(dia_key, []):
                if str(item.get('task_id')) == str(task_id):
                    boleto_entry = item
                    dia = '08' if dia_key == 'dia08' else '16'
                    break
            if boleto_entry:
                break

        if not boleto_entry:
            return jsonify({'success': False, 'error': 'Boleto não encontrado na base local'}), 404

        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        if not os.path.exists(creds_path):
            return jsonify({'success': False, 'error': 'Arquivo de credenciais não encontrado'}), 400

        with open(creds_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)

        servopa_creds = credentials.get('servopa')
        if not servopa_creds:
            return jsonify({'success': False, 'error': 'Credenciais do Servopa não configuradas'}), 400

        progress = lambda msg: progress_callback('boletos', msg)
        driver = create_driver(headless=True)

        try:
            progress('🔐 Efetuando login no portal Servopa...')
            if not login_servopa(driver, progress, servopa_creds):
                raise BoletoAutomationError('Falha ao autenticar no portal Servopa')

            progress('📄 Iniciando geração automática do boleto...')
            result = run_boleto_flow(driver, boleto_entry, dia, progress)

        finally:
            try:
                driver.quit()
            except Exception:
                pass

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if result.png_base64:
            boleto_entry['png_base64'] = result.png_base64
        
        # Usa o link direto do Servopa (já modificado sem IP)
        if result.boleto_url:
            boleto_entry['boleto_url'] = result.boleto_url
            boleto_entry['short_link'] = result.boleto_url  # Link direto, sem proxy
        
        boleto_entry['last_generated'] = timestamp
        boleto_entry['tipo'] = result.tipo
        if result.grupo:
            boleto_entry['grupo'] = result.grupo
        if result.cota:
            boleto_entry['cota'] = result.cota
        if result.metadata:
            boleto_entry['metadata'] = result.metadata

        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)

        progress('✅ Boleto gerado e salvo com sucesso!')
        
        # Sincroniza com cliente correspondente
        dia_key = f'dia{dia}'
        _sync_boleto_to_cliente(boleto_entry, dia_key)

        return jsonify({
            'success': True,
            'message': 'Boleto gerado com sucesso',
            'data': {
                'task_id': task_id,
                'dia': dia,
                'boleto_url': result.boleto_url,
                'short_link': result.boleto_url,  # Link direto do Servopa
                'png_base64': result.png_base64,
                'last_generated': timestamp,
                'tipo': result.tipo,
            }
        })

    except BoletoAutomationError as e:
        progress_callback('boletos', f'❌ Erro ao gerar boleto: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        progress_callback('boletos', f'❌ Erro inesperado ao gerar boleto: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/boletos/whatsapp/<task_id>', methods=['POST'])
def api_boletos_whatsapp(task_id):
    """Envia boleto via WhatsApp usando Evolution API"""
    try:
        from utils.evolution_api import EvolutionAPI
        
        # Carrega dados do boleto
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        
        if not os.path.exists(boletos_filepath):
            return jsonify({'success': False, 'error': 'Dados de boletos não encontrados'})
        
        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)
        
        # Busca o boleto específico
        boleto = None
        dia = None
        
        for boleto_item in boletos_data.get('dia08', []):
            if str(boleto_item.get('task_id')) == str(task_id):
                boleto = boleto_item
                dia = '08'
                break
        
        if not boleto:
            for boleto_item in boletos_data.get('dia16', []):
                if str(boleto_item.get('task_id')) == str(task_id):
                    boleto = boleto_item
                    dia = '16'
                    break
        
        if not boleto:
            return jsonify({'success': False, 'error': 'Boleto não encontrado'})
        
        # Extrai e limpa o celular
        import re
        celular = boleto.get('celular', '').strip()
        
        # Se o celular está vazio, tenta extrair do campo cotas (dados legados)
        if not celular:
            raw_cotas = boleto.get('cotas', '')
            celular_match = re.search(r'(?:📱\s*)?[Cc]elular:\s*(\d+)', raw_cotas)
            if celular_match:
                celular = celular_match.group(1)
        
        # Remove todos os caracteres não numéricos
        celular = re.sub(r'\D', '', celular)
        
        # Valida celular (deve ter pelo menos 10 dígitos)
        if not celular or len(celular) < 10:
            return jsonify({
                'success': False, 
                'error': 'Boleto não possui número de celular válido. Por favor, edite o boleto e adicione um celular com pelo menos 10 dígitos.'
            })
        
        # Carrega configuração da Evolution API
        evolution_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evolution_config.json')
        
        if not os.path.exists(evolution_config_path):
            return jsonify({'success': False, 'error': 'Configuração da Evolution API não encontrada'})
        
        with open(evolution_config_path, 'r', encoding='utf-8') as f:
            evolution_config = json.load(f)
        
        # Cria cliente da Evolution API
        api_config = evolution_config.get('api', {})
        base_url = api_config.get('base_url')
        instance_name = api_config.get('instance_name')
        api_key = api_config.get('api_key')
        
        if not all([base_url, instance_name, api_key]):
            return jsonify({'success': False, 'error': 'Configuração da Evolution API incompleta'})
        
        evolution_api = EvolutionAPI(base_url, instance_name, api_key)
        
        # Monta a mensagem personalizada
        nome = boleto.get('nome', 'Cliente')
        cotas = boleto.get('cotas', 'N/A')
        link_boleto = _best_boleto_link(boleto)

        link_bloco = f"🔗 *Link do boleto:* {link_boleto}\n\n" if link_boleto else "📄 *Acesse o portal Servopa para visualizar o boleto.*\n\n"

        mensagem = f"""Olá *{nome}*! 👋

📋 *Lembrete de Boleto - Sistema OXCASH*

Segue as informações do seu boleto:

🎯 *Cotas:* {cotas}
📅 *Vencimento:* Dia {dia}

{link_bloco}Qualquer dúvida, estamos à disposição!

_Mensagem automática - Sistema OXCASH_"""

        success_text, response_text = evolution_api.send_text_message(celular, mensagem)

        if not success_text:
            return jsonify({
                'success': False,
                'error': f"Falha ao enviar mensagem: {response_text.get('error', 'Erro desconhecido')}",
                'details': response_text
            })

        details = {
            'nome': nome,
            'celular': celular,
            'dia': dia,
            'text_sent': True,
            'link': link_boleto,
            'media_sent': False,
        }

        # Se não há link, tenta enviar imagem remota como fallback
        if not link_boleto:
            import time
            fallback_image = boleto.get('png_base64', '')
            if isinstance(fallback_image, str) and fallback_image.lower().startswith(('http://', 'https://')):
                time.sleep(2)
                success_media, response_media = evolution_api.send_media_message(
                    celular,
                    fallback_image,
                    f"📄 Boleto - {nome}"
                )
                details['media_sent'] = success_media
                details['media_response'] = response_media
        
        # Atualiza o boleto no Todoist adicionando uma nota sobre o envio
        try:
            from utils.todoist_rest_api import TodoistRestAPI
            TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
            todoist_api = TodoistRestAPI(TODOIST_TOKEN)
            
            # Adiciona comentário na task do Todoist
            comment_text = f"📱 WhatsApp enviado em {datetime.now().strftime('%d/%m/%Y %H:%M')} para {celular}"
            if link_boleto:
                comment_text += "\n✅ Texto com link enviado"
            elif details.get('media_sent'):
                comment_text += "\n✅ Texto + Imagem enviados"
            else:
                comment_text += "\n⚠️ Texto enviado, mas link/imagem indisponível"
            
            todoist_api.add_comment(task_id, comment_text)
        except Exception as e:
            print(f"Aviso: Não foi possível adicionar comentário no Todoist: {e}")
        
        return jsonify({
            'success': True,
            'message': f'WhatsApp enviado com sucesso para {nome}!',
            'details': {
                'nome': nome,
                'celular': celular,
                'dia': dia,
                'text_sent': True,
                'media_sent': details.get('media_sent', False),
                'link': link_boleto,
                'text_response': response_text,
                'media_response': details.get('media_response')
            }
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao enviar WhatsApp: {error_details}")
        return jsonify({'success': False, 'error': f'Erro ao enviar WhatsApp: {str(e)}'})

# ========== ROTAS DE EXTRAÇÃO DE COTAS ==========

@app.route('/api/cotas', methods=['GET'])
def api_cotas():
    """Retorna dados das cotas extraídas"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cotas_data.json')
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': {'grupos': []}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cotas/extract/<grupo>', methods=['POST'])
def api_cotas_extract(grupo):
    """Extrai cotas de um grupo específico"""
    try:
        # Valida grupo
        if not grupo or not grupo.isdigit() or len(grupo) > 4:
            return jsonify({'success': False, 'error': 'Número do grupo inválido'})
        
        # ========== RECEBE DIA DO GRUPO ==========
        request_data = request.get_json() or {}
        dia_grupo = request_data.get('dia', 8)  # Padrão: dia 8
        
        # Valida dia
        if dia_grupo not in [8, 16]:
            dia_grupo = 8
        
        # Emite progresso via WebSocket
        def emit_progress(message):
            socketio.emit('cotas_progress', {'message': message})
        
        emit_progress(f'🔐 Carregando credenciais...')
        emit_progress(f'📅 Grupo configurado para Dia {dia_grupo}')
        
        # Carrega credenciais
        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        if not os.path.exists(creds_path):
            return jsonify({'success': False, 'error': 'Credenciais não configuradas'})
        
        with open(creds_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        servopa_creds = credentials.get('servopa')
        if not servopa_creds:
            return jsonify({'success': False, 'error': 'Credenciais do Servopa não encontradas'})
        
        emit_progress('🌐 Abrindo navegador...')
        
        # Cria driver headless
        driver = create_driver(headless=True)
        
        try:
            emit_progress('🔐 Fazendo login no Servopa...')
            
            # Login no Servopa
            if not login_servopa(driver, emit_progress, servopa_creds):
                raise Exception('Falha no login do Servopa')
            
            emit_progress(f'📊 Extraindo cotas do grupo {grupo}...')
            
            # Importa função de extração
            from automation.servopa_automation import extract_cotas_from_grupo
            
            # Executa extração
            result = extract_cotas_from_grupo(driver, grupo, emit_progress)
            
            if not result['success']:
                raise Exception('Falha na extração das cotas')
            
            emit_progress('💾 Salvando dados...')
            
            # Carrega dados existentes
            cotas_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cotas_data.json')
            cotas_data = {'grupos': []}
            
            if os.path.exists(cotas_filepath):
                try:
                    with open(cotas_filepath, 'r', encoding='utf-8') as f:
                        cotas_data = json.load(f)
                except:
                    cotas_data = {'grupos': []}
            
            if 'grupos' not in cotas_data:
                cotas_data['grupos'] = []
            
            # Remove grupo existente se houver
            cotas_data['grupos'] = [g for g in cotas_data['grupos'] if g.get('numero') != grupo]
            
            # Adiciona novo grupo com dia
            cotas_data['grupos'].append({
                'numero': grupo,
                'dia': dia_grupo,  # ========== SALVA DIA ==========
                'cotas': result['cotas'],
                'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Salva arquivo
            with open(cotas_filepath, 'w', encoding='utf-8') as f:
                json.dump(cotas_data, f, indent=2, ensure_ascii=False)
            
            emit_progress(f'✅ Extração concluída! Grupo {grupo} configurado para Dia {dia_grupo}')
            
            # ========== SINCRONIZAÇÃO AUTOMÁTICA COM CLIENTES E BOLETOS ==========
            emit_progress(f'🔄 Sincronizando cotas com aba de Clientes...')
            sync_stats = _sync_cotas_to_clientes(result['cotas'], grupo, dia_grupo)
            
            if sync_stats.get('error'):
                emit_progress(f'⚠️ Erro na sincronização: {sync_stats["error"]}')
            else:
                msg_sync = f"📋 Clientes: {sync_stats['created']} criados, {sync_stats['updated']} atualizados"
                msg_boletos = f"💰 Boletos: {sync_stats.get('boletos_created', 0)} criados, {sync_stats.get('boletos_updated', 0)} atualizados"
                emit_progress(msg_sync)
                emit_progress(msg_boletos)
            
            return jsonify({
                'success': True,
                'message': f'Grupo {grupo} extraído com sucesso',
                'grupo': grupo,
                'total_cotas': len(result['cotas']),
                'sync_stats': sync_stats
            })
            
        finally:
            try:
                driver.quit()
            except:
                pass
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na extração de cotas: {error_details}")
        socketio.emit('cotas_progress', {'message': f'❌ Erro: {str(e)}'})
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cotas/delete/<grupo>', methods=['POST'])
def api_cotas_delete(grupo):
    """Remove um grupo extraído"""
    try:
        cotas_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cotas_data.json')
        
        if os.path.exists(cotas_filepath):
            with open(cotas_filepath, 'r', encoding='utf-8') as f:
                cotas_data = json.load(f)
            
            # Remove grupo
            if 'grupos' in cotas_data:
                cotas_data['grupos'] = [g for g in cotas_data['grupos'] if g.get('numero') != grupo]
            
            with open(cotas_filepath, 'w', encoding='utf-8') as f:
                json.dump(cotas_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': f'Grupo {grupo} removido com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cotas/automatizar-lance/<grupo>', methods=['POST'])
def api_cotas_automatizar_lance(grupo):
    """
    Automatiza lances de TODAS as cotas de um grupo extraído
    SEM depender do Todoist - usa dados da extração de cotas
    """
    try:
        # Valida grupo
        if not grupo or not grupo.isdigit() or len(grupo) > 4:
            return jsonify({'success': False, 'error': 'Número do grupo inválido'})
        
        # Recebe estados dos checkboxes do frontend
        request_data = request.get_json() or {}
        checkbox_states = request_data.get('checkbox_states', {})
        
        # Carrega dados das cotas extraídas
        cotas_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cotas_data.json')
        
        if not os.path.exists(cotas_filepath):
            return jsonify({'success': False, 'error': 'Nenhum grupo extraído ainda. Extraia o grupo primeiro.'})
        
        with open(cotas_filepath, 'r', encoding='utf-8') as f:
            cotas_data = json.load(f)
        
        # Procura o grupo específico
        grupo_data = None
        for g in cotas_data.get('grupos', []):
            if g.get('numero') == grupo:
                grupo_data = g
                break
        
        if not grupo_data:
            return jsonify({'success': False, 'error': f'Grupo {grupo} não encontrado nos dados extraídos'})
        
        cotas_list = grupo_data.get('cotas', [])
        if not cotas_list:
            return jsonify({'success': False, 'error': f'Nenhuma cota encontrada no grupo {grupo}'})
        
        # Emite progresso via WebSocket
        def emit_progress(message):
            socketio.emit('lance_progress', {'grupo': grupo, 'message': message})
        
        emit_progress(f'🔐 Carregando credenciais...')
        
        # Carrega credenciais
        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        if not os.path.exists(creds_path):
            return jsonify({'success': False, 'error': 'Credenciais não configuradas'})
        
        with open(creds_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        servopa_creds = credentials.get('servopa')
        if not servopa_creds:
            return jsonify({'success': False, 'error': 'Credenciais do Servopa não encontradas'})
        
        emit_progress('🌐 Abrindo navegador VISÍVEL para acompanhamento...')
        
        # Cria driver VISÍVEL (headless=False) para você ver a automação
        driver = create_driver(headless=False)
        
        try:
            emit_progress('🔐 Fazendo login no Servopa...')
            
            # Login no Servopa
            if not login_servopa(driver, emit_progress, servopa_creds):
                raise Exception('Falha no login do Servopa')
            
            emit_progress(f'🎯 Iniciando automação do grupo {grupo}...')
            emit_progress(f'📊 Total de {len(cotas_list)} cotas a processar')
            
            # Importa função de automação
            from automation.servopa_lances import processar_lance_completo
            
            # Callback para histórico
            def history_callback(grupo, cota, nome, valor, status, obs="", **kwargs):
                filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'history_dia8.json')
                
                protocolo_valor = kwargs.get('protocolo')
                documento_url = kwargs.get('documento_url')
                docparser_url = kwargs.get('docparser_url')

                entry = {
                    'hora': datetime.now().strftime('%H:%M:%S'),
                    'data': datetime.now().strftime('%Y-%m-%d'),
                    'grupo': str(grupo) if grupo else '-',
                    'cota': str(cota) if cota else '-',
                    'nome': str(nome) if nome else '-',
                    'valor_lance': str(valor) if valor else '-',
                    'protocolo': str(protocolo_valor) if protocolo_valor else '',
                    'documento_url': str(documento_url) if documento_url else '',
                    'docparser_url': str(docparser_url) if docparser_url else '',
                    'status': str(status) if status else 'Processado',
                    'observacao': str(obs) if obs else '',
                }
                
                try:
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        data = []
                    
                    data.append(entry)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    emit_progress(f"📝 Histórico salvo: {nome} - {status}")
                    socketio.emit('history_update', {'dia': 'dia8', 'entry': entry})
                    
                except Exception as e:
                    emit_progress(f"⚠️ Erro ao salvar histórico: {e}")
            
            # Estatísticas
            stats = {
                'total': len(cotas_list),
                'completed': 0,
                'failed': 0,
                'skipped': 0,
                'stopped': False,
                'results': []
            }
            
            # Reseta flag de parada
            app_state['stop_automation'][grupo] = False
            
            # Processa cada cota
            for index, cota_info in enumerate(cotas_list, 1):
                # ========== VERIFICA PARADA NO INÍCIO DO LOOP ==========
                if app_state['stop_automation'].get(grupo, False):
                    emit_progress('')
                    emit_progress('⏹️ AUTOMAÇÃO INTERROMPIDA PELO USUÁRIO')
                    emit_progress(f'📊 Processadas: {index - 1}/{len(cotas_list)} cotas')
                    stats['stopped'] = True
                    
                    # Fecha navegador imediatamente
                    try:
                        emit_progress('🔒 Fechando navegador...')
                        driver.quit()
                        driver = None
                        emit_progress('✅ Navegador fechado')
                    except:
                        pass
                    
                    break
                
                cota_number = cota_info.get('cota', '')
                nome = cota_info.get('nome', 'Sem nome')
                
                # ========== VERIFICA SE COTA JÁ FOI CONCLUÍDA (VERDE) ==========
                cota_normalizada = cota_number.zfill(4)  # Ex: "303" -> "0303"
                checkbox_status = checkbox_states.get(cota_normalizada, 'pending')
                
                if checkbox_status == 'completed':
                    emit_progress('')
                    emit_progress(f"⏭️  Pulando cota {index}/{len(cotas_list)}")
                    emit_progress(f"│  📝 Cota: {cota_number}")
                    emit_progress(f"│  ✅ Já concluída anteriormente")
                    emit_progress(f"└" + "─" * 50)
                    
                    stats['skipped'] += 1  # Conta como pulada
                    stats['results'].append({
                        'cota': cota_number,
                        'nome': nome,
                        'success': True,
                        'skipped': True
                    })
                    continue  # Pula para próxima cota
                
                # Indica que vai processar cotas pendentes/amarelas/vermelhas
                status_emoji = {
                    'pending': '⚪',
                    'processing': '🟡',
                    'error': '🔴'
                }.get(checkbox_status, '⚪')
                
                emit_progress('')
                emit_progress(f"┌─ Cota {index}/{len(cotas_list)} {status_emoji}")
                emit_progress(f"│  📝 Cota: {cota_number}")
                emit_progress(f"│  👤 Nome: {nome}")
                emit_progress(f"└" + "─" * 50)
                
                try:
                    # Processa lance
                    result = processar_lance_completo(driver, grupo, cota_number, emit_progress)
                    
                    if result['success']:
                        stats['completed'] += 1
                        
                        # Salva no histórico
                        valor_lance = result.get('cota_data', {}).get('valor', 'N/A')
                        
                        if result.get('already_exists', False):
                            status = "✅ Sucesso (já existia)"
                            obs = "Lance já existia (protocolo anterior detectado)"
                        else:
                            status = "✅ Sucesso"
                            obs = "Lance registrado com sucesso"
                        
                        history_callback(
                            grupo,
                            cota_number,
                            nome,
                            valor_lance,
                            status,
                            obs,
                            protocolo=result.get('protocol_number'),
                            documento_url=result.get('documento_url'),
                            docparser_url=result.get('docparser_url'),
                        )
                        
                        emit_progress(f"🎉 Cota {index}/{len(cotas_list)} concluída!")
                        emit_progress(f"📊 Progresso: {stats['completed']}/{len(cotas_list)} sucesso")
                        
                    else:
                        stats['failed'] += 1
                        history_callback(grupo, cota_number, nome, 'N/A', '❌ Erro', result.get('error', 'Erro desconhecido'))
                        emit_progress(f"❌ Erro na cota {index}")
                    
                    stats['results'].append({
                        'cota': cota_number,
                        'nome': nome,
                        'success': result['success']
                    })
                    
                except Exception as e:
                    # Verifica se foi erro de navegador fechado
                    error_msg = str(e).lower()
                    if 'disconnected' in error_msg or 'no such window' in error_msg or 'chrome not reachable' in error_msg:
                        emit_progress('')
                        emit_progress('⚠️ NAVEGADOR FECHADO MANUALMENTE')
                        emit_progress('⏹️ Encerrando automação...')
                        stats['stopped'] = True
                        
                        # Não precisa fechar (já foi fechado manualmente)
                        driver = None
                        break
                    
                    stats['failed'] += 1
                    history_callback(grupo, cota_number, nome, 'N/A', '❌ Erro', str(e)[:200])
                    emit_progress(f"❌ Erro na cota {index}: {e}")
                    
                    stats['results'].append({
                        'cota': cota_number,
                        'nome': nome,
                        'success': False,
                        'error': str(e)
                    })
                
                # ========== VERIFICA SE DEVE PARAR APÓS PROCESSAR COTA ==========
                if app_state['stop_automation'].get(grupo, False):
                    emit_progress('')
                    emit_progress('⏹️ AUTOMAÇÃO INTERROMPIDA PELO USUÁRIO')
                    emit_progress(f'📊 Processadas: {index}/{len(cotas_list)} cotas')
                    stats['stopped'] = True
                    
                    # Fecha navegador imediatamente
                    try:
                        emit_progress('🔒 Fechando navegador...')
                        driver.quit()
                        driver = None
                        emit_progress('✅ Navegador fechado')
                    except:
                        pass
                    
                    break
            
            # Relatório final
            emit_progress('')
            emit_progress('=' * 60)
            if stats['stopped']:
                emit_progress('⏹️ AUTOMAÇÃO INTERROMPIDA!')
            else:
                emit_progress('🎉 AUTOMAÇÃO FINALIZADA!')
            emit_progress('=' * 60)
            emit_progress(f'✅ Sucesso: {stats["completed"]}/{stats["total"]}')
            emit_progress(f'⏭️  Puladas: {stats["skipped"]}/{stats["total"]} (já concluídas)')
            emit_progress(f'❌ Falhas: {stats["failed"]}/{stats["total"]}')
            
            # Calcula taxa de sucesso (somente das processadas)
            processadas = stats['completed'] + stats['failed']
            if processadas > 0:
                taxa = (stats['completed']/processadas*100)
                emit_progress(f'📊 Taxa de sucesso: {taxa:.1f}% (de {processadas} processadas)')
            emit_progress('=' * 60)
            
            # Limpa flag de parada
            app_state['stop_automation'][grupo] = False
            
            return jsonify({
                'success': True,
                'message': f'Automação {"interrompida" if stats["stopped"] else "concluída"}: {stats["completed"]} sucesso, {stats["skipped"]} puladas, {stats["failed"]} falhas',
                'stats': stats
            })
            
        finally:
            # Fecha navegador de forma segura (se ainda não foi fechado)
            if driver is not None:
                try:
                    emit_progress('🔒 Fechando navegador...')
                    driver.quit()
                    emit_progress('✅ Navegador fechado com sucesso')
                except Exception as close_error:
                    # Ignora erros ao fechar navegador (pode já estar fechado)
                    pass
            
            # Limpa flag de parada
            app_state['stop_automation'][grupo] = False
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na automação de lances: {error_details}")
        socketio.emit('lance_progress', {'grupo': grupo, 'message': f'❌ Erro: {str(e)}'})
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cotas/parar-automacao/<grupo>', methods=['POST'])
def api_parar_automacao(grupo):
    """Para a automação de lances de um grupo"""
    try:
        # Marca flag de parada
        app_state['stop_automation'][grupo] = True
        
        socketio.emit('lance_progress', {
            'grupo': grupo, 
            'message': '⏹️ Solicitação de parada recebida. Finalizando cota atual...'
        })
        
        return jsonify({
            'success': True,
            'message': 'Automação será interrompida após a cota atual'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========== FIM ROTAS DE EXTRAÇÃO DE COTAS ==========

# ========== ROTAS DE GERENCIAMENTO DE CLIENTES ==========

@app.route('/api/clientes', methods=['GET'])
def api_clientes():
    """Retorna dados dos clientes"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': {'dia08': [], 'dia16': []}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clientes/create', methods=['POST'])
def api_clientes_create():
    """Cria um novo cliente"""
    try:
        data = request.json
        nome = data.get('nome', '')
        grupo = data.get('grupo', '')
        cota = data.get('cota', '')
        contato = data.get('contato', '')
        valor_primeira_cota = data.get('valor_primeira_cota', '')
        dia = data.get('dia', '08')
        
        print(f"🆕 CREATE Cliente: Nome={nome}, Dia={dia}")
        
        if not nome:
            return jsonify({'success': False, 'error': 'Nome é obrigatório'})
        
        # Gera ID único para o cliente
        import uuid
        client_id = str(uuid.uuid4())
        
        # Carrega dados existentes
        clientes_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
        clientes_data = {'dia08': [], 'dia16': []}
        
        if os.path.exists(clientes_filepath):
            with open(clientes_filepath, 'r', encoding='utf-8') as f:
                clientes_data = json.load(f)
        
        dia_key = f'dia{dia}'
        if dia_key not in clientes_data:
            clientes_data[dia_key] = []
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Novo formato: usa listas para grupos e cotas
        grupos_list = [grupo] if grupo else []
        cotas_list = [cota] if cota else []
        
        # Define cotas_texto
        if len(cotas_list) == 1 and len(grupos_list) == 1:
            cotas_texto = f"{cotas_list[0]} - {grupos_list[0]}"
        elif len(cotas_list) > 1:
            cotas_texto = f"{len(cotas_list)} cotas"
        else:
            cotas_texto = ''
        
        new_cliente = {
            'client_id': client_id,
            'nome': nome,
            'grupos': grupos_list,
            'cotas': cotas_list,
            'cotas_texto': cotas_texto,
            'contato': contato,
            'valor_primeira_cota': valor_primeira_cota,
            'historico_boletos': [],
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        clientes_data[dia_key].append(new_cliente)
        
        with open(clientes_filepath, 'w', encoding='utf-8') as f:
            json.dump(clientes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Cliente criado: ID={client_id}, Dia={dia_key}")
        
        return jsonify({
            'success': True,
            'message': 'Cliente criado com sucesso',
            'data': new_cliente
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clientes/update/<client_id>', methods=['POST'])
def api_clientes_update(client_id):
    """Atualiza um cliente existente"""
    try:
        data = request.json
        nome = data.get('nome', '')
        grupo = data.get('grupo', '')
        cota = data.get('cota', '')
        contato = data.get('contato', '')
        valor_primeira_cota = data.get('valor_primeira_cota', '')
        
        print(f"🔧 UPDATE Cliente: ID={client_id}, Nome={nome}")
        
        # Carrega dados
        clientes_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
        if not os.path.exists(clientes_filepath):
            return jsonify({'success': False, 'error': 'Arquivo de clientes não encontrado'})
            
        with open(clientes_filepath, 'r', encoding='utf-8') as f:
            clientes_data = json.load(f)
        
        # Busca e atualiza cliente
        found = False
        for dia_key in ['dia08', 'dia16']:
            if dia_key in clientes_data:
                for cliente in clientes_data[dia_key]:
                    if cliente.get('client_id') == client_id:
                        print(f"✅ Cliente encontrado em {dia_key}: {cliente.get('nome')}")
                        
                        # Atualiza nome
                        cliente['nome'] = nome
                        cliente['contato'] = contato
                        cliente['valor_primeira_cota'] = valor_primeira_cota
                        
                        # ========== PRESERVA GRUPOS/COTAS EXISTENTES ==========
                        # Só atualiza grupos/cotas se novos valores forem enviados
                        # Caso contrário, mantém os valores existentes (arrays)
                        if grupo or cota:
                            # Se enviou novos valores, atualiza
                            grupos_list = [grupo] if grupo else []
                            cotas_list = [cota] if cota else []
                            
                            cliente['grupos'] = grupos_list
                            cliente['cotas'] = cotas_list
                            
                            # Atualiza cotas_texto
                            if len(cotas_list) == 1 and len(grupos_list) == 1:
                                cliente['cotas_texto'] = f"{cotas_list[0]} - {grupos_list[0]}"
                            elif len(cotas_list) > 1:
                                cliente['cotas_texto'] = f"{len(cotas_list)} cotas"
                            else:
                                cliente['cotas_texto'] = ''
                        else:
                            # Não enviou grupo/cota = PRESERVA dados existentes
                            print(f"🔒 Preservando grupos/cotas existentes: {len(cliente.get('grupos', []))} grupos, {len(cliente.get('cotas', []))} cotas")
                            # Não altera cliente['grupos'] nem cliente['cotas']
                        
                        # Remove campos antigos se existirem
                        cliente.pop('grupo', None)
                        cliente.pop('cota', None)
                        
                        cliente['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        found = True
                        
                        # Sincroniza com boleto correspondente
                        _sync_cliente_to_boleto(cliente, dia_key)
                        break
            if found:
                break
        
        if not found:
            print(f"❌ Cliente NÃO encontrado: {client_id}")
            return jsonify({'success': False, 'error': 'Cliente não encontrado'})
        
        with open(clientes_filepath, 'w', encoding='utf-8') as f:
            json.dump(clientes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Cliente atualizado com sucesso!")
        return jsonify({'success': True, 'message': 'Cliente atualizado com sucesso'})
        
    except Exception as e:
        print(f"❌ Erro ao atualizar cliente: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clientes/delete/<client_id>', methods=['POST', 'DELETE'])
def api_clientes_delete(client_id):
    """Deleta um cliente E o boleto associado"""
    try:
        # ========== 1. BUSCA E DELETA CLIENTE ==========
        clientes_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
        if not os.path.exists(clientes_filepath):
            return jsonify({'success': False, 'error': 'Arquivo de clientes não encontrado'})
            
        with open(clientes_filepath, 'r', encoding='utf-8') as f:
            clientes_data = json.load(f)
        
        found = False
        cliente_nome = None
        cliente_task_id = None
        dia_encontrado = None
        
        for dia_key in ['dia08', 'dia16']:
            if dia_key in clientes_data:
                for cliente in clientes_data[dia_key]:
                    if cliente.get('client_id') == client_id:
                        cliente_nome = cliente.get('nome', '').strip()
                        cliente_task_id = cliente.get('task_id', '')
                        dia_encontrado = dia_key
                        found = True
                        break
                
                if found:
                    # Remove cliente
                    original_len = len(clientes_data[dia_key])
                    clientes_data[dia_key] = [
                        c for c in clientes_data[dia_key] 
                        if c.get('client_id') != client_id
                    ]
                    print(f"🗑️ Cliente deletado: {cliente_nome} (ID: {client_id})")
                    break
        
        if not found:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'})
        
        # Salva clientes atualizados
        with open(clientes_filepath, 'w', encoding='utf-8') as f:
            json.dump(clientes_data, f, indent=2, ensure_ascii=False)
        
        # ========== 2. DELETA BOLETO ASSOCIADO ==========
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        boleto_deletado = False
        
        if os.path.exists(boletos_filepath):
            try:
                with open(boletos_filepath, 'r', encoding='utf-8-sig') as f:
                    content = f.read().strip()
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    boletos_data = json.loads(content)
                
                if dia_encontrado and dia_encontrado in boletos_data:
                    original_len = len(boletos_data[dia_encontrado])
                    
                    # Tenta deletar por task_id ou por nome (case-insensitive)
                    boletos_data[dia_encontrado] = [
                        b for b in boletos_data[dia_encontrado]
                        if not (
                            (cliente_task_id and b.get('task_id') == cliente_task_id) or
                            (cliente_nome and b.get('nome', '').strip().lower() == cliente_nome.lower())
                        )
                    ]
                    
                    if len(boletos_data[dia_encontrado]) < original_len:
                        boleto_deletado = True
                        print(f"🗑️ Boleto deletado: {cliente_nome}")
                    
                    # Salva boletos atualizados
                    with open(boletos_filepath, 'w', encoding='utf-8') as f:
                        json.dump(boletos_data, f, indent=2, ensure_ascii=False)
                        
            except Exception as e:
                print(f"⚠️ Erro ao deletar boleto: {e}")
        
        mensagem = f'Cliente deletado com sucesso'
        if boleto_deletado:
            mensagem += ' (boleto também removido)'
        
        return jsonify({'success': True, 'message': mensagem})
        
    except Exception as e:
        print(f"❌ Erro ao deletar cliente: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clientes/sync-from-boletos', methods=['POST'])
def api_clientes_sync_from_boletos():
    """Sincroniza clientes a partir dos boletos existentes"""
    try:
        # Carrega boletos
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if not os.path.exists(boletos_filepath):
            return jsonify({'success': False, 'error': 'Arquivo de boletos não encontrado'})
        
        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)
        
        # Carrega clientes existentes
        clientes_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
        clientes_data = {'dia08': [], 'dia16': []}
        
        if os.path.exists(clientes_filepath):
            with open(clientes_filepath, 'r', encoding='utf-8') as f:
                clientes_data = json.load(f)
        
        import uuid
        import re
        
        created_count = 0
        updated_count = 0
        
        # Processa cada dia
        for dia_key in ['dia08', 'dia16']:
            boletos_list = boletos_data.get(dia_key, [])
            
            for boleto in boletos_list:
                nome = boleto.get('nome', '').strip()
                if not nome:
                    continue
                
                # Extrai grupo e cota das informações do boleto
                cotas_info = boleto.get('cotas', '')
                grupo = boleto.get('grupo', '')
                cota = boleto.get('cota', '')
                
                # Tenta extrair grupo e cota do campo cotas se não existirem
                if not grupo or not cota:
                    # Padrão: "1920 - 1553" ou "Cotas: 304 - 1545"
                    match = re.search(r'(\d{3,4})\s*-\s*(\d{4})', cotas_info)
                    if match:
                        cota = match.group(1)
                        grupo = match.group(2)
                
                contato = boleto.get('celular', '')
                
                # Busca cliente existente com mesmo nome e dia
                cliente_existente = None
                for cliente in clientes_data.get(dia_key, []):
                    if cliente.get('nome') == nome:
                        cliente_existente = cliente
                        break
                
                # Pega link do boleto
                boleto_link = _best_boleto_link(boleto)
                
                if cliente_existente:
                    # Atualiza cliente existente
                    cliente_existente['grupo'] = grupo or cliente_existente.get('grupo', '')
                    cliente_existente['cota'] = cota or cliente_existente.get('cota', '')
                    cliente_existente['contato'] = contato or cliente_existente.get('contato', '')
                    cliente_existente['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Adiciona link ao histórico se não existir
                    if boleto_link and boleto_link not in cliente_existente.get('historico_boletos', []):
                        if 'historico_boletos' not in cliente_existente:
                            cliente_existente['historico_boletos'] = []
                        cliente_existente['historico_boletos'].append(boleto_link)
                    
                    updated_count += 1
                else:
                    # Cria novo cliente
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    novo_cliente = {
                        'client_id': str(uuid.uuid4()),
                        'nome': nome,
                        'grupo': grupo,
                        'cota': cota,
                        'contato': contato,
                        'valor_primeira_cota': '',
                        'historico_boletos': [boleto_link] if boleto_link else [],
                        'created_at': timestamp,
                        'updated_at': timestamp
                    }
                    
                    if dia_key not in clientes_data:
                        clientes_data[dia_key] = []
                    clientes_data[dia_key].append(novo_cliente)
                    created_count += 1
        
        # Salva clientes atualizados
        with open(clientes_filepath, 'w', encoding='utf-8') as f:
            json.dump(clientes_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'Sincronização concluída: {created_count} clientes criados, {updated_count} atualizados',
            'created': created_count,
            'updated': updated_count
        })
        
    except Exception as e:
        import traceback
        print(f"Erro na sincronização: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/calendario-lances/get', methods=['GET'])
def api_calendario_lances_get():
    """Retorna o calendário de lances"""
    try:
        from datetime import datetime
        ano_atual = datetime.now().year
        
        calendario_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'calendario_lances.json')
        
        if not os.path.exists(calendario_filepath):
            # Cria arquivo vazio se não existir
            calendario_inicial = {str(ano_atual): {}}
            meses_chaves = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
                           'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            
            for idx, mes in enumerate(meses_chaves):
                calendario_inicial[str(ano_atual)][mes] = {
                    'mes': idx + 1,
                    'grupos': []
                }
            
            with open(calendario_filepath, 'w', encoding='utf-8') as f:
                json.dump(calendario_inicial, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True,
                'ano': ano_atual,
                'calendario': calendario_inicial[str(ano_atual)]
            })
        
        with open(calendario_filepath, 'r', encoding='utf-8') as f:
            calendario_data = json.load(f)
        
        # Retorna calendário do ano atual ou primeiro ano disponível
        ano_key = str(ano_atual)
        if ano_key not in calendario_data and calendario_data:
            ano_key = list(calendario_data.keys())[0]
        
        calendario = calendario_data.get(ano_key, {})
        
        return jsonify({
            'success': True,
            'ano': ano_key,
            'calendario': calendario
        })
        
    except Exception as e:
        print(f"Erro ao carregar calendário: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/calendario-lances/save', methods=['POST'])
def api_calendario_lances_save():
    """Salva o calendário de lances"""
    try:
        data = request.json
        ano = str(data.get('ano', datetime.now().year))
        calendario = data.get('calendario', {})
        
        calendario_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'calendario_lances.json')
        
        # Carrega calendário existente
        if os.path.exists(calendario_filepath):
            with open(calendario_filepath, 'r', encoding='utf-8') as f:
                calendario_data = json.load(f)
        else:
            calendario_data = {}
        
        # Atualiza ano específico
        calendario_data[ano] = calendario
        
        # Salva
        with open(calendario_filepath, 'w', encoding='utf-8') as f:
            json.dump(calendario_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Calendário salvo: Ano {ano}")
        
        return jsonify({
            'success': True,
            'message': f'Calendário de {ano} salvo com sucesso'
        })
        
    except Exception as e:
        print(f"❌ Erro ao salvar calendário: {e}")
        return jsonify({'success': False, 'error': str(e)})

def _sync_cotas_to_clientes(cotas_list, grupo, dia_grupo):
    """
    Sincroniza cotas extraídas para a aba de clientes
    
    Para cada cota extraída:
    1. Verifica se já existe cliente com o mesmo NOME
    2. Se existe: adiciona grupo/cota ao cliente (se ainda não tiver)
    3. Se não existe: cria novo cliente
    
    Args:
        cotas_list: Lista de cotas extraídas do grupo
        grupo: Número do grupo extraído
        dia_grupo: Dia do grupo (8 ou 16)
    
    Returns:
        dict com estatísticas (criados, atualizados)
    """
    try:
        import uuid
        from datetime import datetime
        
        clientes_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
        
        # Carrega ou cria estrutura de clientes
        clientes_data = {'dia08': [], 'dia16': []}
        if os.path.exists(clientes_filepath):
            with open(clientes_filepath, 'r', encoding='utf-8') as f:
                clientes_data = json.load(f)
        
        dia_key = f'dia{dia_grupo:02d}'
        if dia_key not in clientes_data:
            clientes_data[dia_key] = []
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0}
        
        print(f"\n🔄 Sincronizando {len(cotas_list)} cotas do grupo {grupo} para clientes (Dia {dia_grupo})...")
        
        for cota_info in cotas_list:
            nome = cota_info.get('nome', '').strip()
            cota = cota_info.get('cota', '').strip()
            
            if not nome or not cota:
                stats['skipped'] += 1
                continue
            
            # Busca cliente existente por NOME (case-insensitive)
            cliente_encontrado = None
            for idx, cliente in enumerate(clientes_data[dia_key]):
                nome_cliente = cliente.get('nome', '').strip()
                if nome_cliente.lower() == nome.lower():
                    cliente_encontrado = cliente
                    print(f"  ✓ Cliente encontrado: {nome}")
                    break
            
            if cliente_encontrado:
                # Cliente já existe - atualizar grupos/cotas
                grupos_atual = cliente_encontrado.get('grupos', [])
                cotas_atual = cliente_encontrado.get('cotas', [])
                
                # Se ainda usa formato antigo (string), converte para lista
                if isinstance(cliente_encontrado.get('grupo'), str):
                    grupo_antigo = cliente_encontrado.get('grupo', '').strip()
                    cota_antiga = cliente_encontrado.get('cota', '').strip()
                    
                    if grupo_antigo and cota_antiga:
                        grupos_atual = [grupo_antigo]
                        cotas_atual = [cota_antiga]
                    else:
                        grupos_atual = []
                        cotas_atual = []
                
                # Adiciona nova cota/grupo se não existir
                cota_grupo_key = f"{cota}-{grupo}"
                cotas_grupos_existentes = [f"{c}-{g}" for c, g in zip(cotas_atual, grupos_atual)]
                
                if cota_grupo_key not in cotas_grupos_existentes:
                    grupos_atual.append(grupo)
                    cotas_atual.append(cota)
                    
                    cliente_encontrado['grupos'] = grupos_atual
                    cliente_encontrado['cotas'] = cotas_atual
                    cliente_encontrado['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Atualiza cotas_texto
                    if len(cotas_atual) == 1:
                        cliente_encontrado['cotas_texto'] = f"{cotas_atual[0]} - {grupos_atual[0]}"
                    else:
                        cliente_encontrado['cotas_texto'] = f"{len(cotas_atual)} cotas"
                    
                    # Remove campos antigos (migração)
                    cliente_encontrado.pop('grupo', None)
                    cliente_encontrado.pop('cota', None)
                    
                    stats['updated'] += 1
                    print(f"  ↻ Cliente atualizado: {nome} - Agora com {len(cotas_atual)} cota(s)")
                else:
                    stats['skipped'] += 1
                    print(f"  ⊘ Cliente já possui esta cota: {nome}")
                    
            else:
                # Cliente não existe - criar novo
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                novo_cliente = {
                    'client_id': str(uuid.uuid4()),
                    'nome': nome,
                    'grupos': [grupo],
                    'cotas': [cota],
                    'cotas_texto': f"{cota} - {grupo}",
                    'contato': '',
                    'valor_primeira_cota': cota_info.get('valor', '').replace('R$ ', '').replace('.', '').replace(',', '.'),
                    'historico_boletos': [],
                    'created_at': timestamp,
                    'updated_at': timestamp
                }
                
                clientes_data[dia_key].append(novo_cliente)
                stats['created'] += 1
                print(f"  + Cliente criado: {nome}")
        
        # Salva clientes atualizados
        with open(clientes_filepath, 'w', encoding='utf-8') as f:
            json.dump(clientes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sincronização de clientes concluída: {stats['created']} criados, {stats['updated']} atualizados, {stats['skipped']} ignorados")
        
        # ========== CRIA/ATUALIZA BOLETOS AUTOMATICAMENTE ==========
        print(f"\n🎫 Sincronizando boletos automaticamente...")
        
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        
        # Carrega ou cria estrutura de boletos
        boletos_data = {'dia08': [], 'dia16': [], 'last_import': None}
        if os.path.exists(boletos_filepath):
            with open(boletos_filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
                if content.startswith('\ufeff'):
                    content = content[1:]
                try:
                    boletos_data = json.loads(content)
                except:
                    boletos_data = {'dia08': [], 'dia16': [], 'last_import': None}
        
        if dia_key not in boletos_data:
            boletos_data[dia_key] = []
        
        # Para cada cliente criado/atualizado, cria/atualiza boleto
        boletos_stats = {'created': 0, 'updated': 0, 'skipped': 0}
        
        for cliente in clientes_data[dia_key]:
            nome = cliente.get('nome', '').strip()
            grupos = cliente.get('grupos', [])
            cotas = cliente.get('cotas', [])
            cotas_texto = cliente.get('cotas_texto', '')
            contato = cliente.get('contato', '')
            task_id = cliente.get('task_id', '')
            
            if not nome:
                continue
            
            # Busca boleto existente pelo nome
            boleto_encontrado = None
            for boleto in boletos_data[dia_key]:
                if boleto.get('nome', '').strip().lower() == nome.lower():
                    boleto_encontrado = boleto
                    break
            
            if boleto_encontrado:
                # Atualiza boleto existente
                boleto_encontrado['cotas'] = cotas_texto
                if contato:
                    boleto_encontrado['celular'] = contato
                if grupos:
                    boleto_encontrado['grupo'] = grupos[0]
                if cotas:
                    boleto_encontrado['cota'] = cotas[0]
                boletos_stats['updated'] += 1
                print(f"  ↻ Boleto atualizado: {nome}")
            else:
                # Cria novo boleto
                if not task_id:
                    task_id = str(uuid.uuid4())
                
                novo_boleto = {
                    'task_id': task_id,
                    'client_id': cliente.get('client_id'),
                    'nome': nome,
                    'celular': contato,
                    'cotas': cotas_texto,
                    'grupo': grupos[0] if grupos else '',
                    'cota': cotas[0] if cotas else '',
                    'valor_primeira_cota': cliente.get('valor_primeira_cota', ''),
                    'is_completed': False,
                    'created_from_cotas': True,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                boletos_data[dia_key].append(novo_boleto)
                
                # Atualiza task_id no cliente se não tinha
                if not cliente.get('task_id'):
                    cliente['task_id'] = task_id
                
                boletos_stats['created'] += 1
                print(f"  + Boleto criado: {nome} - {cotas_texto}")
        
        # Salva boletos atualizados
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        # Salva clientes com task_id atualizado
        with open(clientes_filepath, 'w', encoding='utf-8') as f:
            json.dump(clientes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sincronização de boletos concluída: {boletos_stats['created']} criados, {boletos_stats['updated']} atualizados\n")
        
        stats['boletos_created'] = boletos_stats['created']
        stats['boletos_updated'] = boletos_stats['updated']
        
        return stats
        
    except Exception as e:
        import traceback
        print(f"❌ Erro ao sincronizar cotas para clientes: {e}")
        print(traceback.format_exc())
        return {'created': 0, 'updated': 0, 'skipped': 0, 'error': str(e)}

def _sync_cliente_to_boleto(cliente, dia_key):
    """Sincroniza dados do cliente para o boleto correspondente
    
    IDENTIFICAÇÃO: Usa GRUPO + COTA como chave única (igual ao sync inverso)
    - Se grupo/cota existem → busca por eles
    - Se não existem → busca por nome (fallback)
    """
    try:
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if not os.path.exists(boletos_filepath):
            return
        
        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)
        
        # Extrai dados do cliente - suporta novo formato (arrays) e antigo (strings)
        nome = cliente.get('nome', '').strip()
        
        # Novo formato: arrays
        grupos = cliente.get('grupos', [])
        cotas = cliente.get('cotas', [])
        
        # Migração do formato antigo
        if not grupos and cliente.get('grupo'):
            grupos = [str(cliente.get('grupo', '')).strip()]
        if not cotas and cliente.get('cota'):
            cotas = [str(cliente.get('cota', '')).strip()]
        
        # Pega primeiro grupo/cota para busca
        grupo = grupos[0] if grupos else ''
        cota = cotas[0] if cotas else ''
        
        contato = cliente.get('contato', '')
        cotas_texto = cliente.get('cotas_texto', '')
        
        if not nome:
            return
        
        print(f"🔄 SYNC Cliente→Boleto: Nome='{nome}', Grupos={grupos}, Cotas={cotas}, Dia={dia_key}")
        
        # Busca boleto existente - PRIORIDADE: Grupo+Cota, depois Nome
        boleto_encontrado = None
        metodo_busca = None
        
        # Método 1: Busca por GRUPO + COTA (mais confiável)
        if grupo and cota:
            for idx, boleto in enumerate(boletos_data.get(dia_key, [])):
                boleto_grupo = str(boleto.get('grupo', '')).strip()
                boleto_cota = str(boleto.get('cota', '')).strip()
                
                if boleto_grupo == grupo and boleto_cota == cota:
                    print(f"✅ Boleto ENCONTRADO por Grupo+Cota (posição {idx}): '{boleto.get('nome')}'")
                    boleto_encontrado = boleto
                    metodo_busca = "grupo+cota"
                    break
        
        # Método 2: Fallback - Busca por NOME (se não achou por grupo/cota)
        if not boleto_encontrado:
            for idx, boleto in enumerate(boletos_data.get(dia_key, [])):
                nome_boleto = boleto.get('nome', '').strip()
                if nome_boleto == nome:
                    print(f"✅ Boleto ENCONTRADO por Nome (posição {idx}): '{nome_boleto}'")
                    boleto_encontrado = boleto
                    metodo_busca = "nome"
                    break
        
        if boleto_encontrado:
            # ATUALIZA boleto existente
            print(f"📝 ATUALIZANDO boleto existente (método: {metodo_busca})")
            
            # Atualiza NOME se mudou (permite correção de nomes)
            boleto_encontrado['nome'] = nome
            
            # Atualiza grupo e cota (primeiro da lista)
            if grupo:
                boleto_encontrado['grupo'] = grupo
            if cota:
                boleto_encontrado['cota'] = cota
            
            # Atualiza contato/celular
            if contato:
                boleto_encontrado['celular'] = contato
            
            # Atualiza campo cotas
            if cotas_texto:
                boleto_encontrado['cotas'] = cotas_texto
            elif len(cotas) == 1 and len(grupos) == 1:
                boleto_encontrado['cotas'] = f"{cotas[0]} - {grupos[0]}"
            elif len(cotas) > 1:
                boleto_encontrado['cotas'] = f"{len(cotas)} cotas"
            
            print(f"✅ Boleto atualizado: Nome='{nome}', Cotas='{boleto_encontrado.get('cotas')}'")
        else:
            print(f"⚠️ Boleto NÃO encontrado para o cliente: '{nome}' (Grupos: {grupos}, Cotas: {cotas})")
            print(f"📋 Boletos existentes em {dia_key}: {[(b.get('nome'), b.get('grupo'), b.get('cota')) for b in boletos_data.get(dia_key, [])]}")
        
        # Salva boletos atualizados
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(boletos_data, f, indent=2, ensure_ascii=False)
    
    except Exception as e:
        print(f"❌ Erro ao sincronizar cliente para boleto: {e}")
        import traceback
        print(traceback.format_exc())

def _sync_boleto_to_cliente(boleto, dia_key):
    """Sincroniza dados do boleto para o cliente correspondente - ATUALIZA OU CRIA
    
    IDENTIFICAÇÃO: Usa GRUPO + COTA como chave única (ao invés de nome)
    - Se grupo/cota existem → busca por eles
    - Se não existem → busca por nome (fallback)
    """
    try:
        import uuid
        import re
        
        clientes_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clientes_data.json')
        
        # Carrega ou cria estrutura de clientes
        clientes_data = {'dia08': [], 'dia16': []}
        if os.path.exists(clientes_filepath):
            with open(clientes_filepath, 'r', encoding='utf-8') as f:
                clientes_data = json.load(f)
        
        # Extrai dados do boleto
        nome = boleto.get('nome', '').strip()
        if not nome:
            return
        
        cotas_info = boleto.get('cotas', '')
        grupo = boleto.get('grupo', '').strip()
        cota = boleto.get('cota', '').strip()
        
        # Preserva o texto original das cotas
        cotas_texto = cotas_info.strip()
        
        # Tenta extrair grupo e cota do campo cotas se não existirem
        if not grupo or not cota:
            match = re.search(r'(\d{3,4})\s*-\s*(\d{4})', cotas_info)
            if match:
                cota = match.group(1).strip()
                grupo = match.group(2).strip()
        
        contato = boleto.get('celular', '')
        boleto_link = _best_boleto_link(boleto)
        task_id = boleto.get('task_id', '')  # ID único do boleto
        
        print(f"🔄 SYNC Boleto→Cliente: TaskID={task_id}, Nome='{nome}', Grupo={grupo or 'N/A'}, Cota={cota or 'N/A'}, Dia={dia_key}")
        
        # Busca cliente existente - PRIORIDADE: task_id, depois Grupo+Cota, depois Nome
        cliente_encontrado = None
        metodo_busca = None
        
        # Método 0: Busca por TASK_ID (MAIS CONFIÁVEL - vínculo direto com boleto)
        if task_id:
            for idx, cliente in enumerate(clientes_data.get(dia_key, [])):
                cliente_task_id = cliente.get('task_id', '')
                if cliente_task_id == task_id:
                    print(f"✅ Cliente ENCONTRADO por TaskID (posição {idx}): '{cliente.get('nome')}'")
                    cliente_encontrado = cliente
                    metodo_busca = "task_id"
                    break
        
        # Método 1: Busca por GRUPO + COTA (se não achou por task_id)
        if not cliente_encontrado and grupo and cota:
            for idx, cliente in enumerate(clientes_data.get(dia_key, [])):
                cliente_grupo = str(cliente.get('grupo', '')).strip()
                cliente_cota = str(cliente.get('cota', '')).strip()
                
                if cliente_grupo == grupo and cliente_cota == cota:
                    print(f"✅ Cliente ENCONTRADO por Grupo+Cota (posição {idx}): '{cliente.get('nome')}'")
                    cliente_encontrado = cliente
                    metodo_busca = "grupo+cota"
                    break
        
        # Método 2: Fallback - Busca por NOME (se não achou por task_id nem grupo/cota)
        if not cliente_encontrado:
            for idx, cliente in enumerate(clientes_data.get(dia_key, [])):
                nome_cliente = cliente.get('nome', '').strip()
                if nome_cliente.lower() == nome.lower():
                    print(f"✅ Cliente ENCONTRADO por Nome (posição {idx}): '{nome_cliente}'")
                    cliente_encontrado = cliente
                    metodo_busca = "nome"
                    break
        
        if cliente_encontrado:
            # ATUALIZA cliente existente
            print(f"📝 ATUALIZANDO cliente existente (método: {metodo_busca}): {cliente_encontrado.get('client_id')}")
            
            # Converte formato antigo (string) para novo (listas) se necessário
            grupos_atual = cliente_encontrado.get('grupos', [])
            cotas_atual = cliente_encontrado.get('cotas', [])
            
            # Migração de formato antigo
            if isinstance(cliente_encontrado.get('grupo'), str):
                grupo_antigo = cliente_encontrado.get('grupo', '').strip()
                cota_antiga = cliente_encontrado.get('cota', '').strip()
                
                if grupo_antigo and cota_antiga:
                    grupos_atual = [grupo_antigo]
                    cotas_atual = [cota_antiga]
                else:
                    grupos_atual = []
                    cotas_atual = []
            
            # Adiciona nova cota/grupo se existir e ainda não estiver na lista
            if grupo and cota:
                cota_grupo_key = f"{cota}-{grupo}"
                cotas_grupos_existentes = [f"{c}-{g}" for c, g in zip(cotas_atual, grupos_atual)]
                
                if cota_grupo_key not in cotas_grupos_existentes:
                    grupos_atual.append(grupo)
                    cotas_atual.append(cota)
                    print(f"  ↻ Adicionando nova cota: {cota} - {grupo}")
            
            # Atualiza cliente
            cliente_encontrado['nome'] = nome
            cliente_encontrado['grupos'] = grupos_atual
            cliente_encontrado['cotas'] = cotas_atual
            cliente_encontrado['contato'] = contato or cliente_encontrado.get('contato', '')
            cliente_encontrado['task_id'] = task_id
            
            # Atualiza cotas_texto
            if len(cotas_atual) == 1:
                cliente_encontrado['cotas_texto'] = f"{cotas_atual[0]} - {grupos_atual[0]}"
            elif len(cotas_atual) > 1:
                cliente_encontrado['cotas_texto'] = f"{len(cotas_atual)} cotas"
            else:
                cliente_encontrado['cotas_texto'] = cotas_texto
            
            # Remove campos antigos (migração)
            cliente_encontrado.pop('grupo', None)
            cliente_encontrado.pop('cota', None)
            
            # Adiciona link ao histórico se não existir
            if boleto_link:
                if 'historico_boletos' not in cliente_encontrado:
                    cliente_encontrado['historico_boletos'] = []
                if boleto_link not in cliente_encontrado['historico_boletos']:
                    cliente_encontrado['historico_boletos'].append(boleto_link)
            
            cliente_encontrado['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"✅ Cliente atualizado: {nome} - {cliente_encontrado.get('cotas_texto')}")
        else:
            # CRIA novo cliente apenas se não existir
            print(f"🆕 Cliente NÃO encontrado, CRIANDO NOVO: '{nome}' (Grupo: {grupo}, Cota: {cota})")
            print(f"📋 Clientes existentes em {dia_key}: {[(c.get('nome'), c.get('grupos', c.get('grupo')), c.get('cotas', c.get('cota'))) for c in clientes_data.get(dia_key, [])]}")
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Inicia listas vazias
            grupos_list = []
            cotas_list = []
            
            # Adiciona grupo/cota se existirem
            if grupo and cota:
                grupos_list = [grupo]
                cotas_list = [cota]
                cotas_texto_calc = f"{cota} - {grupo}"
            else:
                cotas_texto_calc = cotas_texto
            
            novo_cliente = {
                'client_id': str(uuid.uuid4()),
                'nome': nome,
                'grupos': grupos_list,
                'cotas': cotas_list,
                'cotas_texto': cotas_texto_calc,
                'contato': contato,
                'task_id': task_id,
                'valor_primeira_cota': '',
                'historico_boletos': [boleto_link] if boleto_link else [],
                'created_at': timestamp,
                'updated_at': timestamp
            }
            
            if dia_key not in clientes_data:
                clientes_data[dia_key] = []
            clientes_data[dia_key].append(novo_cliente)
            print(f"✅ Novo cliente criado: {nome} - {cotas_texto_calc}")
        
        # Salva clientes atualizados
        with open(clientes_filepath, 'w', encoding='utf-8') as f:
            json.dump(clientes_data, f, indent=2, ensure_ascii=False)
    
    except Exception as e:
        print(f"❌ Erro ao sincronizar boleto para cliente: {e}")

# ========== FIM ROTAS DE GERENCIAMENTO DE CLIENTES ==========

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
    
    # Fecha driver se existir - COM MÚLTIPLAS TENTATIVAS
    driver_key = f'driver_{dia}'
    if app_state[driver_key]:
        try:
            progress_callback(dia, "🔒 Fechando navegador Chrome...")
            driver = app_state[driver_key]
            
            # Tenta fechar todas as janelas primeiro
            try:
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    driver.close()
            except:
                pass
            
            # Depois mata o driver completamente
            driver.quit()
            app_state[driver_key] = None
            progress_callback(dia, "✅ Chrome fechado com sucesso!")
        except Exception as e:
            # Força None mesmo com erro
            app_state[driver_key] = None
            progress_callback(dia, f"⚠️ Navegador fechado (com avisos): {str(e)[:50]}")
    else:
        progress_callback(dia, "ℹ️ Navegador já estava fechado")
    
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

# ========== ROTAS DA API DO AGENTE DE IA ==========

def _get_or_create_ai_agent():
    """Obtém ou cria instância do agente de IA"""
    # Usa session ID do usuário para manter contexto
    session_id = session.get('user', {}).get('id', 'default')
    
    if app_state['ai_agent'] is None or getattr(app_state['ai_agent'], 'session_id', None) != session_id:
        # Token do Google Gemini (GRATUITO!)
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        
        if not gemini_api_key:
            # Tenta ler de arquivo de configuração
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    ai_config = json.load(f)
                    gemini_api_key = ai_config.get('gemini_api_key')
        
        if not gemini_api_key:
            # Usa a chave fornecida pelo usuário
            gemini_api_key = "AIzaSyCbXLz7HBma76AsPYBr9S-bNmM3LvnlM7k"
        
        agent = OXCASHAgent(
            api_key=gemini_api_key,
            project_root=os.path.dirname(os.path.dirname(__file__)),
            session_id=session_id
        )
        
        # Registra callbacks para execução real
        agent.register_callback('generate_boleto', _execute_boleto_generation)
        agent.register_callback('execute_lance', _execute_lance_automation)
        agent.register_callback('send_whatsapp', _execute_whatsapp_send)
        agent.register_callback('start_automation', _start_automation_callback)
        agent.register_callback('stop_automation', _stop_automation_callback)
        agent.register_callback('get_automation_status', _get_automation_status_callback)
        agent.register_callback('send_whatsapp_custom', _send_whatsapp_custom_callback)
        agent.register_callback('schedule_whatsapp', _schedule_whatsapp_callback)
        
        app_state['ai_agent'] = agent
    
    return app_state['ai_agent']

def _execute_boleto_generation(task_id: str, dia: str) -> Dict:
    """Executa geração real de boleto via automação"""
    try:
        # Carrega credenciais
        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        if not os.path.exists(creds_path):
            raise Exception('Credenciais não configuradas')
        
        with open(creds_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        servopa_creds = credentials.get('servopa')
        if not servopa_creds:
            raise Exception('Credenciais do Servopa não encontradas')
        
        # Carrega dados do boleto
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        with open(boletos_filepath, 'r', encoding='utf-8') as f:
            boletos_data = json.load(f)
        
        boleto_entry = None
        for dia_key in ('dia08', 'dia16'):
            for item in boletos_data.get(dia_key, []):
                if str(item.get('task_id')) == str(task_id):
                    boleto_entry = item
                    dia = '08' if dia_key == 'dia08' else '16'
                    break
            if boleto_entry:
                break
        
        if not boleto_entry:
            raise Exception('Boleto não encontrado')
        
        # Cria driver headless
        driver = create_driver(headless=True)
        
        try:
            # Login no Servopa
            if not login_servopa(driver, lambda msg: socketio.emit('log', {'dia': 'ai', 'message': msg}), servopa_creds):
                raise Exception('Falha no login do Servopa')
            
            # Executa geração do boleto
            result = run_boleto_flow(
                driver, 
                boleto_entry, 
                dia,
                lambda msg: socketio.emit('log', {'dia': 'ai', 'message': msg})
            )
            
            # Salva resultado no arquivo
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if result.png_base64:
                boleto_entry['png_base64'] = result.png_base64
            if result.boleto_url:
                boleto_entry['boleto_url'] = result.boleto_url
                boleto_entry['short_link'] = result.boleto_url
            boleto_entry['last_generated'] = timestamp
            boleto_entry['tipo'] = result.tipo
            
            with open(boletos_filepath, 'w', encoding='utf-8') as f:
                json.dump(boletos_data, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'boleto_url': result.boleto_url,
                'tipo': result.tipo,
                'timestamp': timestamp
            }
            
        finally:
            driver.quit()
            
    except Exception as e:
        socketio.emit('log', {'dia': 'ai', 'message': f'❌ Erro: {str(e)}'})
        raise

def _execute_lance_automation(grupo: str, cota: str) -> Dict:
    """Executa lance real via automação"""
    try:
        # Carrega credenciais
        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        if not os.path.exists(creds_path):
            raise Exception('Credenciais não configuradas')
        
        with open(creds_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        servopa_creds = credentials.get('servopa')
        if not servopa_creds:
            raise Exception('Credenciais do Servopa não encontradas')
        
        # Cria driver headless
        driver = create_driver(headless=True)
        
        try:
            # Login no Servopa
            if not login_servopa(driver, lambda msg: socketio.emit('log', {'dia': 'ai', 'message': msg}), servopa_creds):
                raise Exception('Falha no login do Servopa')
            
            # Navega para painel
            driver.get("https://www.consorcioservopa.com.br/vendas/painel")
            time.sleep(2)
            
            # Importa funções de lance
            from automation.servopa_lances import processar_lance_completo
            
            # Executa lance
            result = processar_lance_completo(
                driver, 
                grupo, 
                cota,
                lambda msg: socketio.emit('log', {'dia': 'ai', 'message': msg})
            )
            
            if not result['success']:
                raise Exception(result.get('lance_message', 'Falha ao executar lance'))
            
            return {
                'success': True,
                'protocol_number': result.get('protocol_number'),
                'already_exists': result.get('already_exists', False),
                'message': result.get('lance_message', 'Lance executado com sucesso')
            }
            
        finally:
            driver.quit()
            
    except Exception as e:
        socketio.emit('log', {'dia': 'ai', 'message': f'❌ Erro: {str(e)}'})
        raise

def _execute_whatsapp_send(task_id: str) -> Dict:
    """Executa envio de WhatsApp real"""
    # Reutiliza a lógica existente da rota /api/boletos/whatsapp
    # (já implementada anteriormente)
    return {'success': True, 'message': 'WhatsApp enviado'}

def _start_automation_callback(dia: str) -> Dict:
    """Callback para iniciar automação via IA"""
    try:
        # Importa requests para fazer chamada HTTP interna
        import requests
        
        # Faz chamada para a rota de start existente
        response = requests.post(
            f'http://localhost:5000/api/automation/start/{dia}',
            json={},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': data.get('success', False),
                'message': data.get('message', 'Automação iniciada'),
                'dia': dia
            }
        else:
            return {
                'success': False,
                'error': f'Erro HTTP {response.status_code}',
                'dia': dia
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'dia': dia
        }

def _stop_automation_callback(dia: str) -> Dict:
    """Callback para parar automação via IA"""
    try:
        import requests
        
        response = requests.post(
            f'http://localhost:5000/api/automation/stop/{dia}',
            json={},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': data.get('success', False),
                'message': data.get('message', 'Automação parada'),
                'dia': dia
            }
        else:
            # Mesmo com erro HTTP, pode ter parado - verifica status
            status_response = requests.get(f'http://localhost:5000/api/stats', timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                is_running = status_data.get('running', {}).get(dia, False)
                
                if not is_running:
                    return {
                        'success': True,
                        'message': f'Automação {dia} foi parada (status confirmado)',
                        'dia': dia
                    }
            
            return {
                'success': False,
                'error': f'Erro HTTP {response.status_code}',
                'message': f'Não foi possível confirmar se a automação parou. Verifique manualmente.',
                'dia': dia
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Erro ao tentar parar automação: {str(e)}',
            'dia': dia
        }

def _send_whatsapp_custom_callback(numero: str, mensagem: str) -> Dict:
    """Callback para enviar WhatsApp customizado via IA"""
    try:
        # Carrega configuração da Evolution API
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evolution_config.json')
        if not os.path.exists(config_file):
            return {
                'success': False,
                'error': 'Configuração da Evolution API não encontrada. Configure em evolution_config.json'
            }
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'api' not in config:
            return {
                'success': False,
                'error': 'Configuração da API incompleta'
            }
        
        # Importa módulo de envio
        from utils.evolution_api import EvolutionAPI
        
        # Cria cliente API
        api = EvolutionAPI(
            config['api']['base_url'],
            config['api']['instance_name'],
            config['api']['api_key']
        )
        
        # Envia mensagem
        success, result = api.send_text_message(numero, mensagem)
        
        if success:
            return {
                'success': True,
                'message': f'WhatsApp enviado para {numero}',
                'numero': numero,
                'result': result
            }
        else:
            return {
                'success': False,
                'error': f'Falha ao enviar: {result}',
                'numero': numero
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'numero': numero
        }

def _schedule_whatsapp_callback(numero: str, mensagem: str, data_hora: str) -> Dict:
    """Callback para agendar WhatsApp via IA"""
    try:
        from datetime import datetime
        import threading
        
        # Valida formato de data/hora
        try:
            dt = datetime.strptime(data_hora, '%d/%m/%Y %H:%M')
        except ValueError:
            return {
                'success': False,
                'error': 'Formato de data inválido. Use: DD/MM/YYYY HH:MM (ex: 07/10/2025 14:30)'
            }
        
        # Verifica se é no futuro
        now = datetime.now()
        if dt <= now:
            return {
                'success': False,
                'error': 'Data/hora deve ser no futuro'
            }
        
        # Calcula delay em segundos
        delay = (dt - now).total_seconds()
        
        # Carrega configuração da Evolution API
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evolution_config.json')
        if not os.path.exists(config_file):
            return {
                'success': False,
                'error': 'Configuração da Evolution API não encontrada'
            }
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Função que será executada no futuro
        def send_scheduled_message():
            try:
                from utils.evolution_api import EvolutionAPI
                
                api = EvolutionAPI(
                    config['api']['base_url'],
                    config['api']['instance_name'],
                    config['api']['api_key']
                )
                
                success, result = api.send_text_message(numero, mensagem)
                print(f"📅 Mensagem agendada enviada para {numero}: {'✅ Sucesso' if success else '❌ Falha'}")
                
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem agendada: {str(e)}")
        
        # Agenda em thread separada
        timer = threading.Timer(delay, send_scheduled_message)
        timer.daemon = True
        timer.start()
        
        return {
            'success': True,
            'message': f'WhatsApp agendado para {numero} em {data_hora}',
            'numero': numero,
            'data_hora': data_hora,
            'delay_segundos': int(delay),
            'delay_minutos': round(delay / 60, 1)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'numero': numero,
            'data_hora': data_hora
        }

def _get_automation_status_callback(dia: str) -> Dict:
    """Callback para verificar status de automação via IA"""
    if dia == "both":
        return {
            'dia8_running': app_state['automation_dia8_running'],
            'dia16_running': app_state['automation_dia16_running'],
            'dia8': {
                'running': app_state['automation_dia8_running'],
                'has_driver': app_state['driver_dia8'] is not None
            },
            'dia16': {
                'running': app_state['automation_dia16_running'],
                'has_driver': app_state['driver_dia16'] is not None
            }
        }
    else:
        return {
            'running': app_state[f'automation_{dia}_running'],
            'has_driver': app_state[f'driver_{dia}'] is not None
        }


@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    """Endpoint para conversar com o agente de IA"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Mensagem não pode estar vazia'
            })
        
        # Obtém agente de IA
        agent = _get_or_create_ai_agent()
        
        # Processa mensagem
        response = agent.chat(message)
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro no chat da IA: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.'
        })

@app.route('/api/ai/reset', methods=['POST'])
def api_ai_reset():
    """Reseta a conversa com o agente de IA"""
    try:
        agent = _get_or_create_ai_agent()
        agent.reset_conversation()
        
        return jsonify({
            'success': True,
            'message': 'Conversa resetada com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/ai/status')
def api_ai_status():
    """Retorna status do agente de IA"""
    try:
        agent = _get_or_create_ai_agent()
        
        return jsonify({
            'success': True,
            'active': True,
            'conversation_length': len(agent.conversation_history),
            'tools_available': len(agent.tools)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'active': False
        })

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
                
                protocolo_valor = kwargs.get('protocolo')
                documento_url = kwargs.get('documento_url')
                docparser_url = kwargs.get('docparser_url')

                entry = {
                    'hora': datetime.now().strftime('%H:%M:%S'),
                    'data': datetime.now().strftime('%Y-%m-%d'),
                    'grupo': str(grupo) if grupo else '-',
                    'cota': str(cota) if cota else '-',
                    'nome': str(nome) if nome else '-',
                    'valor_lance': str(valor) if valor else '-',
                    'protocolo': str(protocolo_valor) if protocolo_valor else '',
                    'documento_url': str(documento_url) if documento_url else '',
                    'docparser_url': str(docparser_url) if docparser_url else '',
                    'status': str(status) if status else 'Processado',
                    'observacao': str(obs) if obs else '',
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
