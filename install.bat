@echo off
REM install.bat - Script de instalação completa para Windows
REM Sistema de Automação Servopa + Todoist

title Instalação do Sistema de Automação Servopa + Todoist

echo ==========================================
echo 🤖 Instalação Automática do Sistema
echo Sistema de Automação Servopa + Todoist
echo ==========================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [⚠] Executando como administrador - OK
) else (
    echo [⚠] AVISO: Não está executando como administrador
    echo [⚠] Algumas instalações podem falhar
    echo.
    pause
)

echo [INFO] Sistema: Windows
echo.

REM 1. Verificar Python
echo [INFO] Verificando Python...

set "PYTHON_CMD="
set "PYTHON_VERSION_DISPLAY="
call :detect_python

if defined PYTHON_CMD (
    echo [✓] Python encontrado: %PYTHON_VERSION_DISPLAY%
    goto :check_pip
)

echo [⚠] Python não encontrado. Tentando instalar automaticamente...
call :install_python

if "%PY_INSTALL_SUCCESS%"=="1" (
    call :detect_python
)

if defined PYTHON_CMD (
    echo [✓] Python instalado: %PYTHON_VERSION_DISPLAY%
) else (
    echo [✗] Não foi possível instalar Python automaticamente.
    echo [INFO] Instale manualmente em: https://www.python.org/downloads/
    pause
    exit /b 1
)

:check_pip
echo.
echo [INFO] Verificando pip...

%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] pip encontrado
) else (
    echo [INFO] Instalando pip...
    %PYTHON_CMD% -m ensurepip --upgrade
    
    %PYTHON_CMD% -m pip --version >nul 2>&1
    if %errorLevel% == 0 (
        echo [✓] pip instalado com sucesso!
    ) else (
        echo [✗] Falha na instalação do pip
        pause
        exit /b 1
    )
)

echo.

REM 2. Verificar Google Chrome
echo [INFO] Verificando Google Chrome...

reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Google Chrome encontrado
    goto :create_venv
)

reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" /v version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Google Chrome encontrado
    goto :create_venv
)

where chrome >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Google Chrome encontrado
    goto :create_venv
)

echo [⚠] Google Chrome não encontrado
echo [INFO] Baixando Google Chrome...

powershell -Command "(New-Object Net.WebClient).DownloadFile('https://dl.google.com/chrome/install/375.126/chrome_installer.exe', 'chrome_installer.exe')"

if exist chrome_installer.exe (
    echo [INFO] Instalando Google Chrome...
    start /wait chrome_installer.exe /silent /install
    del chrome_installer.exe
    echo [✓] Google Chrome instalado!
) else (
    echo [⚠] Falha ao baixar Chrome. Baixe manualmente de: https://www.google.com/chrome/
)

:create_venv
echo.
echo [INFO] Criando ambiente virtual...

if exist venv (
    echo [⚠] Ambiente virtual já existe. Removendo...
    rmdir /s /q venv
)

%PYTHON_CMD% -m venv venv

if exist venv (
    echo [✓] Ambiente virtual criado!
) else (
    echo [✗] Falha na criação do ambiente virtual
    pause
    exit /b 1
)

echo.

REM 3. Ativar ambiente virtual e instalar dependências
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Atualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando dependências Python do requirements.txt...
if exist requirements.txt (
    python -m pip install -r requirements.txt
    if %errorLevel% == 0 (
        echo [✓] Todas as dependências instaladas com sucesso!
    ) else (
        echo [!] Algumas dependências podem ter falhado, mas continuando...
    )
) else (
    echo [!] requirements.txt não encontrado, instalando dependências básicas...
    python -m pip install selenium webdriver-manager requests pdfplumber beautifulsoup4 python-dotenv schedule Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
)

echo [✓] Dependências Python instaladas!
echo.

REM 4. Verificar estrutura de arquivos
echo [INFO] Verificando estrutura de arquivos...

set files_ok=1

if not exist main_gui.py (
    echo [⚠] main_gui.py não encontrado
    set files_ok=0
)

if not exist requirements.txt (
    echo [⚠] requirements.txt não encontrado
    set files_ok=0
)

