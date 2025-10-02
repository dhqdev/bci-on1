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

python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version') do echo [✓] Python encontrado: %%i
    set PYTHON_CMD=python
    goto :check_pip
)

python3 --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python3 --version') do echo [✓] Python3 encontrado: %%i
    set PYTHON_CMD=python3
    goto :check_pip
)

py --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('py --version') do echo [✓] Python (py) encontrado: %%i
    set PYTHON_CMD=py
    goto :check_pip
)

echo [✗] Python não encontrado!
echo.
echo [INFO] Baixando Python...

REM Baixar Python usando PowerShell
echo [INFO] Baixando Python 3.11 (64-bit)...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe', 'python-installer.exe')"

if exist python-installer.exe (
    echo [INFO] Instalando Python...
    echo [INFO] IMPORTANTE: Marque a opção "Add Python to PATH" durante a instalação!
    echo [INFO] Pressione qualquer tecla para continuar com a instalação...
    pause >nul
    
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    del python-installer.exe
    
    echo [INFO] Reinicie o terminal e execute este script novamente.
    pause
    exit /b 1
) else (
    echo [✗] Falha ao baixar Python
    echo [INFO] Baixe manualmente de: https://www.python.org/downloads/
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

echo [INFO] Instalando dependências Python...
python -m pip install selenium webdriver-manager requests beautifulsoup4 schedule Flask Flask-SocketIO Flask-CORS python-socketio python-engineio

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

python -c "import selenium; from webdriver_manager.chrome import ChromeDriverManager; import tkinter as tk; import requests; from bs4 import BeautifulSoup; import schedule; import flask; from flask_socketio import SocketIO; from flask_cors import CORS; print('✓ Todas as dependências OK!')" 2>nul

if %errorLevel% == 0 (
    echo [✓] Teste de dependências passou!
) else (
    echo [✗] Teste de dependências falhou!
    echo [INFO] Verifique se todas as dependências foram instaladas corretamente
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
echo ==========================================
echo [✓] 🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ==========================================
echo.
echo [INFO] Como executar o sistema:
echo.
echo Interface Desktop (Tkinter):
echo    Clique duas vezes em: run.bat
echo.
echo Interface Web (Moderna):
echo    Clique duas vezes em: web\run_web.bat
echo    Depois acesse: http://localhost:5000
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