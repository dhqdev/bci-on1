#!/bin/bash
# Script de execução rápida
# Sistema de Automação Servopa + Todoist

# Ir para o diretório do script
cd "$(dirname "$0")"

echo "🚀 Iniciando Sistema de Automação Servopa + Todoist..."
echo ""

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Execute primeiro: bash install.sh"
    exit 1
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

if [ $? -eq 0 ]; then
    echo "✓ Ambiente virtual ativado"
    echo ""
fi

# Executar sistema
python main_gui.py

# Desativar ambiente virtual ao sair
deactivate
