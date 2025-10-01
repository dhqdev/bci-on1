@echo off
REM setup-windows.bat - Instalador Autônomo para Windows
REM Sistema de Automação Servopa + Todoist
REM 
REM COMO USAR:
REM 1. Baixe este arquivo
REM 2. Clique com botão direito e "Executar como administrador"

setlocal enabledelayedexpansion
title Instalador do Sistema de Automação Servopa + Todoist

color 0B
cls

echo ================================================================
echo.
echo     🤖 Sistema de Automação Servopa + Todoist
echo        Instalador Automático Completo para Windows
echo.
echo ================================================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR!
    echo.
    echo Clique com o botão direito no arquivo e selecione:
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Executando como administrador
echo.

REM Definir diretório de instalação
set "INSTALL_DIR=%USERPROFILE%\auto-oxbci"
set "REPO_URL=https://github.com/dhqdev/auto-oxbci.git"

echo [INFO] Sistema: Windows
echo [INFO] Usuário: %USERNAME%
echo [INFO] Diretório de instalação: %INSTALL_DIR%
echo.
echo.
echo Esta instalação irá:
echo   1. Instalar Python (se necessário)
echo   2. Instalar Git (se necessário)
echo   3. Instalar Google Chrome (se necessário)
echo   4. Clonar o repositório do GitHub
echo   5. Configurar ambiente virtual Python
echo   6. Instalar todas as dependências
echo   7. Criar atalhos de execução
echo.

set /p "continue=Deseja continuar? (S/n): "
if /i not "%continue%"=="s" if /i not "%continue%"=="" (
    echo [INFO] Instalação cancelada pelo usuário
    pause
    exit /b 0
)

echo.
echo ================================================================
echo [ETAPA 1/7] Verificando Python...
echo ================================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        echo [OK] Python encontrado: %%i
        set PYTHON_CMD=python
        goto :check_git
    )
)

py --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('py --version 2^>^&1') do (
        echo [OK] Python encontrado: %%i
        set PYTHON_CMD=py
        goto :check_git
    )
)

echo [AVISO] Python não encontrado!
echo [INFO] Baixando Python 3.11...

REM Baixar Python usando PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%TEMP%\python-installer.exe'}"

if exist "%TEMP%\python-installer.exe" (
    echo [INFO] Instalando Python...
    echo [INFO] Aguarde, isto pode levar alguns minutos...
    
    start /wait "" "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_tcltk=1
    
    del "%TEMP%\python-installer.exe"
    
    REM Atualizar PATH
    call :refresh_env
    
    python --version >nul 2>&1
    if %errorLevel% == 0 (
        echo [OK] Python instalado com sucesso!
        set PYTHON_CMD=python
    ) else (
        echo [ERRO] Falha na instalação do Python
        echo [INFO] Baixe manualmente de: https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    echo [ERRO] Falha ao baixar Python
    echo [INFO] Baixe manualmente de: https://www.python.org/downloads/
    pause
    exit /b 1
)

:check_git
echo.
echo ================================================================
echo [ETAPA 2/7] Verificando Git...
echo ================================================================
echo.

git --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do (
        echo [OK] Git encontrado: %%i
        goto :check_chrome
    )
)

echo [AVISO] Git não encontrado!
echo [INFO] Baixando Git...

REM Baixar Git
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe' -OutFile '%TEMP%\git-installer.exe'}"

if exist "%TEMP%\git-installer.exe" (
    echo [INFO] Instalando Git...
    echo [INFO] Aguarde, isto pode levar alguns minutos...
    
    start /wait "" "%TEMP%\git-installer.exe" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
    
    del "%TEMP%\git-installer.exe"
    
    REM Atualizar PATH
    call :refresh_env
    
    git --version >nul 2>&1
    if %errorLevel% == 0 (
        echo [OK] Git instalado com sucesso!
    ) else (
        echo [ERRO] Falha na instalação do Git
        echo [INFO] Baixe manualmente de: https://git-scm.com/download/win
        pause
        exit /b 1
    )
) else (
    echo [ERRO] Falha ao baixar Git
    pause
    exit /b 1
)

:check_chrome
echo.
echo ================================================================
echo [ETAPA 3/7] Verificando Google Chrome...
echo ================================================================
echo.

reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Google Chrome encontrado
    goto :clone_repo
)

reg query "HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\BLBeacon" >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Google Chrome encontrado
    goto :clone_repo
)

echo [AVISO] Google Chrome não encontrado!
echo [INFO] Baixando Google Chrome...

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://dl.google.com/chrome/install/latest/chrome_installer.exe' -OutFile '%TEMP%\chrome_installer.exe'}"

if exist "%TEMP%\chrome_installer.exe" (
    echo [INFO] Instalando Google Chrome...
    start /wait "" "%TEMP%\chrome_installer.exe" /silent /install
    del "%TEMP%\chrome_installer.exe"
    echo [OK] Google Chrome instalado!
) else (
    echo [AVISO] Falha ao baixar Chrome
    echo [INFO] Baixe manualmente de: https://www.google.com/chrome/
)

