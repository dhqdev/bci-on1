@echo off
echo ========================================
echo 🚀 OXCASH - Preview Arquitetura Web
echo ========================================
echo.

REM Verifica se está no diretório correto
if not exist "app_preview.py" (
    echo ❌ Erro: Execute este script na pasta 'web'
    exit /b 1
)

REM Sobe para o diretório raiz do projeto
cd ..

echo 📦 Instalando dependências...
pip install -q flask flask-socketio flask-cors supabase python-socketio[client]

echo.
echo ✅ Dependências instaladas!
echo.
echo 🌐 Iniciando servidor...
echo.
echo 📡 Dashboard: http://localhost:5001
echo 📊 API: http://localhost:5001/api/*
echo 🔌 WebSocket: ws://localhost:5001
echo.
echo ========================================
echo.

REM Inicia o servidor
cd web
python app_preview.py
