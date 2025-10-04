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
set "PYTHON_CMD="
set "PYTHON_VERSION="

for %%i in (python python3 py) do (
    for /f "usebackq tokens=*" %%j in (`%%i --version 2^>^&1`) do (
        set "PYTHON_CMD=%%i"
        set "PYTHON_VERSION=%%j"
        goto :python_found
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
        goto :python_found
    )
)

:python_found
if not defined PYTHON_CMD (
    echo ❌ Python não encontrado!
    echo.
    echo Execute o instalador primeiro:
    echo    install.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado: %PYTHON_VERSION%

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
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
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

goto :EOF

:add_path_if_needed
if "%~1"=="" exit /b 0
echo %PATH% | find /I "%~1" >nul
if %errorlevel%==0 exit /b 0
set "PATH=%~1;%PATH%"
exit /b 0

