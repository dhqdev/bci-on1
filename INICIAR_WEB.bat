@echo off
title BCI-ON1 - Interface Web
color 0B

REM Este é o atalho criado automaticamente pelo instalador
REM Ele inicia a interface web do BCI-ON1

echo ==========================================
echo   BCI-ON1 - Sistema de Automacao
echo ==========================================
echo.

REM Detecta onde está o projeto
set PROJECT_DIR=%USERPROFILE%\bci-on1

REM Se não existir no local padrão, tenta no diretório atual
if not exist "%PROJECT_DIR%" (
    set PROJECT_DIR=%~dp0
)

echo Diretorio do projeto: %PROJECT_DIR%
echo.

REM Vai para o diretório do projeto
cd /d "%PROJECT_DIR%"

REM Verifica se o projeto existe
if not exist "web\app.py" (
    echo ❌ ERRO: Projeto nao encontrado!
    echo.
    echo Execute primeiro o instalador:
    echo    irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.bat -OutFile setup.bat; .\setup.bat
    echo.
    pause
    exit /b 1
)

REM Ativa ambiente virtual
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

echo.
echo ==========================================
echo 🌐 Iniciando servidor web...
echo ==========================================
echo.
echo Apos iniciar, abra seu navegador em:
echo    http://localhost:5000
echo.
echo Pressione CTRL+C para parar o servidor.
echo ==========================================
echo.

REM Vai para pasta web e inicia
cd web
python app.py

pause
