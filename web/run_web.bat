@echo off
REM run_web.bat
REM Script para iniciar interface web moderna no Windows

echo ==================================
echo 🚀 OXCASH - Interface Web Moderna
echo ==================================

REM Verifica Python
echo 📦 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Ativa ambiente virtual se existir
if exist venv\ (
    echo 🔧 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Instala dependências se necessário
if not exist .web_deps_installed (
    echo 📥 Instalando dependências web...
    pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
    echo. > .web_deps_installed
    echo ✅ Dependências instaladas
)

REM Inicia servidor Flask
echo.
echo ==================================
echo 🌐 Iniciando servidor web...
echo ==================================
echo.

cd web
python app.py