:clone_repo
echo.
echo ================================================================
echo [ETAPA 4/7] Clonando repositório do GitHub...
echo ================================================================
echo.

if exist "%INSTALL_DIR%" (
    echo [AVISO] Diretório já existe
    echo [INFO] Atualizando repositório...
    cd /d "%INSTALL_DIR%"
    git pull origin main
) else (
    echo [INFO] Clonando repositório...
    git clone "%REPO_URL%" "%INSTALL_DIR%"
    
    if %errorLevel% neq 0 (
        echo [ERRO] Falha ao clonar repositório
        pause
        exit /b 1
    )
    
    cd /d "%INSTALL_DIR%"
)

echo [OK] Repositório configurado!

:create_venv
echo.
echo ================================================================
echo [ETAPA 5/7] Criando ambiente virtual Python...
echo ================================================================
echo.

if exist "venv" (
    echo [INFO] Removendo ambiente virtual antigo...
    rmdir /s /q venv
)

echo [INFO] Criando novo ambiente virtual...
%PYTHON_CMD% -m venv venv

if exist "venv\Scripts\activate.bat" (
    echo [OK] Ambiente virtual criado!
) else (
    echo [ERRO] Falha ao criar ambiente virtual
    pause
    exit /b 1
)

:install_deps
echo.
echo ================================================================
echo [ETAPA 6/7] Instalando dependências Python...
echo ================================================================
echo.

echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Atualizando pip...
python -m pip install --upgrade pip --quiet

echo [INFO] Instalando dependências...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt --quiet
) else (
    python -m pip install selenium webdriver-manager requests beautifulsoup4 python-dotenv --quiet
)

echo [OK] Dependências instaladas!

:verify
echo.
echo [INFO] Verificando instalação...

python -c "import selenium; from webdriver_manager.chrome import ChromeDriverManager; import tkinter; import requests; from bs4 import BeautifulSoup; print('[OK] Todas as dependências verificadas!')" 2>nul

if %errorLevel% neq 0 (
    echo [ERRO] Falha na verificação de dependências
    pause
    exit /b 1
)

:create_shortcuts
echo.
echo ================================================================
echo [ETAPA 7/7] Criando atalhos de execução...
echo ================================================================
echo.

REM Criar arquivo run.bat atualizado
echo @echo off > run.bat
echo title Sistema de Automação Servopa + Todoist >> run.bat
echo cd /d "%%~dp0" >> run.bat
echo echo Ativando ambiente virtual... >> run.bat
echo call venv\Scripts\activate.bat >> run.bat
echo echo. >> run.bat
echo echo Iniciando sistema... >> run.bat
echo python main_gui.py >> run.bat
echo echo. >> run.bat
echo echo Sistema encerrado. >> run.bat
echo pause >> run.bat

echo [OK] Arquivo run.bat criado!

REM Criar atalho na área de trabalho
set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Área de Trabalho"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\Auto OXBCI.lnk'); $s.TargetPath = '%INSTALL_DIR%\run.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.IconLocation = 'shell32.dll,21'; $s.Description = 'Sistema de Automação Servopa + Todoist'; $s.Save()" >nul 2>&1

if exist "%DESKTOP%\Auto OXBCI.lnk" (
    echo [OK] Atalho criado na área de trabalho!
)

REM Atualizar install.bat para ativar venv automaticamente
if exist "install.bat" (
    echo. >> install.bat
    echo echo. >> install.bat
    echo echo [INFO] Ativando ambiente virtual automaticamente... >> install.bat
    echo call venv\Scripts\activate.bat >> install.bat
    echo echo [OK] Ambiente virtual ativado! Você já está dentro do ambiente. >> install.bat
    echo echo [INFO] Para sair do ambiente virtual, digite: deactivate >> install.bat
    echo echo. >> install.bat
)

echo.
echo ================================================================
echo.
echo     🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo.
echo ================================================================
echo.
echo 📂 Localização: %INSTALL_DIR%
echo.
echo 🚀 Como executar:
echo.
echo    1. Clique duas vezes no atalho "Auto OXBCI" na área de trabalho
echo.
echo    2. OU execute: %INSTALL_DIR%\run.bat
echo.
echo    3. OU via linha de comando:
echo       cd %INSTALL_DIR%
echo       run.bat
echo.
echo ================================================================
echo.

REM Perguntar se quer executar agora
set /p "run_now=Deseja executar o sistema agora? (S/n): "
if /i "%run_now%"=="s" if /i "%run_now%"=="" (
    echo.
    echo [INFO] Iniciando sistema...
    echo.
    call run.bat
) else (
    pause
)

exit /b 0

REM Função para atualizar variáveis de ambiente
:refresh_env
setlocal
for /f "tokens=2*" %%a in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "syspath=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "userpath=%%b"
set "PATH=%syspath%;%userpath%"
endlocal & set "PATH=%PATH%"
goto :eof
