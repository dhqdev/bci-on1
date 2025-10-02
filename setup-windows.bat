@echo off
REM setup-windows.bat - BCI-ON1 Installer
REM Usage: irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.bat -OutFile setup.bat; .\setup.bat

title BCI-ON1 Installer
color 0B
cls

echo ============================================================
echo   BCI-ON1 - Instalador Automatico
echo   Sistema de Automacao Servopa + Todoist
echo ============================================================
echo.

REM Check Git
echo [*] Verificando Git...
git --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [!] Instalando Git...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe', 'git-installer.exe')"
    start /wait git-installer.exe /VERYSILENT /NORESTART
    del git-installer.exe
)
echo [OK] Git instalado

REM Check Python
echo [*] Verificando Python...
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [!] Instalando Python...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe', 'python-installer.exe')"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
)
echo [OK] Python instalado

REM Check Chrome
echo [*] Verificando Chrome...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [!] Instalando Chrome...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://dl.google.com/chrome/install/375.126/chrome_installer.exe', 'chrome_installer.exe')"
    start /wait chrome_installer.exe /silent /install
    del chrome_installer.exe
)
echo [OK] Chrome instalado
echo.

REM Install directory
set INSTALL_DIR=%USERPROFILE%\bci-on1
if exist "%INSTALL_DIR%" (
    echo [!] Diretorio ja existe
    set /p "remove=Remover e reinstalar? [s/N]: "
    if /i "%remove%"=="s" (
        rd /s /q "%INSTALL_DIR%"
    ) else (
        exit /b 0
    )
)

REM Clone repo
echo [*] Clonando repositorio...
git clone https://github.com/dhqdev/bci-on1.git "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

# Run installer
echo [*] Executando instalador...
echo.
call install.bat

REM Criar atalho na área de trabalho
echo.
echo [*] Criando atalho na area de trabalho...

REM Cria arquivo BAT na área de trabalho
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
echo REM Vai para o diretorio do projeto >> "%SHORTCUT_FILE%"
echo cd /d "%INSTALL_DIR%" >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo REM Ativa ambiente virtual >> "%SHORTCUT_FILE%"
echo if exist "venv\Scripts\activate.bat" ( >> "%SHORTCUT_FILE%"
echo     echo [+] Ativando ambiente virtual... >> "%SHORTCUT_FILE%"
echo     call venv\Scripts\activate.bat >> "%SHORTCUT_FILE%"
echo ) else ( >> "%SHORTCUT_FILE%"
echo     echo [!] ERRO: Ambiente virtual nao encontrado! >> "%SHORTCUT_FILE%"
echo     echo Execute o instalador novamente. >> "%SHORTCUT_FILE%"
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
echo REM Inicia servidor >> "%SHORTCUT_FILE%"
echo cd web >> "%SHORTCUT_FILE%"
echo python app.py >> "%SHORTCUT_FILE%"
echo. >> "%SHORTCUT_FILE%"
echo pause >> "%SHORTCUT_FILE%"

echo [OK] Atalho criado: %SHORTCUT_FILE%

echo.
echo ============================================================
echo   INSTALACAO CONCLUIDA!
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
pause
