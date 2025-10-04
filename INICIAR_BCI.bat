@echo off
REM ===============================================
REM  🚀 BCI-ON1 - INICIALIZADOR WEB
REM  Atalho executável para iniciar a interface
REM ===============================================

title BCI-ON1 - Interface Web
color 0B

echo ==========================================
echo   🚀 BCI-ON1 - Sistema de Automacao
echo ==========================================
echo.

REM Detecta o diretório onde este script está
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo 📁 Diretorio do projeto: %SCRIPT_DIR%
echo.

REM Verifica se o projeto existe
if not exist "web\app.py" (
    echo ❌ ERRO: Arquivos do projeto nao encontrados!
    echo.
    echo Verifique se o projeto foi instalado corretamente.
    echo Execute: install.bat
    echo.
    pause
    exit /b 1
)

REM Verifica Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo.
    echo Execute o instalador:
    echo    irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 ^| iex
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Ativa ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
    echo ✅ Ambiente virtual ativado
) else (
    echo ⚠️  Ambiente virtual nao encontrado
    echo Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
)

echo.

REM Instala dependências se necessário
if not exist ".web_deps_installed" (
    echo 📥 Instalando dependencias web...
    pip install --upgrade pip
    pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar dependencias
        pause
        exit /b 1
    )
    echo. > .web_deps_installed
    echo ✅ Dependencias instaladas
)

echo.
echo ==========================================
echo 🌐 Iniciando servidor web...
echo ==========================================
echo.
echo 📌 Acesse no navegador:
echo    http://localhost:5000
echo.
echo ⚠️  Pressione CTRL+C para parar o servidor
echo ==========================================
echo.

REM Muda para diretório web e inicia o servidor
cd web
python app.py

REM Se o servidor parar, mantém a janela aberta
echo.
echo.
echo Servidor encerrado.
pause
