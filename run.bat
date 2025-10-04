@echo off 
title Sistema de Automação Servopa + Todoist 
echo Ativando ambiente virtual... 
call venv\Scripts\activate.bat 
echo Iniciando sistema... 
python main_gui.py 
pause 