if not exist credentials.json (
    echo [⚠] credentials.json não encontrado
    set files_ok=0
)

if not exist auth\servopa_auth.py (
    echo [⚠] auth\servopa_auth.py não encontrado
    set files_ok=0
)

if not exist auth\todoist_auth.py (
    echo [⚠] auth\todoist_auth.py não encontrado  
    set files_ok=0
)

if not exist ui\modern_automation_gui.py (
    echo [⚠] ui\modern_automation_gui.py não encontrado
    set files_ok=0
)

if %files_ok%==1 (
    echo [✓] Todos os arquivos necessários estão presentes!
) else (
    echo [⚠] Alguns arquivos estão ausentes. Verifique a estrutura do projeto.
)

echo.

REM 5. Testar instalação
echo [INFO] Testando instalação...

python -c "import selenium; from webdriver_manager.chrome import ChromeDriverManager; import tkinter as tk; import requests; from bs4 import BeautifulSoup; import schedule; import pdfplumber; import flask; from flask_socketio import SocketIO; from flask_cors import CORS; print('✓ Todas as dependências OK!')" 2>nul

if %errorLevel% == 0 (
    echo [✓] Teste de dependências passou!
) else (
    echo [✗] Teste de dependências falhou!
    echo [INFO] Verifique se todas as dependências foram instaladas corretamente
)

echo.

echo [INFO] Verificando integridade do código...
python -m compileall automation web >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Código compilado com sucesso (automation/, web/)
) else (
    echo [⚠] Aviso: falha ao compilar automation/ ou web/. Verifique mensagens acima.
)

echo [INFO] Testando extração de protocolo...
python test_protocol_flow_complete.py >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Teste de protocolo executado com sucesso!
) else (
    echo [⚠] Aviso: teste de protocolo encontrou problemas. Veja test_protocol_flow_complete.py.
)

echo.

REM 5.5. Criar arquivo de configuração da Evolution API
echo [INFO] Verificando arquivo de configuração da Evolution API...

if not exist evolution_config.json (
    echo [INFO] Criando evolution_config.json...
    
    (
        echo {
        echo   "api": {
        echo     "base_url": "https://zap.tekvosoft.com",
        echo     "instance_name": "david -tekvo",
        echo     "api_key": "634A7E882CE5-4314-8C5B-BC79C0A9EBBA"
        echo   },
        echo   "grupos": {
        echo     "grupo1": {
        echo       "nome": "Grupo 1 - Clientes Principal",
        echo       "contatos": [
        echo         {
        echo           "phone": "5519995378302",
        echo           "name": "João Silva"
        echo         },
        echo         {
        echo           "phone": "5519988776655",
        echo           "name": "Maria Santos"
        echo         }
        echo       ]
        echo     },
        echo     "grupo2": {
        echo       "nome": "Grupo 2 - Clientes Secundário",
        echo       "contatos": [
        echo         {
        echo           "phone": "5519977665544",
        echo           "name": "Ana Costa"
        echo         },
        echo         {
        echo           "phone": "5519966554433",
        echo           "name": "Carlos Oliveira"
        echo         }
        echo       ]
        echo     }
        echo   },
        echo   "mensagens": {
        echo     "dia7": {
        echo       "grupo1": "Olá {nome}! 🎉\n\nLembrando que hoje, dia 7, é o último dia para enviar seus lances!\n\nNão perca essa oportunidade! ⏰",
        echo       "grupo2": "Oi {nome}! 📢\n\nAviso importante: hoje é dia 7 e você tem até o final do dia para enviar seus lances.\n\nQualquer dúvida, estamos à disposição! 💪"
        echo     },
        echo     "dia15": {
        echo       "grupo1": "Olá {nome}! 🎯\n\nHoje é dia 15! Último dia para enviar seus lances.\n\nVamos lá, não deixe passar! 🚀",
        echo       "grupo2": "Oi {nome}! ⏰\n\nLembrando: dia 15 é o prazo final para lances!\n\nConte conosco para ajudar! 📞"
        echo     }
        echo   },
        echo   "agendamento": {
        echo     "enabled": false,
        echo     "horario_envio": "09:00",
        echo     "dias_para_enviar": [7, 15]
        echo   },
        echo   "configuracoes": {
        echo     "delay_entre_mensagens": 2.0,
        echo     "tentar_reenviar_falhas": true,
        echo     "max_tentativas": 3
        echo   }
        echo }
    ) > evolution_config.json
    
    echo [✓] Arquivo evolution_config.json criado!
) else (
    echo [✓] Arquivo evolution_config.json já existe!
)

