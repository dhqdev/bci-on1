#!/bin/bash
# Script de execução rápida
# Sistema de Automação Servopa + Todoist

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ir para o diretório do script (garante que funcione de qualquer lugar)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Iniciando Sistema de Automação Servopa + Todoist..."
echo -e "${BLUE}📁 Diretório do projeto: $SCRIPT_DIR${NC}"
echo ""

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo ""
    echo "Execute primeiro:"
    echo "  cd $SCRIPT_DIR"
    echo "  bash install.sh"
    echo ""
    exit 1
fi

# Verificar se main_gui.py existe
if [ ! -f "main_gui.py" ]; then
    echo -e "${RED}❌ Arquivo main_gui.py não encontrado!${NC}"
    echo "Certifique-se de estar no diretório correto do projeto."
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
    echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"
    echo ""
fi

# Executar sistema
python main_gui.py

# Desativar ambiente virtual ao sair
deactivate
