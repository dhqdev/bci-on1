@echo off
title Sistema de Automação Servopa + Todoist

REM Ir para o diretório do script
cd /d "%~dp0"

echo ==========================================
echo 🤖 Sistema de Automação Servopa + Todoist
echo ==========================================
echo.

echo Verificando ambiente virtual...
if not exist venv\Scripts\activate.bat (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute primeiro: install.bat
    echo.
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

if %errorLevel% == 0 (
    echo ✓ Ambiente virtual ativado
    echo.
) else (
    echo ❌ Falha ao ativar ambiente virtual
    pause
    exit /b 1
)

echo Iniciando sistema...
python main_gui.py

echo.
echo Sistema encerrado.
pause