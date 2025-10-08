"""
OXCASH - API Backend Moderna com WebSocket
Sistema de automação de boletos e lances com atualizações em tempo real
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
from datetime import datetime
import threading
import time
import random

# Importar cliente Supabase
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
    SUPABASE_KEY = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase conectado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao conectar Supabase: {e}")
    supabase = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oxcash-secret-key-2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Estado global das automações
automation_threads = {
    '08': None,
    '16': None
}

# ========================================
# ROTAS DA INTERFACE WEB
# ========================================

@app.route('/')
def index():
    """Página principal - Dashboard moderno"""
    return render_template('preview_dashboard.html')

@app.route('/demo-automation')
def demo_automation():
    """Página de demonstração de automação"""
    return render_template('preview_automation.html')

# ========================================
# API ENDPOINTS REST
# ========================================

@app.route('/api/boletos', methods=['GET'])
def get_boletos():
    """Retorna todos os boletos ou filtrados por dia"""
    try:
        dia = request.args.get('dia')

        if not supabase:
            return jsonify({'success': False, 'error': 'Banco de dados não disponível'})

        query = supabase.table('boletos').select('*')

        if dia:
            query = query.eq('dia', dia)

        response = query.execute()

        # Organiza por dia
        boletos_dia08 = [b for b in response.data if b.get('dia') == '08']
        boletos_dia16 = [b for b in response.data if b.get('dia') == '16']

        return jsonify({
            'success': True,
            'data': {
                'dia08': boletos_dia08,
                'dia16': boletos_dia16,
                'total': len(response.data)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/cotas', methods=['GET'])
def get_cotas():
    """Retorna todas as cotas agrupadas por grupo"""
    try:
        if not supabase:
            return jsonify({'success': False, 'error': 'Banco de dados não disponível'})

        response = supabase.table('cotas').select('*').execute()

        # Agrupa por grupo
        grupos = {}
        for cota in response.data:
            grupo_key = cota.get('grupo')
            if grupo_key not in grupos:
                grupos[grupo_key] = {
                    'grupo': grupo_key,
                    'dia': cota.get('dia'),
                    'cotas': []
                }
            grupos[grupo_key]['cotas'].append(cota)

        return jsonify({
            'success': True,
            'data': {
                'grupos': list(grupos.values()),
                'total_cotas': len(response.data),
                'total_grupos': len(grupos)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/historico', methods=['GET'])
def get_historico():
    """Retorna histórico de execuções"""
    try:
        if not supabase:
            return jsonify({'success': False, 'error': 'Banco de dados não disponível'})

        limit = request.args.get('limit', 50)

        response = supabase.table('historico_execucoes')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()

        return jsonify({
            'success': True,
            'data': response.data,
            'total': len(response.data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/automation/status', methods=['GET'])
def get_automation_status():
    """Retorna status das automações"""
    try:
        if not supabase:
            return jsonify({'success': False, 'error': 'Banco de dados não disponível'})

        response = supabase.table('automacao_status').select('*').execute()

        status_data = {}
        for status in response.data:
            dia = status.get('dia')
            status_data[dia] = status

        return jsonify({
            'success': True,
            'data': status_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """Inicia automação para um dia específico"""
    try:
        data = request.get_json()
        dia = data.get('dia', '08')

        # Verifica se já está rodando
        if automation_threads.get(dia) and automation_threads[dia].is_alive():
            return jsonify({
                'success': False,
                'error': f'Automação do dia {dia} já está em execução'
            })

        # Atualiza status no banco
        if supabase:
            supabase.table('automacao_status')\
                .update({
                    'is_running': True,
                    'started_at': datetime.now().isoformat(),
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'failed_tasks': 0
                })\
                .eq('dia', dia)\
                .execute()

        # Inicia thread de automação (DEMO)
        thread = threading.Thread(
            target=simulate_automation,
            args=(dia,)
        )
        thread.daemon = True
        thread.start()
        automation_threads[dia] = thread

        return jsonify({
            'success': True,
            'message': f'Automação do dia {dia} iniciada com sucesso'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """Para automação para um dia específico"""
    try:
        data = request.get_json()
        dia = data.get('dia', '08')

        # Atualiza status no banco
        if supabase:
            supabase.table('automacao_status')\
                .update({'is_running': False})\
                .eq('dia', dia)\
                .execute()

        # Emite evento via WebSocket
        socketio.emit('automation_stopped', {'dia': dia})

        return jsonify({
            'success': True,
            'message': f'Automação do dia {dia} será parada'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ========================================
# WEBSOCKET EVENTS
# ========================================

@socketio.on('connect')
def handle_connect():
    """Cliente conectou via WebSocket"""
    print('🔌 Cliente conectado via WebSocket')
    emit('connected', {'message': 'Conectado ao servidor OXCASH'})


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectou"""
    print('🔌 Cliente desconectado')


