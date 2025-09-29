@echo off
title Sistema de Automação Servopa + Todoist v1.0

echo ==========================================
echo 🤖 Sistema de Automação Servopa + Todoist
echo Versão 1.0 - Interface Moderna
echo ==========================================
echo.

echo Ativando ambiente virtual...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✓ Ambiente virtual ativado
) else (
    echo ⚠ Ambiente virtual não encontrado
    echo Execute install.bat primeiro
    pause
    exit /b 1
)

echo.
echo Iniciando sistema...
python main_gui.py

echo.
echo Sistema encerrado.
pause