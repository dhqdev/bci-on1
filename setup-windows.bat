@echo off
REM setup-windows.bat - Instalador Automático BCI-ON1 (Windows)
REM Pode ser executado diretamente do PowerShell (como Administrador):
REM irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.bat -OutFile setup.bat; .\setup.bat

title BCI-ON1 - Instalador Automático

color 0B
cls

echo ================================================================
echo.
echo     🤖 BCI-ON1 - Instalador Automático
echo        Sistema de Automação Servopa + Todoist
echo.
echo ================================================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Executando como administrador
) else (
    echo [AVISO] Não está executando como administrador
    echo [AVISO] Algumas instalações podem falhar
    echo.
    pause
)

echo.

REM 1. Verificar Git
echo [INFO] Verificando Git...

git --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=3" %%i in ('git --version') do echo [OK] Git encontrado: %%i
    goto :check_python
)

echo [INFO] Git não encontrado. Instalando...

REM Baixar Git usando PowerShell
echo [INFO] Baixando Git para Windows...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe', 'git-installer.exe')"

if exist git-installer.exe (
    echo [INFO] Instalando Git...
    start /wait git-installer.exe /VERYSILENT /NORESTART
    del git-installer.exe
    echo [OK] Git instalado!
) else (
    echo [ERRO] Falha ao baixar Git
    echo [INFO] Baixe manualmente: https://git-scm.com/download/win
    pause
    exit /b 1
)

:check_python
echo.
echo [INFO] Verificando Python...

python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version') do echo [OK] Python encontrado: %%i
    set PYTHON_CMD=python
    goto :check_chrome
)

python3 --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python3 --version') do echo [OK] Python3 encontrado: %%i
    set PYTHON_CMD=python3
    goto :check_chrome
)

py --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('py --version') do echo [OK] Python (py) encontrado: %%i
    set PYTHON_CMD=py
    goto :check_chrome
)

echo [INFO] Python não encontrado. Instalando...

REM Baixar Python usando PowerShell
echo [INFO] Baixando Python 3.11 (64-bit)...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe', 'python-installer.exe')"

if exist python-installer.exe (
    echo [INFO] Instalando Python...
    echo [INFO] IMPORTANTE: Python será instalado com Add to PATH
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python-installer.exe
    echo [OK] Python instalado!
    set PYTHON_CMD=python
) else (
    echo [ERRO] Falha ao baixar Python
    echo [INFO] Baixe manualmente: https://www.python.org/downloads/
    pause
    exit /b 1
)

:check_chrome
echo.
echo [INFO] Verificando Google Chrome...

reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Google Chrome encontrado
    goto :clone_repo
)

reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" /v version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Google Chrome encontrado
    goto :clone_repo
)

where chrome >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Google Chrome encontrado
    goto :clone_repo
)

echo [INFO] Google Chrome não encontrado. Instalando...

powershell -Command "(New-Object Net.WebClient).DownloadFile('https://dl.google.com/chrome/install/375.126/chrome_installer.exe', 'chrome_installer.exe')"

if exist chrome_installer.exe (
    echo [INFO] Instalando Google Chrome...
    start /wait chrome_installer.exe /silent /install
    del chrome_installer.exe
    echo [OK] Google Chrome instalado!
) else (
    echo [AVISO] Falha ao baixar Chrome
    echo [INFO] Instale manualmente: https://www.google.com/chrome/
)

:clone_repo
echo.
echo [INFO] Escolhendo diretório de instalação...

set INSTALL_DIR=%USERPROFILE%\bci-on1

if exist "%INSTALL_DIR%" (
    echo [AVISO] Diretório %INSTALL_DIR% já existe!
    set /p "remove=Deseja remover e reinstalar? [s/N]: "
    if /i "%remove%"=="s" (
        echo [INFO] Removendo diretório antigo...
        rd /s /q "%INSTALL_DIR%"
        echo [OK] Diretório removido!
    ) else (
        echo [INFO] Instalação cancelada.
        pause
        exit /b 0
    )
)

echo.
echo [INFO] Clonando repositório do GitHub...

git clone https://github.com/dhqdev/bci-on1.git "%INSTALL_DIR%"

if %errorLevel% == 0 (
    echo [OK] Repositório clonado com sucesso!
) else (
    echo [ERRO] Falha ao clonar repositório
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

echo.
echo [INFO] Executando instalador local...
echo.

call install.bat

if %errorLevel% == 0 (
    echo.
    echo ================================================================
    echo.
    echo     ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
    echo.
    echo ================================================================
    echo.
    echo 📍 Projeto instalado em: %INSTALL_DIR%
    echo.
    echo 🚀 Como executar:
    echo.
    echo    Interface Desktop:
    echo    cd %INSTALL_DIR%
    echo    run.bat
    echo.
    echo    Interface Web:
    echo    cd %INSTALL_DIR%
    echo    cd web
    echo    run_web.bat
    echo    Depois acesse: http://localhost:5000
    echo.
    echo ================================================================
    echo.
) else (
    echo [ERRO] Falha na instalação
    pause
    exit /b 1
)

pause
