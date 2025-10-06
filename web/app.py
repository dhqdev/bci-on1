# web/app.py
"""
🚀 OXCASH Web Interface
Interface web moderna para o sistema de automação
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from functools import wraps
import json
import os
import sys
import threading
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
    }
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

@app.route('/automation/dia8')
@login_required
def automation_dia8():
    """Página de automação Dia 8"""
    return render_template('automation_dia8.html')

@app.route('/automation/dia16')
@login_required
def automation_dia16():
    """Página de automação Dia 16"""
    return render_template('automation_dia16.html')

@app.route('/whatsapp')
@login_required
def whatsapp():
    """Página de envio WhatsApp"""
    return render_template('whatsapp.html')

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

@app.route('/lances')
@login_required
def lances():
    """Página de Kanban de Lances Servopa"""
    return render_template('lances.html')


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
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': {'dia08': [], 'dia16': []}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/import', methods=['POST'])
def api_boletos_import():
    """Importa boletos do Todoist via API REST"""
    try:
        from utils.todoist_rest_api import TodoistRestAPI
        
        # Token do Todoist (pode ser movido para credentials.json futuramente)
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        
        # Emite progresso via WebSocket
        def emit_progress(message):
            socketio.emit('boletos_progress', {'message': message})
        
        # Função para parsear descrição e extrair cotas e celular
        def parse_boleto_description(description_text):
            """Extrai cotas e celular da descrição do Todoist"""
            cotas = ''
            celular = ''
            
            if not description_text:
                return cotas, celular
            
            # Remove quebras de linha e limpa o texto
            text = description_text.replace('\n', ' ').strip()
            
            # Extrai celular (formato: 📱 Celular: XXXXX ou apenas Celular: XXXXX)
            import re
            celular_match = re.search(r'(?:📱\s*)?[Cc]elular:\s*(\d+)', text)
            if celular_match:
                celular = celular_match.group(1)
                # Remove a parte do celular do texto
                text = re.sub(r'(?:📱\s*)?[Cc]elular:\s*\d+', '', text)
            
            # Limpa repetições de "Cotas:" e extrai o valor
            # Remove todos os "Cotas:" extras e pega só o número/valor
            text = re.sub(r'[Cc]otas:\s*', '', text, flags=re.IGNORECASE)
            text = text.strip()
            
            # Se sobrou algo, é a cota
            if text:
                cotas = text
            
            return cotas, celular
        
        emit_progress('🔄 Conectando à API do Todoist...')
        
        # Cria cliente da API
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        # Extrai dados via API REST
        boletos_data = api.extract_boletos_board(
            project_name="Boletos Servopa Outubro",
            section_dia08="Vencimento dia 08",
            section_dia16="Vencimento dia 16",
            progress_callback=emit_progress
        )
        
        # Salva dados
        clean_data = {
            'dia08': [],
            'dia16': [],
            'last_import': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for boleto in boletos_data['dia08']:
            # Parseia descrição para separar cotas e celular
            raw_cotas = boleto.get('cotas', '')
            cotas, celular = parse_boleto_description(raw_cotas)
            
            clean_data['dia08'].append({
                'nome': boleto['nome'],
                'cotas': cotas,
                'celular': celular,
                'task_id': boleto.get('task_id', ''),
                'is_completed': boleto.get('is_completed', False)
            })
        
        for boleto in boletos_data['dia16']:
            # Parseia descrição para separar cotas e celular
            raw_cotas = boleto.get('cotas', '')
            cotas, celular = parse_boleto_description(raw_cotas)
            
            clean_data['dia16'].append({
                'nome': boleto['nome'],
                'cotas': cotas,
                'celular': celular,
                'task_id': boleto.get('task_id', ''),
                'is_completed': boleto.get('is_completed', False)
            })
        
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')

        # Preserva campos locais adicionais (png_base64, boleto_url, etc.)
        existing_data = {}
        if os.path.exists(boletos_filepath):
            try:
                with open(boletos_filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except Exception:
                existing_data = {}

        def merge_preserved_fields(new_list, old_list):
            if not isinstance(old_list, list):
                return
            old_map = {str(item.get('task_id')): item for item in old_list if item.get('task_id')}
            for entry in new_list:
                existing = old_map.get(str(entry.get('task_id')))
                if not existing:
                    continue

                # Preferir celular existente se o novo vier vazio
                if not entry.get('celular') and existing.get('celular'):
                    entry['celular'] = existing['celular']

                for field in ('png_base64', 'boleto_url', 'short_link', 'last_generated', 'tipo', 'grupo', 'cota', 'metadata'):
                    if existing.get(field) and not entry.get(field):
                        entry[field] = existing[field]

        merge_preserved_fields(clean_data['dia08'], existing_data.get('dia08', []))
        merge_preserved_fields(clean_data['dia16'], existing_data.get('dia16', []))
        
        with open(boletos_filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
        
        emit_progress('✅ Importação concluída!')
        
        total_dia08 = len(clean_data['dia08'])
        total_dia16 = len(clean_data['dia16'])
        
        return jsonify({
            'success': True, 
            'message': f'Importado: {total_dia08} boletos (dia 08) e {total_dia16} boletos (dia 16)',
            'data': clean_data
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/toggle/<task_id>', methods=['POST'])
def api_boletos_toggle(task_id):
    """Marca/desmarca uma tarefa no Todoist"""
    try:
        from utils.todoist_rest_api import TodoistRestAPI
        
        # Token do Todoist
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        
        data = request.json
        is_completed = data.get('is_completed', False)
        
        # Cria cliente da API
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        if is_completed:
            # Marca como concluída
            api.close_task(task_id)
        else:
            # Reabre tarefa
            api.reopen_task(task_id)
        
        # Atualiza arquivo local também
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if os.path.exists(boletos_filepath):
            with open(boletos_filepath, 'r', encoding='utf-8') as f:
                boletos_data = json.load(f)
            
            # Atualiza status no cache local
            for dia_key in ['dia08', 'dia16']:
                if dia_key in boletos_data:
                    for boleto in boletos_data[dia_key]:
                        if boleto.get('task_id') == task_id:
                            boleto['is_completed'] = is_completed
                            break
            
            with open(boletos_filepath, 'w', encoding='utf-8') as f:
                json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Tarefa atualizada no Todoist'
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/update/<task_id>', methods=['POST'])
def api_boletos_update(task_id):
    """Atualiza um boleto existente"""
    try:
        data = request.json
        nome = data.get('nome', '')
        celular = data.get('celular', '')
        cotas = data.get('cotas', '')
        dia = data.get('dia', '08')
        png_base64 = data.get('png_base64', '')  # Pode ser imagem ou link
        short_link = data.get('short_link', '')
        
        # Atualiza no Todoist
        from utils.todoist_rest_api import TodoistRestAPI
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        # Monta novo conteúdo da tarefa
        new_content = nome
        
        # Monta descrição com dados estruturados
        description_parts = []
        if cotas:
            description_parts.append(f"Cotas: {cotas}")
        if celular:
            description_parts.append(f"📱 Celular: {celular}")
        
        new_description = "\n".join(description_parts) if description_parts else ""
        
        # Atualiza task no Todoist
        api.update_task(task_id, content=new_content, description=new_description)
        
        # Atualiza arquivo local
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if os.path.exists(boletos_filepath):
            with open(boletos_filepath, 'r', encoding='utf-8') as f:
                boletos_data = json.load(f)
            
            dia_key = f'dia{dia}'
            if dia_key in boletos_data:
                for boleto in boletos_data[dia_key]:
                    if boleto.get('task_id') == task_id:
                        boleto['nome'] = nome
                        boleto['celular'] = celular
                        boleto['cotas'] = cotas
                        # ✅ Salva PNG em base64
                        if png_base64:
                            boleto['png_base64'] = png_base64
                        if short_link:
                            boleto['short_link'] = short_link
                        break
            
            with open(boletos_filepath, 'w', encoding='utf-8') as f:
                json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Boleto atualizado com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/create', methods=['POST'])
def api_boletos_create():
    """Cria um novo boleto"""
    try:
        data = request.json
        nome = data.get('nome', '')
        celular = data.get('celular', '')
        cotas = data.get('cotas', '')
        dia = data.get('dia', '08')
        png_base64 = data.get('png_base64', '')  # Pode ser imagem ou link
        short_link = data.get('short_link', '')
        
        if not nome:
            return jsonify({'success': False, 'error': 'Nome é obrigatório'})
        
        # Cria no Todoist
        from utils.todoist_rest_api import TodoistRestAPI
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        # Monta conteúdo da tarefa
        content = nome
        
        # Monta descrição com dados estruturados
        description_parts = []
        if cotas:
            description_parts.append(f"Cotas: {cotas}")
        if celular:
            description_parts.append(f"📱 Celular: {celular}")
        
        description = "\n".join(description_parts) if description_parts else ""
        
        # Cria a tarefa
        task = api.create_task(content=content, description=description)
        task_id = task.get('id')
        
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
        
        # ✅ Adiciona PNG se fornecido
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

@app.route('/api/boletos/delete/<task_id>', methods=['POST'])
def api_boletos_delete(task_id):
    """Deleta um boleto"""
    try:
        # Deleta no Todoist
        from utils.todoist_rest_api import TodoistRestAPI
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        api.delete_task(task_id)
        
        # Remove do arquivo local
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if os.path.exists(boletos_filepath):
            with open(boletos_filepath, 'r', encoding='utf-8') as f:
                boletos_data = json.load(f)
            
            for dia_key in ['dia08', 'dia16']:
                if dia_key in boletos_data:
                    boletos_data[dia_key] = [
                        b for b in boletos_data[dia_key] 
                        if b.get('task_id') != task_id
                    ]
            
            with open(boletos_filepath, 'w', encoding='utf-8') as f:
                json.dump(boletos_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Boleto deletado com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/boletos/sync', methods=['POST'])
def api_boletos_sync():
    """Sincroniza status dos boletos do Todoist para o site (bidirecional)"""
    try:
        from utils.todoist_rest_api import TodoistRestAPI
        
        # Token do Todoist
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        
        # Carrega dados locais
        boletos_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boletos_data.json')
        if not os.path.exists(boletos_filepath):
            return jsonify({'success': False, 'error': 'Nenhum dado local encontrado'})
        
        try:
            with open(boletos_filepath, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'error': f'Erro ao ler dados locais: {str(e)}'})
        
        # Busca dados atualizados do Todoist
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        try:
            updated_data = api.extract_boletos_board(
                project_name="Boletos Servopa Outubro",
                section_dia08="Vencimento dia 08",
                section_dia16="Vencimento dia 16"
            )
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erro ao buscar dados do Todoist: {str(e)}'})
        
        # Conta mudanças e mescla dados (preserva celular local)
        changes = 0
        merged_data = {'dia08': [], 'dia16': []}
        
        for dia_key in ['dia08', 'dia16']:
            local_tasks = {t.get('task_id'): t for t in local_data.get(dia_key, []) if t.get('task_id')}
            updated_tasks = {t.get('task_id'): t for t in updated_data.get(dia_key, []) if t.get('task_id')}
            
            for task_id, updated_task in updated_tasks.items():
                # Começa com dados do Todoist
                merged_task = updated_task.copy()
                
                # Se já existia localmente, preserva o celular local
                if task_id in local_tasks:
                    local_task = local_tasks[task_id]
                    
                    # Preserva celular local se existir
                    if local_task.get('celular'):
                        merged_task['celular'] = local_task['celular']
                    
                    # ✅ Preserva PNG local se existir
                    if local_task.get('png_base64'):
                        merged_task['png_base64'] = local_task['png_base64']

                    # Preserva demais metadados do boleto gerado
                    if local_task.get('boleto_url'):
                        merged_task['boleto_url'] = local_task['boleto_url']
                    if local_task.get('last_generated'):
                        merged_task['last_generated'] = local_task['last_generated']
                    if local_task.get('tipo'):
                        merged_task['tipo'] = local_task['tipo']
                    if local_task.get('metadata'):
                        merged_task['metadata'] = local_task['metadata']
                    if local_task.get('grupo'):
                        merged_task['grupo'] = local_task['grupo']
                    if local_task.get('cota'):
                        merged_task['cota'] = local_task['cota']
                    
                    # Conta mudança de status
                    if local_task.get('is_completed') != updated_task.get('is_completed'):
                        changes += 1
                
                merged_data[dia_key].append(merged_task)
        
        # Adiciona timestamp
        merged_data['last_sync'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Salva dados atualizados
        try:
            with open(boletos_filepath, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erro ao salvar dados: {str(e)}'})
        
        return jsonify({
            'success': True,
            'changes': changes,
            'data': merged_data,
            'message': f'{changes} alterações sincronizadas do Todoist' if changes > 0 else 'Tudo sincronizado'
        })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na sincronização: {error_details}")
        return jsonify({'success': False, 'error': f'Erro na sincronização: {str(e)}'})


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

# ========== ROTAS DE LANCES SERVOPA ==========

@app.route('/api/lances', methods=['GET'])
def api_lances():
    """Retorna dados dos lances"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lances_data.json')
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': True, 'data': {'dia08': [], 'dia16': []}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lances/import', methods=['POST'])
def api_lances_import():
    """Importa lances do Todoist via API REST"""
    try:
        from utils.todoist_rest_api import TodoistRestAPI
        
        # Token do Todoist
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        
        # Emite progresso via WebSocket
        def emit_progress(message):
            socketio.emit('lances_progress', {'message': message})
        
        emit_progress('🔄 Conectando à API do Todoist...')
        
        # Cria cliente da API
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        # Extrai dados via API REST
        lances_data = api.extract_lances_board(
            project_dia8="Lances Servopa Outubro Dia 8",
            project_dia16="Lances Servopa Outubro Dia 16",
            progress_callback=emit_progress
        )
        
        # Salva dados
        clean_data = {
            'dia08': [],
            'dia16': [],
            'last_import': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Copia dados do dia 8 (com grupos/seções)
        for grupo in lances_data['dia08']:
            clean_grupo = {
                'grupo': grupo['grupo'],
                'title': grupo['title'],
                'tasks': []
            }
            for task in grupo['tasks']:
                clean_grupo['tasks'].append({
                    'cota': task['cota'],
                    'nome': task['nome'],
                    'task_id': task['task_id'],
                    'is_completed': task.get('is_completed', False)
                })
            clean_data['dia08'].append(clean_grupo)
        
        # Copia dados do dia 16
        for grupo in lances_data['dia16']:
            clean_grupo = {
                'grupo': grupo['grupo'],
                'title': grupo['title'],
                'tasks': []
            }
            for task in grupo['tasks']:
                clean_grupo['tasks'].append({
                    'cota': task['cota'],
                    'nome': task['nome'],
                    'task_id': task['task_id'],
                    'is_completed': task.get('is_completed', False)
                })
            clean_data['dia16'].append(clean_grupo)
        
        lances_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lances_data.json')
        
        with open(lances_filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
        
        emit_progress('✅ Importação concluída!')
        
        total_grupos_8 = len(clean_data['dia08'])
        total_cotas_8 = sum(len(g['tasks']) for g in clean_data['dia08'])
        total_grupos_16 = len(clean_data['dia16'])
        total_cotas_16 = sum(len(g['tasks']) for g in clean_data['dia16'])
        
        return jsonify({
            'success': True,
            'message': f'Importado: Dia 08 ({total_grupos_8} grupos, {total_cotas_8} cotas) | Dia 16 ({total_grupos_16} grupos, {total_cotas_16} cotas)',
            'data': clean_data
        })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na importação de lances: {error_details}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lances/toggle/<task_id>', methods=['POST'])
def api_lances_toggle(task_id):
    """Marca/desmarca uma tarefa de lance no Todoist"""
    try:
        from utils.todoist_rest_api import TodoistRestAPI
        
        # Token do Todoist
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        
        data = request.json
        is_completed = data.get('is_completed', False)
        
        # Cria cliente da API
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        if is_completed:
            # Marca como concluída
            api.close_task(task_id)
        else:
            # Reabre tarefa
            api.reopen_task(task_id)
        
        # Atualiza arquivo local também
        lances_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lances_data.json')
        if os.path.exists(lances_filepath):
            with open(lances_filepath, 'r', encoding='utf-8') as f:
                lances_data = json.load(f)
            
            # Atualiza status no cache local (busca em grupos)
            for dia_key in ['dia08', 'dia16']:
                if dia_key in lances_data:
                    for grupo in lances_data[dia_key]:
                        if 'tasks' in grupo:
                            for task in grupo['tasks']:
                                if task.get('task_id') == task_id:
                                    task['is_completed'] = is_completed
                                    break
            
            with open(lances_filepath, 'w', encoding='utf-8') as f:
                json.dump(lances_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Lance atualizado no Todoist'
        })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao toggle lance: {error_details}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lances/update/<task_id>', methods=['POST'])
def api_lances_update(task_id):
    """Atualiza um lance existente"""
    try:
        data = request.json
        cota = data.get('cota', '')
        nome = data.get('nome', '')
        grupo = data.get('grupo', '')
        dia = data.get('dia', '08')
        
        # Atualiza no Todoist
        from utils.todoist_rest_api import TodoistRestAPI
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        # Monta novo conteúdo
        new_content = f"Cota {cota} - {nome}"
        api.update_task(task_id, content=new_content)
        
        # Atualiza arquivo local
        lances_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lances_data.json')
        if os.path.exists(lances_filepath):
            with open(lances_filepath, 'r', encoding='utf-8') as f:
                lances_data = json.load(f)
            
            dia_key = f'dia{dia}'
            if dia_key in lances_data:
                for grp in lances_data[dia_key]:
                    if 'tasks' in grp:
                        for task in grp['tasks']:
                            if task.get('task_id') == task_id:
                                task['cota'] = cota
                                task['nome'] = nome
                                break
            
            with open(lances_filepath, 'w', encoding='utf-8') as f:
                json.dump(lances_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Lance atualizado com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lances/create', methods=['POST'])
def api_lances_create():
    """Cria um novo lance"""
    try:
        data = request.json
        cota = data.get('cota', '')
        nome = data.get('nome', '')
        grupo = data.get('grupo', '')
        dia = data.get('dia', '08')
        
        if not cota or not nome:
            return jsonify({'success': False, 'error': 'Cota e Nome são obrigatórios'})
        
        # Cria no Todoist
        from utils.todoist_rest_api import TodoistRestAPI
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        content = f"Cota {cota} - {nome}"
        task = api.create_task(content=content)
        task_id = task.get('id')
        
        # Adiciona ao arquivo local
        lances_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lances_data.json')
        lances_data = {'dia08': [], 'dia16': []}
        
        if os.path.exists(lances_filepath):
            with open(lances_filepath, 'r', encoding='utf-8') as f:
                lances_data = json.load(f)
        
        dia_key = f'dia{dia}'
        if dia_key not in lances_data:
            lances_data[dia_key] = []
        
        # Procura grupo existente ou cria novo
        grupo_obj = None
        for grp in lances_data[dia_key]:
            if grp.get('grupo') == grupo:
                grupo_obj = grp
                break
        
        if not grupo_obj:
            grupo_obj = {
                'grupo': grupo,
                'title': f'{grupo} - dia {dia}',
                'tasks': []
            }
            lances_data[dia_key].append(grupo_obj)
        
        new_lance = {
            'task_id': task_id,
            'cota': cota,
            'nome': nome,
            'is_completed': False
        }
        
        grupo_obj['tasks'].append(new_lance)
        
        with open(lances_filepath, 'w', encoding='utf-8') as f:
            json.dump(lances_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Lance criado com sucesso',
            'data': new_lance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lances/delete/<task_id>', methods=['POST'])
def api_lances_delete(task_id):
    """Deleta um lance"""
    try:
        # Deleta no Todoist
        from utils.todoist_rest_api import TodoistRestAPI
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        api.delete_task(task_id)
        
        # Remove do arquivo local
        lances_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lances_data.json')
        if os.path.exists(lances_filepath):
            with open(lances_filepath, 'r', encoding='utf-8') as f:
                lances_data = json.load(f)
            
            for dia_key in ['dia08', 'dia16']:
                if dia_key in lances_data:
                    for grupo in lances_data[dia_key]:
                        if 'tasks' in grupo:
                            grupo['tasks'] = [
                                t for t in grupo['tasks']
                                if t.get('task_id') != task_id
                            ]
            
            with open(lances_filepath, 'w', encoding='utf-8') as f:
                json.dump(lances_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Lance deletado com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lances/sync', methods=['POST'])
def api_lances_sync():
    """Sincroniza status dos lances do Todoist para o site (bidirecional)"""
    try:
        from utils.todoist_rest_api import TodoistRestAPI
        
        # Token do Todoist
        TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
        
        # Carrega dados locais
        lances_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lances_data.json')
        if not os.path.exists(lances_filepath):
            return jsonify({'success': False, 'error': 'Nenhum dado local encontrado'})
        
        try:
            with open(lances_filepath, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'error': f'Erro ao ler dados locais: {str(e)}'})
        
        # Busca dados atualizados do Todoist
        api = TodoistRestAPI(TODOIST_TOKEN)
        
        try:
            updated_data = api.extract_lances_board(
                project_dia8="Lances Servopa Outubro Dia 8",
                project_dia16="Lances Servopa Outubro Dia 16"
            )
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erro ao buscar dados do Todoist: {str(e)}'})
        
        # Conta mudanças
        changes = 0
        for dia_key in ['dia08', 'dia16']:
            # Cria dicionário de tasks por task_id (local)
            local_tasks = {}
            for grupo in local_data.get(dia_key, []):
                for task in grupo.get('tasks', []):
                    if task.get('task_id'):
                        local_tasks[task['task_id']] = task
            
            # Cria dicionário de tasks por task_id (updated)
            updated_tasks = {}
            for grupo in updated_data.get(dia_key, []):
                for task in grupo.get('tasks', []):
                    if task.get('task_id'):
                        updated_tasks[task['task_id']] = task
            
            # Compara mudanças
            for task_id, updated_task in updated_tasks.items():
                if task_id in local_tasks:
                    local_task = local_tasks[task_id]
                    if local_task.get('is_completed') != updated_task.get('is_completed'):
                        changes += 1
        
        # Salva dados atualizados
        clean_data = {
            'dia08': [],
            'dia16': [],
            'last_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Copia dados do dia 8
        for grupo in updated_data['dia08']:
            clean_grupo = {
                'grupo': grupo['grupo'],
                'title': grupo['title'],
                'tasks': []
            }
            for task in grupo['tasks']:
                clean_grupo['tasks'].append({
                    'cota': task['cota'],
                    'nome': task['nome'],
                    'task_id': task['task_id'],
                    'is_completed': task.get('is_completed', False)
                })
            clean_data['dia08'].append(clean_grupo)
        
        # Copia dados do dia 16
        for grupo in updated_data['dia16']:
            clean_grupo = {
                'grupo': grupo['grupo'],
                'title': grupo['title'],
                'tasks': []
            }
            for task in grupo['tasks']:
                clean_grupo['tasks'].append({
                    'cota': task['cota'],
                    'nome': task['nome'],
                    'task_id': task['task_id'],
                    'is_completed': task.get('is_completed', False)
                })
            clean_data['dia16'].append(clean_grupo)
        
        try:
            with open(lances_filepath, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erro ao salvar dados: {str(e)}'})
        
        return jsonify({
            'success': True,
            'changes': changes,
            'data': clean_data,
            'message': f'{changes} alterações sincronizadas do Todoist' if changes > 0 else 'Tudo sincronizado'
        })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na sincronização de lances: {error_details}")
        return jsonify({'success': False, 'error': f'Erro na sincronização: {str(e)}'})

# ========== FIM ROTAS DE LANCES ==========

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
