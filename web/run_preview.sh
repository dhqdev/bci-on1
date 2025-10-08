#!/bin/bash

echo "========================================"
echo "🚀 OXCASH - Preview Arquitetura Web"
echo "========================================"
echo ""

# Verifica se está no diretório correto
if [ ! -f "app_preview.py" ]; then
    echo "❌ Erro: Execute este script na pasta 'web'"
    exit 1
fi

# Sobe para o diretório raiz do projeto
cd ..

echo "📦 Instalando dependências..."
pip install -q flask flask-socketio flask-cors supabase python-socketio[client]

echo ""
echo "✅ Dependências instaladas!"
echo ""
echo "🌐 Iniciando servidor..."
echo ""
echo "📡 Dashboard: http://localhost:5001"
echo "📊 API: http://localhost:5001/api/*"
echo "🔌 WebSocket: ws://localhost:5001"
echo ""
echo "========================================"
echo ""

# Exporta variáveis de ambiente
export FLASK_APP=web/app_preview.py
export FLASK_ENV=development

# Inicia o servidor
cd web
python3 app_preview.py
