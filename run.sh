#!/bin/bash
# Script de execução rápida

# Ativar ambiente virtual
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Executar sistema
python main_gui.py
