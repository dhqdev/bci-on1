@echo off
REM update.bat - Script de Atualização Automática para Windows
REM Sistema de Automação Servopa + Todoist

setlocal enabledelayedexpansion
title Atualizador Automático - Auto OXBCI

color 0B
cls

echo ================================================================
echo.
echo     🔄 Atualizador Automático - Auto OXBCI
echo        Sistema de Automação Servopa + Todoist
echo.
echo ================================================================
echo.

REM Verificar se está no diretório correto
if not exist .git (
    color 0C
    echo [ERRO] Este não é um repositório Git válido!
    echo [INFO] Execute este script dentro do diretório do projeto
    pause
    exit /b 1
)

if not exist main_gui.py (
    color 0C
    echo [ERRO] Arquivos do projeto não encontrados!
    echo [INFO] Execute este script dentro do diretório auto-oxbci
    pause
    exit /b 1
)

echo [OK] Diretório do projeto verificado
echo.

REM Verificar conexão com internet
echo [INFO] Verificando conexão com internet...
ping -n 1 github.com >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Conexão com internet OK
) else (
    ping -n 1 8.8.8.8 >nul 2>&1
    if %errorLevel% == 0 (
        echo [OK] Conexão com internet OK
    ) else (
        color 0C
        echo [ERRO] Sem conexão com internet!
        echo [INFO] Verifique sua conexão e tente novamente
        pause
        exit /b 1
    )
)
echo.

REM Fazer backup das configurações
echo [INFO] Fazendo backup das configurações...
set BACKUP_DIR=.backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

mkdir "%BACKUP_DIR%" 2>nul

if exist credentials.json (
    copy credentials.json "%BACKUP_DIR%\" >nul 2>&1
    echo [OK] Backup de credentials.json criado
)

if exist evolution_config.json (
    copy evolution_config.json "%BACKUP_DIR%\" >nul 2>&1
    echo [OK] Backup de evolution_config.json criado
)

if exist .env (
    copy .env "%BACKUP_DIR%\" >nul 2>&1
    echo [OK] Backup de .env criado
)

echo %BACKUP_DIR% > .last_backup
echo [OK] Backup completo em: %BACKUP_DIR%
echo.

REM Verificar mudanças locais
echo [INFO] Verificando mudanças locais...
git diff-index --quiet HEAD -- 2>nul
if %errorLevel% neq 0 (
    echo [AVISO] Você tem mudanças não commitadas!
    echo.
    echo Mudanças detectadas:
    git status --short
    echo.
    
    set /p "stash=Deseja fazer stash das mudanças? [S/n]: "
    if /i "!stash!"=="s" (
        git stash push -m "Auto-backup antes de atualização %date% %time%"
        echo [OK] Mudanças salvas em stash
        set STASHED=true
    ) else if /i "!stash!"=="" (
        git stash push -m "Auto-backup antes de atualização %date% %time%"
        echo [OK] Mudanças salvas em stash
        set STASHED=true
    ) else (
        echo [AVISO] Atualização pode sobrescrever suas mudanças!
        set /p "continue=Continuar mesmo assim? [s/N]: "
        if /i not "!continue!"=="s" (
            echo [INFO] Atualização cancelada
            pause
            exit /b 0
        )
    )
) else (
    echo [OK] Nenhuma mudança local detectada
)
echo.

REM Buscar atualizações
echo [INFO] Buscando atualizações do GitHub...
git fetch origin main 2>nul

if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Falha ao buscar atualizações do GitHub
    echo [INFO] Verifique sua conexão e tente novamente
    pause
    exit /b 1
)

REM Verificar se há atualizações
for /f %%i in ('git rev-parse HEAD') do set CURRENT_COMMIT=%%i
for /f %%i in ('git rev-parse origin/main') do set REMOTE_COMMIT=%%i

if "%CURRENT_COMMIT%"=="%REMOTE_COMMIT%" (
    echo.
    echo [OK] Você já está na versão mais recente! 🎉
    echo.
    echo [INFO] Versão atual:
    git log -1 --pretty=format:"%%h - %%s"
    echo.
    echo.
    pause
    exit /b 0
)

echo [OK] Atualizações disponíveis!
echo.
echo Últimas mudanças:
echo.
git log HEAD..origin/main --oneline | findstr /N "^"
echo.

for /f %%i in ('git rev-list --count HEAD..origin/main') do set COMMITS_BEHIND=%%i
echo [INFO] Você está %COMMITS_BEHIND% commit(s) atrás
echo.