echo.

REM 6. Criar arquivo de execução rápida
echo [INFO] Criando arquivo de execução rápida...

echo @echo off > run.bat
echo title Sistema de Automação Servopa + Todoist >> run.bat
echo echo Ativando ambiente virtual... >> run.bat
echo call venv\Scripts\activate.bat >> run.bat
echo echo Iniciando sistema... >> run.bat
echo python main_gui.py >> run.bat
echo pause >> run.bat

echo [✓] Arquivo run.bat criado!

echo.

REM 6.5. Criar ícone personalizado e atalho
echo [INFO] Criando ícone personalizado OXCASH...

REM Verificar se Pillow está instalado
python -c "import PIL" >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Instalando Pillow para criar ícone...
    python -m pip install Pillow
)

REM Criar ícone
python create_icon.py >nul 2>&1
if exist oxcash_icon.ico (
    echo [✓] Ícone personalizado criado!
) else (
    echo [⚠] Não foi possível criar ícone personalizado
)

REM Criar atalho na área de trabalho com ícone
echo [INFO] Criando atalho na área de trabalho...

set SCRIPT_TEMP="%TEMP%\create_bci_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT_TEMP%
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\BCI-ON1 Web.lnk" >> %SCRIPT_TEMP%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT_TEMP%
echo oLink.TargetPath = "%cd%\web\run_web.bat" >> %SCRIPT_TEMP%
echo oLink.WorkingDirectory = "%cd%" >> %SCRIPT_TEMP%
echo oLink.Description = "BCI-ON1 - Interface Web OXCASH" >> %SCRIPT_TEMP%
if exist oxcash_icon.ico (
    echo oLink.IconLocation = "%cd%\oxcash_icon.ico" >> %SCRIPT_TEMP%
)
echo oLink.Save >> %SCRIPT_TEMP%

cscript //nologo %SCRIPT_TEMP% >nul 2>&1
del %SCRIPT_TEMP%

echo [✓] Atalho criado na área de trabalho!

echo.
echo ==========================================
echo [✓] 🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ==========================================
echo.
echo [INFO] Como executar o sistema:
echo.
echo Interface Web (Recomendado):
echo    🖱️  Clique no atalho "BCI-ON1 Web" na área de trabalho
echo    📁 Ou execute: web\run_web.bat
echo    🌐 Depois acesse: http://localhost:5000
echo.
echo Interface Desktop (Legado):
echo    📁 Execute: run.bat
echo.
echo 🎨 Ícone personalizado criado!
echo 🔗 Atalho criado na área de trabalho!
echo.
echo [INFO] Sistema pronto para uso! 🚀
echo.

REM Ativar ambiente virtual automaticamente
echo ==========================================
echo [INFO] Ativando ambiente virtual automaticamente...
echo ==========================================
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [✓] Ambiente virtual ativado!
    echo.
    echo [INFO] Você já está dentro do ambiente virtual Python.
    echo [INFO] Agora você pode executar diretamente: python main_gui.py
    echo.
    echo [INFO] Para sair do ambiente virtual, digite: deactivate
    echo.
)

