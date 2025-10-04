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

REM Detecta onde está o projeto - tenta vários locais
set PROJECT_DIR=

REM Tenta: onde este script está
if exist "%~dp0web\app.py" (
    set PROJECT_DIR=%~dp0
    goto :found
)

REM Tenta: Desktop do usuário
if exist "%USERPROFILE%\Desktop\bci-on1\web\app.py" (
    set PROJECT_DIR=%USERPROFILE%\Desktop\bci-on1
    goto :found
)

REM Tenta: Home do usuário
if exist "%USERPROFILE%\bci-on1\web\app.py" (
    set PROJECT_DIR=%USERPROFILE%\bci-on1
    goto :found
)

REM Não encontrou
echo ❌ ERRO: Projeto nao encontrado!
echo.
echo Execute primeiro o instalador:
echo    irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 ^| iex
echo.
pause
exit /b 1

:found
echo 📁 Diretorio do projeto: %PROJECT_DIR%
cd /d "%PROJECT_DIR%"
echo.

REM Verifica Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo.
    echo Execute o instalador novamente.
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
    echo Execute: install.bat
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 🌐 Iniciando servidor web...
echo ==========================================
echo.
echo 📌 Acesse no navegador:
echo    http://localhost:5000
echo.
echo ⚠️  Pressione CTRL+C para parar
echo ==========================================
echo.

REM Vai para o diretório web e inicia
cd web
python app.py

REM Se parar, mantém janela aberta
echo.
echo Servidor encerrado.
pause