# ========================================
# SIMULAÇÃO DE AUTOMAÇÃO (DEMO)
# ========================================

def simulate_automation(dia):
    """
    Simula uma automação para demonstração
    Em produção, aqui você chamaria as funções reais de automação
    """
    print(f"🤖 Iniciando simulação de automação para dia {dia}")

    # Simula 10 tarefas
    total_tasks = 10

    if supabase:
        supabase.table('automacao_status')\
            .update({'total_tasks': total_tasks})\
            .eq('dia', dia)\
            .execute()

    for i in range(1, total_tasks + 1):
        # Verifica se deve parar
        if supabase:
            status = supabase.table('automacao_status')\
                .select('is_running')\
                .eq('dia', dia)\
                .maybeSingle()\
                .execute()

            if status.data and not status.data.get('is_running'):
                print(f"⏹️ Automação dia {dia} foi parada")
                break

        # Simula processamento
        grupo = f"GRP-{dia}-{i:03d}"
        cota = f"COTA-{i:03d}"
        nome = f"Cliente {i}"

        # Emite progresso via WebSocket
        socketio.emit('automation_progress', {
            'dia': dia,
            'current_task': i,
            'total_tasks': total_tasks,
            'grupo': grupo,
            'cota': cota,
            'nome': nome,
            'message': f'Processando {nome}...'
        })

        # Simula tempo de processamento
        time.sleep(random.uniform(1, 3))

        # Simula sucesso/falha (90% sucesso)
        success = random.random() < 0.9

        # Atualiza banco de dados
        if supabase:
            # Atualiza contador
            supabase.table('automacao_status')\
                .update({
                    'completed_tasks': i,
                    'failed_tasks': 0 if success else 1,
                    'current_task': f'{grupo} - {cota}'
                })\
                .eq('dia', dia)\
                .execute()

            # Adiciona ao histórico
            supabase.table('historico_execucoes').insert({
                'dia': dia,
                'grupo': grupo,
                'cota': cota,
                'nome': nome,
                'valor_lance': f'{random.randint(10, 30)}',
                'status': '✅ Sucesso' if success else '❌ Erro',
                'observacao': 'Lance registrado com sucesso' if success else 'Erro ao processar lance',
                'protocolo': f'PROT-{dia}-{i:05d}' if success else None
            }).execute()

        # Emite resultado via WebSocket
        socketio.emit('task_completed', {
            'dia': dia,
            'grupo': grupo,
            'cota': cota,
            'nome': nome,
            'success': success,
            'current': i,
            'total': total_tasks
        })

    # Finaliza automação
    if supabase:
        supabase.table('automacao_status')\
            .update({
                'is_running': False,
                'current_task': 'Concluído'
            })\
            .eq('dia', dia)\
            .execute()

    socketio.emit('automation_complete', {
        'dia': dia,
        'message': f'Automação do dia {dia} concluída!'
    })

    print(f"✅ Simulação de automação dia {dia} concluída")


# ========================================
# INICIALIZAÇÃO
# ========================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 OXCASH - Sistema de Automação Moderno")
    print("=" * 60)
    print("📡 Backend API + WebSocket")
    print("💾 Banco de dados: Supabase")
    print("=" * 60)

    # Roda servidor com WebSocket
    socketio.run(app, debug=True, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
