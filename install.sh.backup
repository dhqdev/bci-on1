#!/bin/bash
# install.sh - Script de instalação completa do Sistema de Automação Servopa + Todoist
# Para sistemas Linux/Mac

echo "=========================================="
echo "🤖 Instalação Automática do Sistema"
echo "Sistema de Automação Servopa + Todoist"
echo "=========================================="
echo ""
echo "⚠️  ATENÇÃO: Este script pode precisar de permissões de administrador"
echo "    para instalar pacotes do sistema. Você pode ser solicitado a"
echo "    digitar sua senha sudo durante a instalação."
echo ""
read -p "Pressione ENTER para continuar..."
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

# Verificar se python3-tk está disponível (necessário para GUI)
if [[ "$MACHINE" == "Linux" ]] && ! $PYTHON_CMD -c "import tkinter" &> /dev/null; then
    print_warning "python3-tk não encontrado. Pode ser necessário para a interface gráfica."
    if command -v apt-get &> /dev/null; then
        print_status "Instalando python3-tk..."
        sudo apt-get install -y python3-tk
    fi
fi

echo ""

# 2. Verificar se python3-venv está disponível (necessário para ambientes gerenciados)
print_status "Verificando suporte a ambientes virtuais..."

if ! $PYTHON_CMD -c "import venv" &> /dev/null; then
    print_warning "Módulo venv não encontrado. Instalando python3-venv..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            echo ""
            print_status "Atualizando lista de pacotes..."
            sudo apt-get update -qq
            print_status "Instalando python3-venv e python3-full..."
            sudo apt-get install -y python3-venv python3-full
        # CentOS/RHEL/Fedora
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-venv
        else
            print_error "Não foi possível instalar python3-venv. Instale manualmente."
            exit 1
        fi
    fi
    
    # Verificar novamente
    if ! $PYTHON_CMD -c "import venv" &> /dev/null; then
        print_error "Falha ao instalar suporte a ambientes virtuais"
        exit 1
    fi
    print_success "Suporte a ambientes virtuais instalado!"
else
    print_success "Suporte a ambientes virtuais encontrado!"
fi

echo ""

# 3. Verificar tkinter (necessário para GUI)
print_status "Verificando tkinter..."

if $PYTHON_CMD -c "import tkinter" &> /dev/null; then
    print_success "tkinter encontrado!"
else
    print_warning "tkinter não encontrado. Instalando..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            print_status "Instalando python3-tk..."
            sudo apt-get install -y python3-tk
        # CentOS/RHEL/Fedora
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-tkinter
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-tkinter
        fi
    fi
    
    if $PYTHON_CMD -c "import tkinter" &> /dev/null; then
        print_success "tkinter instalado!"
    else
        print_warning "tkinter não pôde ser instalado automaticamente."
        print_warning "Você pode instalá-lo manualmente com: sudo apt install python3-tk"
    fi
fi

echo ""

# 4. Instalar Google Chrome
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

# 5. Criar ambiente virtual
print_status "Criando ambiente virtual..."

if [ -d "venv" ]; then
    print_warning "Ambiente virtual já existe. Removendo para criar novo..."
    rm -rf venv
fi

# Criar ambiente virtual
print_status "Criando novo ambiente virtual Python..."
if ! $PYTHON_CMD -m venv venv 2>/dev/null; then
    print_error "Falha ao criar ambiente virtual!"
    
    if [[ "$MACHINE" == "Linux" ]]; then
        print_status "Tentando instalar python3-venv e python3-full..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update -qq
            sudo apt-get install -y python3-venv python3-full python3.12-venv
        fi
    fi
    
    # Tentar novamente
    print_status "Tentando criar ambiente virtual novamente..."
    if ! $PYTHON_CMD -m venv venv 2>/dev/null; then
        print_error "Não foi possível criar ambiente virtual."
        print_error "Execute manualmente: sudo apt install python3.12-venv"
        exit 1
    fi
fi

# Verificar se o ambiente virtual foi criado corretamente
if [ ! -f "venv/bin/python" ] && [ ! -f "venv/Scripts/python.exe" ]; then
    print_error "Ambiente virtual não foi criado corretamente!"
    exit 1
fi

print_success "Ambiente virtual criado com sucesso!"

# Definir caminhos do ambiente virtual baseado no OS
if [ -f "venv/bin/python" ]; then
    VENV_PYTHON="./venv/bin/python"
    VENV_PIP="./venv/bin/pip"
else
    VENV_PYTHON="./venv/Scripts/python"
    VENV_PIP="./venv/Scripts/pip"
fi

echo ""

# 6. Atualizar pip no ambiente virtual (isso sempre funciona dentro do venv)
print_status "Atualizando pip no ambiente virtual..."

if ! $VENV_PIP install --upgrade pip > /dev/null 2>&1; then
    print_warning "Não foi possível atualizar pip, mas continuando..."
fi

print_success "pip pronto no ambiente virtual!"

echo ""

# 7. Instalar dependências Python no ambiente virtual
print_status "Instalando dependências Python no ambiente virtual..."

# Instalar dependências uma por uma para melhor diagnóstico
dependencies=("selenium" "webdriver-manager" "requests" "beautifulsoup4")

for dep in "${dependencies[@]}"; do
    print_status "Instalando $dep..."
    if $VENV_PIP install "$dep" > /dev/null 2>&1; then
        print_success "$dep instalado!"
    else
        print_error "Falha ao instalar $dep"
        exit 1
    fi
done

print_success "Todas as dependências Python foram instaladas!"

echo ""

# 8. Verificar estrutura de arquivos necessários
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

# 9. Testar instalação
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
echo "📋 Resumo da Instalação:"
echo "   ✓ Python $PYTHON_VERSION"
echo "   ✓ Ambiente virtual criado em ./venv"
echo "   ✓ Todas as dependências instaladas"
echo "   ✓ Selenium, WebDriver, Requests, BeautifulSoup"
echo ""
echo "=========================================="
echo "🚀 COMO EXECUTAR O SISTEMA"
echo "=========================================="
echo ""
echo "Opção 1 - Usando o script automático (RECOMENDADO):"
echo ""
echo "   bash run.sh"
echo ""
echo "Opção 2 - Manualmente:"
echo ""
echo "   source venv/bin/activate"
echo "   python main_gui.py"
echo ""
echo "=========================================="
echo ""
print_success "Sistema instalado e pronto para uso! 🎉"
echo ""

# Ativar ambiente virtual automaticamente
echo "=========================================="
print_status "Ativando ambiente virtual automaticamente..."
echo "=========================================="
echo ""

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "✓ Ambiente virtual ativado!"
    echo ""
    print_info "Você já está dentro do ambiente virtual Python."
    print_info "Agora você pode executar diretamente: python main_gui.py"
    echo ""
    print_info "Para sair do ambiente virtual, digite: deactivate"
    echo ""
    
    # Mostrar prompt do ambiente virtual
    echo "Prompt atual: $(which python)"
    echo ""
fi

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