REM Perguntar se quer aplicar atualizações
set /p "apply=Deseja aplicar as atualizações? [S/n]: "
if /i not "%apply%"=="s" if /i not "%apply%"=="" (
    echo [INFO] Atualização cancelada
    pause
    exit /b 0
)

echo.
echo [INFO] Aplicando atualizações...

git pull origin main

if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Falha ao aplicar atualizações!
    echo [INFO] Pode haver conflitos. Verifique com: git status
    pause
    exit /b 1
)

echo [OK] Atualizações aplicadas com sucesso!
echo.

REM Atualizar dependências Python
echo [INFO] Verificando dependências Python...

if not exist venv (
    echo [AVISO] Ambiente virtual não encontrado!
    echo [INFO] Execute: install.bat
    goto :cleanup
)

call venv\Scripts\activate.bat

if exist requirements.txt (
    echo [INFO] Atualizando dependências...
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt --upgrade --quiet
    echo [OK] Dependências atualizadas!

    echo [INFO] Verificando integridade do código...
    python -m compileall automation web >nul 2>&1
    if %errorLevel% == 0 (
        echo [OK] Código compilado com sucesso (automation/, web/)
    ) else (
        echo [AVISO] Falha ao compilar automation/ ou web/. Recomendado revisar o código atualizado.
    )

    echo [INFO] Executando teste rápido de extração de protocolo...
    python test_protocol_flow_complete.py >nul 2>&1
    if %errorLevel% == 0 (
        echo [OK] Teste de protocolo executado com sucesso!
    ) else (
        echo [AVISO] O teste de protocolo encontrou problemas. Consulte test_protocol_flow_complete.py.
    )
) else (
    echo [AVISO] requirements.txt não encontrado
)

echo.

REM Verificar arquivos de configuração
echo [INFO] Verificando arquivos de configuração...

if not exist evolution_config.json (
    echo [AVISO] evolution_config.json não encontrado!
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
    
    echo [OK] Arquivo evolution_config.json criado!
) else (
    echo [OK] evolution_config.json encontrado!
)

echo.

:cleanup
REM Limpar arquivos temporários
echo [INFO] Limpando arquivos temporários...

REM Remover cache Python
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul

REM Remover backups antigos (manter últimos 5)
for /f "skip=5 delims=" %%i in ('dir /b /ad /o-d .backup_* 2^>nul') do rd /s /q "%%i" 2>nul

echo [OK] Limpeza concluída!
echo.

REM Restaurar stash
if "%STASHED%"=="true" (
    set /p "restore=Deseja restaurar suas mudanças do stash? [S/n]: "
    if /i "!restore!"=="s" (
        git stash pop
        if %errorLevel% == 0 (
            echo [OK] Mudanças restauradas com sucesso!
        ) else (
            echo [AVISO] Conflitos ao restaurar mudanças
            echo [INFO] Use 'git stash list' e 'git stash apply' manualmente
        )
    ) else if /i "!restore!"=="" (
        git stash pop
        if %errorLevel% == 0 (
            echo [OK] Mudanças restauradas com sucesso!
        ) else (
            echo [AVISO] Conflitos ao restaurar mudanças
            echo [INFO] Use 'git stash list' e 'git stash apply' manualmente
        )
    ) else (
        echo [INFO] Mudanças permanecem no stash
        echo [INFO] Use 'git stash list' para ver e 'git stash pop' para restaurar
    )
    echo.
)

REM Mostrar resumo
echo ================================================================
echo.
echo     ✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!
echo.
echo ================================================================
echo.
echo 📊 Resumo:
echo.

echo    Versão atual:
git log -1 --pretty=format:"   %%h - %%s"
echo.
echo.

echo    Data:
git log -1 --pretty=format:"   %%cd" --date=format:"%%d/%%m/%%Y %%H:%%M"
echo.
echo.

if exist .last_backup (
    set /p BACKUP_DIR=<.last_backup
    echo    Backup: !BACKUP_DIR!
    echo.
)

echo 🚀 Para executar o sistema:
echo.
echo    run.bat
echo.
echo ================================================================
echo.

REM Perguntar se quer executar
set /p "run_now=Deseja executar o sistema agora? [S/n]: "
if /i "%run_now%"=="s" (
    echo.
    echo [INFO] Iniciando sistema...
    echo.
    call run.bat
) else if /i "%run_now%"=="" (
    echo.
    echo [INFO] Iniciando sistema...
    echo.
    call run.bat
) else (
    pause
)

exit /b 0