REM Perguntar se quer executar agora
set /p choice="Deseja executar o sistema agora? (s/n): "
if /i "%choice%"=="s" (
    echo.
    echo [INFO] Iniciando sistema...
    python main_gui.py
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul
goto :EOF

:detect_python
set "PYTHON_CMD="
set "PYTHON_VERSION_DISPLAY="
for %%i in (python python3 py) do (
    for /f "usebackq tokens=*" %%j in (`%%i --version 2^>^&1`) do (
        echo %%j | findstr /R /C:"Python [0-9][0-9]*\.[0-9]" >nul
        if not errorlevel 1 (
            set "PYTHON_CMD=%%i"
            set "PYTHON_VERSION_DISPLAY=%%j"
            goto detect_python_end
        )
    )
)
call :ensure_python_path
for %%i in (python python3 py) do (
    for /f "usebackq tokens=*" %%j in (`%%i --version 2^>^&1`) do (
        echo %%j | findstr /R /C:"Python [0-9][0-9]*\.[0-9]" >nul
        if not errorlevel 1 (
            set "PYTHON_CMD=%%i"
            set "PYTHON_VERSION_DISPLAY=%%j"
            goto detect_python_end
        )
    )
)
for %%p in ("C:\Program Files\Python312\python.exe" "C:\Program Files\Python311\python.exe" "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%LOCALAPPDATA%\Programs\Python\Python311\python.exe") do (
    if exist %%~p (
        for /f "usebackq tokens=*" %%j in (`"%%~p" --version 2^>^&1`) do (
            echo %%j | findstr /R /C:"Python [0-9][0-9]*\.[0-9]" >nul
            if not errorlevel 1 (
                set "PYTHON_CMD="%%~p""
                set "PYTHON_VERSION_DISPLAY=%%j"
                goto detect_python_end
            )
        )
    )
)
:detect_python_end
exit /b 0

:ensure_python_path
for %%p in ("C:\Program Files\Python312" "C:\Program Files\Python311" "%LOCALAPPDATA%\Programs\Python\Python312" "%LOCALAPPDATA%\Programs\Python\Python311") do (
    if exist %%~p\python.exe (
        call :append_path "%%~p"
        call :append_path "%%~p\Scripts"
    )
)
exit /b 0

:append_path
if "%~1"=="" exit /b 0
echo %PATH% | find /I "%~1" >nul
if %errorlevel%==0 exit /b 0
set "PATH=%~1;%PATH%"
exit /b 0

:install_python
set "PY_INSTALL_SUCCESS=0"
set "PY_VERSION=3.11.7"
set "PY_URL="
if /I "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "PY_URL=https://www.python.org/ftp/python/%PY_VERSION%/python-%PY_VERSION%-amd64.exe"
) else (
    set "PY_URL=https://www.python.org/ftp/python/%PY_VERSION%/python-%PY_VERSION%.exe"
)

where winget >nul 2>&1
if %errorlevel%==0 (
    echo [INFO] Instalando Python via winget...
    winget install --id Python.Python.3.11 --exact --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel%==0 (
        set "PY_INSTALL_SUCCESS=1"
        call :ensure_python_path
    ) else (
        echo [⚠] winget retornou código %errorlevel% ao instalar Python.
    )
)

if "%PY_INSTALL_SUCCESS%"=="0" (
    echo [INFO] Baixando instalador oficial do Python...
    del /q python-installer.exe 2>nul
    powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile 'python-installer.exe'" >nul 2>&1
    if exist python-installer.exe (
        set "PY_ALL_USERS=0"
        net session >nul 2>&1
        if %errorlevel%==0 (
            set "PY_ALL_USERS=1"
            set "PY_TARGET_DIR=C:\Program Files\Python311"
        ) else (
            set "PY_TARGET_DIR=%LOCALAPPDATA%\Programs\Python\Python311"
        )
        echo [INFO] Instalando Python em %PY_TARGET_DIR%...
        start /wait "" python-installer.exe /quiet InstallAllUsers=%PY_ALL_USERS% PrependPath=1 Include_test=0 Include_doc=0 Include_pip=1 TargetDir="%PY_TARGET_DIR%"
        if %errorlevel%==0 (
            set "PY_INSTALL_SUCCESS=1"
            call :append_path "%PY_TARGET_DIR%"
            call :append_path "%PY_TARGET_DIR%\Scripts"
        ) else (
            echo [⚠] O instalador do Python retornou código %errorlevel%.
        )
        del /q python-installer.exe 2>nul
    ) else (
        echo [⚠] Falha ao baixar o instalador do Python.
    )
)

exit /b 0