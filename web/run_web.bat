@echo off
REM run_web.bat
REM Script para iniciar interface web moderna no Windows

title BCI-ON1 - Interface Web

echo ==================================
echo 🚀 BCI-ON1 - Interface Web
echo ==================================
echo.

REM Volta para o diretório raiz do projeto
cd /d "%~dp0\.."

REM Verifica Python
echo 📦 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo.
    echo Execute o instalador primeiro:
    echo    install.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Ativa ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    echo 🔧 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
    echo ✅ Ambiente virtual ativado
) else (
    echo ⚠️  Ambiente virtual não encontrado
    echo Execute o instalador primeiro: install.bat
    echo.
    pause
    exit /b 1
)

REM Instala dependências web se necessário
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
echo Após iniciar, abra seu navegador em:
echo    http://localhost:5000
echo.
echo Pressione CTRL+C para parar o servidor.
echo ==================================
echo.

cd web
python app.py

