#!/bin/bash
# install.sh - Script de instalação completa do Sistema de Automação Servopa + Todoist
# Para sistemas Linux/Mac

echo "=========================================="
echo "🤖 Instalação Automática do Sistema"
echo "Sistema de Automação Servopa + Todoist"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar se está executando como root (não recomendado)
if [ "$EUID" -eq 0 ]; then
    print_warning "Não execute este script como root/sudo para evitar problemas de permissão"
    echo "Execute: bash install.sh"
    exit 1
fi

# Verificar sistema operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_status "Sistema detectado: $MACHINE"
echo ""

# 1. Verificar/Instalar Python
print_status "Verificando Python..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python3 encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    print_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_error "Python não encontrado!"
    echo ""
    print_status "Instalando Python..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            print_status "Instalando Python via apt-get..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv python3-tk
            PYTHON_CMD="python3"
        # CentOS/RHEL/Fedora
        elif command -v yum &> /dev/null; then
            print_status "Instalando Python via yum..."
            sudo yum install -y python3 python3-pip python3-tkinter
            PYTHON_CMD="python3"
        elif command -v dnf &> /dev/null; then
            print_status "Instalando Python via dnf..."
            sudo dnf install -y python3 python3-pip python3-tkinter
            PYTHON_CMD="python3"
        else
            print_error "Gerenciador de pacotes não suportado. Instale Python manualmente."
            exit 1
        fi
    elif [[ "$MACHINE" == "Mac" ]]; then
        if command -v brew &> /dev/null; then
            print_status "Instalando Python via Homebrew..."
            brew install python@3.11
            PYTHON_CMD="python3"
        else
            print_error "Homebrew não encontrado. Instale Python manualmente de python.org"
            exit 1
        fi
    fi
    
    # Verificar se instalação foi bem-sucedida
    if command -v $PYTHON_CMD &> /dev/null; then
        print_success "Python instalado com sucesso!"
    else
        print_error "Falha na instalação do Python"
        exit 1
    fi
fi

# Verificar se venv está disponível
if [[ "$MACHINE" == "Linux" ]]; then
    if ! $PYTHON_CMD -c "import venv" &> /dev/null; then
        print_warning "python3-venv não está instalado. Instalando..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-venv
        else
            print_error "Não foi possível instalar python3-venv automaticamente. Instale manualmente com: sudo apt install python3-venv"
            exit 1
        fi
        if ! $PYTHON_CMD -c "import venv" &> /dev/null; then
            print_error "Falha ao instalar python3-venv"
            exit 1
        fi
        print_success "python3-venv instalado!"
    fi
fi

echo ""

# 2. Verificar/Instalar pip
print_status "Verificando pip..."

if $PYTHON_CMD -m pip --version &> /dev/null; then
    print_success "pip encontrado"
else
    print_status "Instalando pip..."
    
    # Download e instala pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $PYTHON_CMD get-pip.py
    rm get-pip.py
    
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_success "pip instalado com sucesso!"
    else
        print_error "Falha na instalação do pip"
        exit 1
    fi
fi

echo ""

# 3. Instalar Google Chrome
print_status "Verificando Google Chrome..."

if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version | cut -d' ' -f3)
    print_success "Google Chrome encontrado: $CHROME_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROME_VERSION=$(chromium-browser --version | cut -d' ' -f2)
    print_success "Chromium encontrado: $CHROME_VERSION"
elif command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" &> /dev/null; then
    CHROME_VERSION=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version | cut -d' ' -f3)
    print_success "Google Chrome encontrado: $CHROME_VERSION"
else
    print_warning "Google Chrome não encontrado"
    print_status "Instalando Google Chrome..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable
        # CentOS/RHEL/Fedora
        elif command -v yum &> /dev/null; then
            sudo yum install -y wget
            wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            sudo yum localinstall -y google-chrome-stable_current_x86_64.rpm
            rm google-chrome-stable_current_x86_64.rpm
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y wget
            wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            sudo dnf localinstall -y google-chrome-stable_current_x86_64.rpm
            rm google-chrome-stable_current_x86_64.rpm
        fi
    elif [[ "$MACHINE" == "Mac" ]]; then
        if command -v brew &> /dev/null; then
            brew install --cask google-chrome
        else
            print_warning "Baixe e instale o Chrome manualmente de: https://www.google.com/chrome/"
        fi
    fi
fi

echo ""

# 4. Criar ambiente virtual
print_status "Criando ambiente virtual..."

if [ -d "venv" ]; then
    print_warning "Ambiente virtual já existe. Removendo..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv

if [ ! -f "venv/bin/python" ]; then
    print_error "Falha ao criar ambiente virtual. Verifique se python3-venv está instalado."
    exit 1
fi

VENV_PYTHON="./venv/bin/python"
VENV_PIP="./venv/bin/pip"

print_success "Ambiente virtual criado!"

echo ""

# 5. Instalar dependências Python
print_status "Instalando dependências Python..."

# Atualizar pip no ambiente virtual
$VENV_PIP install --upgrade pip

# Instalar dependências
$VENV_PIP install selenium webdriver-manager requests beautifulsoup4

print_success "Dependências Python instaladas!"

echo ""

# 6. Verificar estrutura de arquivos necessários
print_status "Verificando estrutura de arquivos..."

required_files=(
    "main_gui.py"
    "requirements.txt"
    "credentials.json"
    "auth/__init__.py"
    "auth/servopa_auth.py" 
    "auth/todoist_auth.py"
    "automation/__init__.py"
    "automation/servopa_automation.py"
    "ui/__init__.py"
    "ui/modern_automation_gui.py"
    "utils/__init__.py"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    print_success "Todos os arquivos necessários estão presentes!"
else
    print_warning "Arquivos ausentes detectados:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
fi

echo ""

# 7. Testar instalação
print_status "Testando instalação..."

# Teste rápido de importações
$VENV_PYTHON -c "
import sys
try:
    import selenium
    from webdriver_manager.chrome import ChromeDriverManager
    print('✓ Selenium: OK')
    print('✓ WebDriver Manager: OK')
    
    import tkinter as tk
    print('✓ Tkinter: OK')
    
    import requests
    print('✓ Requests: OK')
    
    from bs4 import BeautifulSoup
    print('✓ BeautifulSoup: OK')
    
    print('\\n✅ Todas as dependências estão funcionando!')
    
except ImportError as e:
    print(f'❌ Erro na importação: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Teste de dependências passou!"
else
    print_error "Teste de dependências falhou!"
    exit 1
fi

echo ""
echo "=========================================="
print_success "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=========================================="
echo ""
print_status "Como executar o sistema:"
echo ""
echo "1. Ativar ambiente virtual:"
if [[ "$MACHINE" == "Mac" ]] || [[ "$MACHINE" == "Linux" ]]; then
    echo "   source venv/bin/activate"
else
    echo "   venv/bin/activate"
fi
echo ""
echo "2. Executar o sistema:"
echo "   python main_gui.py"
echo ""
print_status "Para desativar o ambiente virtual:"
echo "   deactivate"
echo ""

# Criar script de execução rápida
cat > run.sh << 'EOF'
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
EOF

chmod +x run.sh

print_success "Script de execução criado: ./run.sh"
echo ""

print_status "Sistema pronto para uso! 🚀"