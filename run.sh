#!/bin/bash
# Script de execução do sistema

cd "$(dirname "$0")"

echo "🚀 Iniciando Sistema de Automação Servopa + Todoist..."
echo ""

# Ativar ambiente virtual
source venv/bin/activate

# Executar sistema
python main_gui.py

# Desativar ambiente virtual ao sair
deactivate
