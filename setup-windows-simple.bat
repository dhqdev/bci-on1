@echo off
REM setup-windows-simple.bat - Instalador Simplificado
REM Versão sem remoção automática de diretórios

setlocal enabledelayedexpansion

title BCI-ON1 Installer (Simple)
color 0B
cls

echo ============================================================
echo   BCI-ON1 - Instalador Simplificado
echo   Sistema de Automacao Servopa + Todoist
echo ============================================================
echo.

REM Install directory
set INSTALL_DIR=%USERPROFILE%\bci-on1

REM Verifica se já existe
if exist "%INSTALL_DIR%" (
    echo [!] ATENCAO: Ja existe uma instalacao em:
    echo     %INSTALL_DIR%
    echo.
    echo Para reinstalar:
    echo   1. Feche TODOS os programas (navegador, VS Code, etc.)
    echo   2. Delete a pasta manualmente:
    echo      Abra: %USERPROFILE%
    echo      Delete a pasta: bci-on1
    echo   3. Execute este instalador novamente
    echo.
    echo Para apenas atualizar, execute na pasta do projeto:
    echo      cd %INSTALL_DIR%
    echo      git pull origin main
    echo.
    pause
    exit /b 0
)

REM Check Git
echo [*] Verificando Git...
git --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] Git nao encontrado!
    echo     Baixe em: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git instalado

REM Check Python
echo [*] Verificando Python...
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [X] Python nao encontrado!
    echo     Baixe em: https://www.python.org/downloads/
    echo     IMPORTANTE: Marque "Add Python to PATH" durante instalacao
    pause
    exit /b 1
)
echo [OK] Python instalado

REM Check Chrome
echo [*] Verificando Chrome...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [!] Chrome nao encontrado!
    echo     Baixe em: https://www.google.com/chrome/
    echo     Continuando sem Chrome... (pode causar erros na automacao)
    ping localhost -n 3 >nul 2>&1
) else (
    echo [OK] Chrome instalado
)
echo.

REM Clone repo
echo [*] Clonando repositorio do GitHub...
git clone https://github.com/dhqdev/bci-on1.git "%INSTALL_DIR%"
if %errorLevel% NEQ 0 (
    echo [X] ERRO: Falha ao clonar repositorio
    echo     Verifique sua conexao com a internet
    pause
    exit /b 1
)
echo [OK] Repositorio clonado

REM Vai para o diretório
cd /d "%INSTALL_DIR%"

REM Run installer
echo.
echo [*] Executando instalador de dependencias...
echo.
call install.bat
if %errorLevel% NEQ 0 (
    echo [X] ERRO na instalacao de dependencias
    pause
    exit /b 1
)

REM Criar atalho na área de trabalho
echo.
echo [*] Criando atalho na area de trabalho...

set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_FILE=%DESKTOP%\BCI-ON1-Web.bat

echo @echo off > "%SHORTCUT_FILE%"
echo title BCI-ON1 - Interface Web >> "%SHORTCUT_FILE%"
echo color 0B >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo echo ========================================== >> "%SHORTCUT_FILE%"
echo echo   BCI-ON1 - Sistema de Automacao >> "%SHORTCUT_FILE%"
echo echo ========================================== >> "%SHORTCUT_FILE%"
echo echo. >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo cd /d "%INSTALL_DIR%" >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo if exist "venv\Scripts\activate.bat" ( >> "%SHORTCUT_FILE%"
echo     echo [+] Ativando ambiente virtual... >> "%SHORTCUT_FILE%"
echo     call venv\Scripts\activate.bat >> "%SHORTCUT_FILE%"
echo ) else ( >> "%SHORTCUT_FILE%"
echo     echo [!] ERRO: Ambiente virtual nao encontrado! >> "%SHORTCUT_FILE%"
echo     pause >> "%SHORTCUT_FILE%"
echo     exit /b 1 >> "%SHORTCUT_FILE%"
echo ) >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo echo. >> "%SHORTCUT_FILE%"
echo echo ========================================== >> "%SHORTCUT_FILE%"
echo echo Iniciando servidor web... >> "%SHORTCUT_FILE%"
echo echo ========================================== >> "%SHORTCUT_FILE%"
echo echo. >> "%SHORTCUT_FILE%"
echo echo Apos iniciar, abra seu navegador em: >> "%SHORTCUT_FILE%"
echo echo    http://localhost:5000 >> "%SHORTCUT_FILE%"
echo echo. >> "%SHORTCUT_FILE%"
echo echo Pressione CTRL+C para parar o servidor. >> "%SHORTCUT_FILE%"
echo echo ========================================== >> "%SHORTCUT_FILE%"
echo echo. >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo cd web >> "%SHORTCUT_FILE%"
echo python app.py >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo pause >> "%SHORTCUT_FILE%"

echo [OK] Atalho criado: %SHORTCUT_FILE%

echo.
echo ============================================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ============================================================
echo.
echo Projeto instalado em: %INSTALL_DIR%
echo.
echo ✅ Atalho criado na area de trabalho: BCI-ON1-Web.bat
echo.
echo Como executar:
echo   1. Clique no atalho "BCI-ON1-Web.bat" na area de trabalho
echo   2. Ou execute: cd %INSTALL_DIR%\web ^&^& run_web.bat
echo.
echo Apos iniciar, abra: http://localhost:5000
echo.
echo ============================================================
pause
