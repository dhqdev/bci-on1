#!/bin/bash
# check_dependencies.sh - Verifica se todas as dependências estão instaladas

echo "=================================================="
echo "  Verificando Dependências - BCI-ON1"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

errors=0

# Verificar se está no venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}[!]${NC} Ambiente virtual não ativado"
    echo "    Ativando venv..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo -e "${RED}[ERRO]${NC} Ambiente virtual não encontrado!"
        echo "        Execute: bash install.sh"
        exit 1
    fi
fi

echo "[*] Testando importações Python..."
echo ""

# Testar cada dependência
python -c "
import sys

dependencies = {
    'selenium': 'Automação de navegador',
    'webdriver_manager.chrome': 'Gerenciador ChromeDriver',
    'tkinter': 'Interface gráfica',
    'requests': 'Requisições HTTP',
    'bs4': 'BeautifulSoup - Parsing HTML',
    'pdfplumber': 'Extração de PDF',
    'dotenv': 'python-dotenv - Variáveis de ambiente',
    'schedule': 'Agendamento de tarefas',
    'flask': 'Framework web',
    'flask_socketio': 'WebSocket tempo real',
    'flask_cors': 'CORS para Flask'
}

errors = 0
for module, desc in dependencies.items():
    try:
        __import__(module)
        print(f'\033[0;32m[OK]\033[0m {desc:40} ({module})')
    except ImportError as e:
        print(f'\033[0;31m[ERRO]\033[0m {desc:40} ({module})')
        print(f'       Erro: {e}')
        errors += 1

print()
if errors == 0:
    print('\033[0;32m✅ Todas as dependências estão instaladas!\033[0m')
    sys.exit(0)
else:
    print(f'\033[0;31m❌ {errors} dependência(s) faltando!\033[0m')
    print()
    print('Para corrigir, execute:')
    print('  source venv/bin/activate')
    print('  pip install -r requirements.txt')
    sys.exit(1)
"

exit_code=$?

echo ""
echo "=================================================="
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}  Sistema pronto para uso!${NC}"
else
    echo -e "${RED}  Instale as dependências faltantes${NC}"
fi
echo "=================================================="

exit $exit_code
