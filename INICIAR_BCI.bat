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
set "PYTHON_CMD="
set "PYTHON_VERSION="

for %%i in (python python3 py) do (
    for /f "usebackq tokens=*" %%j in (`%%i --version 2^>^&1`) do (
        set "PYTHON_CMD=%%i"
        set "PYTHON_VERSION=%%j"
        goto :python_check_done
    )
)

for %%p in ("%ProgramFiles%\Python312\python.exe" "%ProgramFiles%\Python311\python.exe" "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%LOCALAPPDATA%\Programs\Python\Python311\python.exe") do (
    if exist %%~p (
        call :add_path_if_needed "%%~dp"
        call :add_path_if_needed "%%~dpScripts"
    )
)

for %%i in (python python3 py) do (
    for /f "usebackq tokens=*" %%j in (`%%i --version 2^>^&1`) do (
        set "PYTHON_CMD=%%i"
        set "PYTHON_VERSION=%%j"
        goto :python_check_done
    )
)

:python_check_done
if not defined PYTHON_CMD (
    echo ❌ Python nao encontrado!
    echo.
    echo Execute o instalador:
    echo    irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 ^| iex
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado: %PYTHON_VERSION%
echo.

REM Ativa ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
    echo ✅ Ambiente virtual ativado
) else (
    echo ⚠️  Ambiente virtual nao encontrado
    echo Criando ambiente virtual...
    %PYTHON_CMD% -m venv venv
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
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
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
goto :EOF

:add_path_if_needed
if "%~1"=="" exit /b 0
echo %PATH% | find /I "%~1" >nul
if %errorlevel%==0 exit /b 0
set "PATH=%~1;%PATH%"
exit /b 0
