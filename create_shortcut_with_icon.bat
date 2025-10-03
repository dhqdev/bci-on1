@echo off
REM create_shortcut_with_icon.vbs
REM Script para criar atalho com ícone personalizado

title Criando Atalho BCI-ON1 com Ícone

echo ==========================================
echo 🎨 Criando Atalho com Ícone Personalizado
echo ==========================================
echo.

REM Vai para diretório do projeto
cd /d "%~dp0"

REM Verifica se Pillow está instalado
echo 📦 Verificando Pillow...
python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Pillow não encontrado. Instalando...
    pip install Pillow
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar Pillow
        pause
        exit /b 1
    )
    echo ✅ Pillow instalado
) else (
    echo ✅ Pillow encontrado
)

REM Cria o ícone
echo.
echo 🎨 Criando ícone personalizado...
python create_icon.py
if %errorlevel% neq 0 (
    echo ❌ Erro ao criar ícone
    pause
    exit /b 1
)

REM Cria atalho na área de trabalho com ícone
echo.
echo 🔗 Criando atalho na área de trabalho...

set SCRIPT="%TEMP%\create_shortcut_icon.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\BCI-ON1 Web.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0web\run_web.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "BCI-ON1 - Interface Web OXCASH" >> %SCRIPT%
echo oLink.IconLocation = "%~dp0oxcash_icon.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript //nologo %SCRIPT%
del %SCRIPT%

echo.
echo ==========================================
echo ✅ Atalho criado com sucesso!
echo ==========================================
echo.
echo 📍 Local: Área de Trabalho
echo 🏷️  Nome: BCI-ON1 Web
echo 🎨 Ícone: Logo OXCASH personalizada
echo.
pause
