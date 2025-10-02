#!/bin/bash#!/bin/bash#!/bin/bash

# setup-linux.sh - BCI-ON1 Installer for Linux/Mac

# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-linux.sh)# setup-linux.sh - Instalador Automático BCI-ON1 (Linux/Mac)# setup-linux.sh - Instalador Autônomo para Linux/Mac



set -e# Pode ser executado diretamente do GitHub:# Sistema de Automação Servopa + Todoist



RED='\033[0;31m'# bash <(curl -fsSL https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-linux.sh)# 

GREEN='\033[0;32m'

YELLOW='\033[0;33m'# COMO USAR:

BLUE='\033[0;34m'

CYAN='\033[0;36m'set -e# wget -O - https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash

BOLD='\033[1m'

NC='\033[0m'# OU



print_banner() {# Cores# curl -fsSL https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash

    clear

    echo -e "${CYAN}============================================================${NC}"RED='\033[0;31m'# OU baixe e execute: bash setup-linux.sh

    echo -e "${CYAN}  ${BOLD}BCI-ON1 - Instalador Automatico${NC}"

    echo -e "${CYAN}  Sistema de Automacao Servopa + Todoist${NC}"GREEN='\033[0;32m'

    echo -e "${CYAN}============================================================${NC}"

    echo ""YELLOW='\033[0;33m'set -e  # Sair em caso de erro

}

BLUE='\033[0;34m'

print_step() {

    echo -e "${BLUE}[*]${NC} ${BOLD}$1${NC}"CYAN='\033[0;36m'# Cores para output

}

BOLD='\033[1m'RED='\033[0;31m'

print_success() {

    echo -e "${GREEN}[OK]${NC} $1"NC='\033[0m'GREEN='\033[0;32m'

}

YELLOW='\033[0;33m'

print_warning() {

    echo -e "${YELLOW}[!]${NC} $1"# BannerBLUE='\033[0;34m'

}

clearCYAN='\033[0;36m'

print_error() {

    echo -e "${RED}[ERRO]${NC} $1"echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"BOLD='\033[1m'

}

echo -e "${CYAN}║${NC}  ${BOLD}🤖 BCI-ON1 - Instalador Automático${NC}                    ${CYAN}║${NC}"NC='\033[0m' # No Color

print_info() {

    echo -e "${CYAN}[INFO]${NC} $1"echo -e "${CYAN}║${NC}     Sistema de Automação Servopa + Todoist                ${CYAN}║${NC}"

}

echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"# Função para imprimir banner

print_banner

echo ""print_banner() {

if [[ "$OSTYPE" == "linux-gnu"* ]]; then

    OS="Linux"    clear

    print_info "Sistema detectado: Linux"

elif [[ "$OSTYPE" == "darwin"* ]]; then# Funções    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"

    OS="Mac"

    print_info "Sistema detectado: macOS"print_step() {    echo -e "${CYAN}║${NC}  ${BOLD}🤖 Sistema de Automação Servopa + Todoist${NC}              ${CYAN}║${NC}"

else

    print_error "Sistema operacional nao suportado: $OSTYPE"    echo -e "${BLUE}▶${NC} ${BOLD}$1${NC}"    echo -e "${CYAN}║${NC}     Instalador Automático Completo                        ${CYAN}║${NC}"

    exit 1

fi}    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"



echo ""    echo ""



# 1. Check Gitprint_success() {}

print_step "Verificando Git..."

    echo -e "${GREEN}✓${NC} $1"

if ! command -v git &> /dev/null; then

    print_warning "Git nao encontrado. Instalando..."}# Funções para mensagens

    

    if [[ "$OS" == "Linux" ]]; thenprint_step() {

        if command -v apt-get &> /dev/null; then

            sudo apt-get update -qqprint_warning() {    echo -e "${BLUE}▶${NC} ${BOLD}$1${NC}"

            sudo apt-get install -y git

        elif command -v yum &> /dev/null; then    echo -e "${YELLOW}⚠${NC} $1"}

            sudo yum install -y git

        elif command -v dnf &> /dev/null; then}

            sudo dnf install -y git

        fiprint_success() {

    elif [[ "$OS" == "Mac" ]]; then

        if command -v brew &> /dev/null; thenprint_error() {    echo -e "${GREEN}✓${NC} $1"

            brew install git

        else    echo -e "${RED}✗${NC} $1"}

            print_error "Homebrew nao encontrado. Instale o Git manualmente."

            exit 1}

        fi

    fiprint_warning() {

    

    if command -v git &> /dev/null; thenprint_info() {    echo -e "${YELLOW}⚠${NC} $1"

        print_success "Git instalado com sucesso!"

    else    echo -e "${CYAN}ℹ${NC} $1"}

        print_error "Falha ao instalar Git"

        exit 1}

    fi

elseprint_error() {

    GIT_VERSION=$(git --version | cut -d' ' -f3)

    print_success "Git ja instalado (versao $GIT_VERSION)"# Detectar sistema operacional    echo -e "${RED}✗${NC} $1"

fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then}

echo ""

    OS="Linux"

# 2. Check Python

print_step "Verificando Python..."    print_info "Sistema detectado: Linux"print_info() {



PYTHON_CMD=""elif [[ "$OSTYPE" == "darwin"* ]]; then    echo -e "${CYAN}ℹ${NC} $1"

if command -v python3 &> /dev/null; then

    PYTHON_CMD="python3"    OS="Mac"}

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)

    print_success "Python3 encontrado (versao $PYTHON_VERSION)"    print_info "Sistema detectado: macOS"

elif command -v python &> /dev/null; then

    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)else# Detectar sistema operacional

    if [[ $PYTHON_VERSION == 3.* ]]; then

        PYTHON_CMD="python"    print_error "Sistema operacional não suportado: $OSTYPE"detect_os() {

        print_success "Python encontrado (versao $PYTHON_VERSION)"

    else    exit 1    OS="$(uname -s)"

        print_error "Python 2 detectado. Python 3.8+ e necessario."

        PYTHON_CMD=""fi    case "${OS}" in

    fi

fi        Linux*)     



if [ -z "$PYTHON_CMD" ]; thenecho ""            MACHINE="Linux"

    print_warning "Python 3 nao encontrado. Instalando..."

                if [ -f /etc/os-release ]; then

    if [[ "$OS" == "Linux" ]]; then

        if command -v apt-get &> /dev/null; then# 1. Verificar/Instalar Git                . /etc/os-release

            sudo apt-get update -qq

            sudo apt-get install -y python3 python3-pip python3-venv python3-fullprint_step "Verificando Git..."                OS_NAME=$NAME

        elif command -v yum &> /dev/null; then

            sudo yum install -y python3 python3-pip                OS_VERSION=$VERSION_ID

        elif command -v dnf &> /dev/null; then

            sudo dnf install -y python3 python3-pipif ! command -v git &> /dev/null; then            fi

        fi

        PYTHON_CMD="python3"    print_warning "Git não encontrado. Instalando..."            ;;

    elif [[ "$OS" == "Mac" ]]; then

        if command -v brew &> /dev/null; then            Darwin*)    

            brew install python3

            PYTHON_CMD="python3"    if [[ "$OS" == "Linux" ]]; then            MACHINE="Mac"

        else

            print_error "Homebrew nao encontrado. Instale o Python manualmente."        if command -v apt-get &> /dev/null; then            OS_NAME="macOS"

            exit 1

        fi            sudo apt-get update -qq            OS_VERSION=$(sw_vers -productVersion)

    fi

                sudo apt-get install -y git            ;;

    if command -v $PYTHON_CMD &> /dev/null; then

        PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)        elif command -v yum &> /dev/null; then        *)          

        print_success "Python instalado com sucesso! (versao $PYTHON_VERSION)"

    else            sudo yum install -y git            MACHINE="UNKNOWN"

        print_error "Falha ao instalar Python"

        exit 1        elif command -v dnf &> /dev/null; then            print_error "Sistema operacional não suportado: ${OS}"

    fi

fi            sudo dnf install -y git            exit 1



echo ""        fi            ;;



# 3. Check Chrome    elif [[ "$OS" == "Mac" ]]; then    esac

print_step "Verificando Google Chrome..."

        if command -v brew &> /dev/null; then}

CHROME_FOUND=false

            brew install git

if command -v google-chrome &> /dev/null; then

    CHROME_VERSION=$(google-chrome --version | cut -d' ' -f3)        else# Verificar se está executando como root (não recomendado)

    print_success "Google Chrome encontrado (versao $CHROME_VERSION)"

    CHROME_FOUND=true            print_error "Homebrew não encontrado. Instale o Git manualmente."check_root() {

elif command -v chromium-browser &> /dev/null; then

    CHROME_VERSION=$(chromium-browser --version | cut -d' ' -f2)            exit 1    if [ "$EUID" -eq 0 ]; then

    print_success "Chromium encontrado (versao $CHROME_VERSION)"

    CHROME_FOUND=true        fi        print_error "Não execute este script como root/sudo!"

elif [[ "$OS" == "Mac" ]] && [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then

    CHROME_VERSION=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version | cut -d' ' -f3)    fi        print_info "Execute: bash setup-linux.sh"

    print_success "Google Chrome encontrado (versao $CHROME_VERSION)"

    CHROME_FOUND=true            exit 1

fi

    if command -v git &> /dev/null; then    fi

if [ "$CHROME_FOUND" = false ]; then

    print_warning "Google Chrome nao encontrado. Instalando..."        print_success "Git instalado com sucesso!"}

    

    if [[ "$OS" == "Linux" ]]; then    else

        if command -v apt-get &> /dev/null; then

            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 2>/dev/null || true        print_error "Falha ao instalar Git"# Instalar dependências do sistema

            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

            sudo apt-get update -qq        exit 1install_system_dependencies() {

            sudo apt-get install -y google-chrome-stable

        elif command -v dnf &> /dev/null; then    fi    print_step "Instalando dependências do sistema..."

            sudo dnf install -y wget

            wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpmelse    

            sudo dnf localinstall -y google-chrome-stable_current_x86_64.rpm

            rm google-chrome-stable_current_x86_64.rpm    GIT_VERSION=$(git --version | cut -d' ' -f3)    if [[ "$MACHINE" == "Linux" ]]; then

        fi

    elif [[ "$OS" == "Mac" ]]; then    print_success "Git já instalado (versão $GIT_VERSION)"        # Detectar gerenciador de pacotes

        if command -v brew &> /dev/null; then

            brew install --cask google-chromefi        if command -v apt-get &> /dev/null; then

        else

            print_warning "Instale o Chrome manualmente: https://www.google.com/chrome/"            PKG_MANAGER="apt-get"

        fi

    fiecho ""            print_info "Usando apt-get (Debian/Ubuntu)"

    

    print_success "Google Chrome instalado!"            

fi

# 2. Verificar/Instalar Python            # Atualizar lista de pacotes (ignorando erros de GPG de outros repos)

echo ""

print_step "Verificando Python..."            sudo apt-get update 2>&1 | grep -v "GPG" | grep -v "NO_PUBKEY" | grep -v "não está assinado" || true

# 4. Install directory

print_step "Escolhendo diretorio de instalacao..."            



INSTALL_DIR="$HOME/bci-on1"PYTHON_CMD=""            # Instalar pacotes necessários



if [ -d "$INSTALL_DIR" ]; thenif command -v python3 &> /dev/null; then            sudo apt-get install -y \

    print_warning "Diretorio $INSTALL_DIR ja existe!"

    read -p "Deseja remover e reinstalar? [s/N]: " -n 1 -r    PYTHON_CMD="python3"                python3 \

    echo

    if [[ $REPLY =~ ^[Ss]$ ]]; then    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)                python3-pip \

        print_info "Removendo diretorio antigo..."

        rm -rf "$INSTALL_DIR"    print_success "Python3 encontrado (versão $PYTHON_VERSION)"                python3-venv \

        print_success "Diretorio removido!"

    elseelif command -v python &> /dev/null; then                python3-tk \

        print_info "Instalacao cancelada."

        exit 0    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)                git \

    fi

fi    if [[ $PYTHON_VERSION == 3.* ]]; then                wget \



echo ""        PYTHON_CMD="python"                curl \



# 5. Clone repository        print_success "Python encontrado (versão $PYTHON_VERSION)"                2>&1 | grep -v "already" || true

print_step "Clonando repositorio do GitHub..."

    else                

if git clone https://github.com/dhqdev/bci-on1.git "$INSTALL_DIR" 2>&1; then

    print_success "Repositorio clonado com sucesso!"        print_error "Python 2 detectado. Python 3.8+ é necessário."        elif command -v dnf &> /dev/null; then

else

    print_error "Falha ao clonar repositorio"        PYTHON_CMD=""            PKG_MANAGER="dnf"

    exit 1

fi    fi            print_info "Usando dnf (Fedora/RHEL 8+)"



cd "$INSTALL_DIR"fi            sudo dnf install -y \



echo ""                python3 \



# 6. Run local installerif [ -z "$PYTHON_CMD" ]; then                python3-pip \

print_step "Executando instalador local..."

echo ""    print_warning "Python 3 não encontrado. Instalando..."                python3-tkinter \



chmod +x install.sh                    git \



if bash install.sh; then    if [[ "$OS" == "Linux" ]]; then                wget \

    echo ""

    echo -e "${GREEN}============================================================${NC}"        if command -v apt-get &> /dev/null; then                curl \

    echo -e "${GREEN}  ${BOLD}INSTALACAO CONCLUIDA COM SUCESSO!${NC}"

    echo -e "${GREEN}============================================================${NC}"            sudo apt-get update -qq                2>&1 | grep -v "already" || true

    echo ""

    echo -e "${BOLD}Projeto instalado em:${NC} $INSTALL_DIR"            sudo apt-get install -y python3 python3-pip python3-venv python3-full                

    echo ""

    echo -e "${BOLD}Como executar:${NC}"        elif command -v yum &> /dev/null; then        elif command -v yum &> /dev/null; then

    echo ""

    echo -e "  ${CYAN}Interface Desktop:${NC}"            sudo yum install -y python3 python3-pip            PKG_MANAGER="yum"

    echo -e "  cd $INSTALL_DIR"

    echo -e "  bash run.sh"        elif command -v dnf &> /dev/null; then            print_info "Usando yum (CentOS/RHEL)"

    echo ""

    echo -e "  ${CYAN}Interface Web:${NC}"            sudo dnf install -y python3 python3-pip            sudo yum install -y \

    echo -e "  cd $INSTALL_DIR"

    echo -e "  bash web/run_web.sh"        fi                python3 \

    echo -e "  Depois acesse: ${BOLD}http://localhost:5000${NC}"

    echo ""        PYTHON_CMD="python3"                python3-pip \

else

    print_error "Falha na instalacao"    elif [[ "$OS" == "Mac" ]]; then                python3-tkinter \

    exit 1

fi        if command -v brew &> /dev/null; then                git \


            brew install python3                wget \

            PYTHON_CMD="python3"                curl \

        else                2>&1 | grep -v "already" || true

            print_error "Homebrew não encontrado. Instale o Python manualmente."        else

            exit 1            print_error "Gerenciador de pacotes não suportado!"

        fi            print_info "Instale manualmente: python3, python3-pip, python3-venv, git"

    fi            exit 1

            fi

    if command -v $PYTHON_CMD &> /dev/null; then        

        PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)    elif [[ "$MACHINE" == "Mac" ]]; then

        print_success "Python instalado com sucesso! (versão $PYTHON_VERSION)"        # Verificar Homebrew

    else        if ! command -v brew &> /dev/null; then

        print_error "Falha ao instalar Python"            print_warning "Homebrew não encontrado. Instalando..."

        exit 1            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    fi        fi

fi        

        print_info "Usando Homebrew (macOS)"

echo ""        brew install python@3.11 git 2>&1 | grep -v "already" || true

    fi

# 3. Verificar/Instalar Google Chrome    

print_step "Verificando Google Chrome..."    print_success "Dependências do sistema instaladas!"

}

CHROME_FOUND=false

# Verificar e instalar Python

if command -v google-chrome &> /dev/null; thensetup_python() {

    CHROME_VERSION=$(google-chrome --version | cut -d' ' -f3)    print_step "Verificando Python..."

    print_success "Google Chrome encontrado (versão $CHROME_VERSION)"    

    CHROME_FOUND=true    if command -v python3 &> /dev/null; then

elif command -v chromium-browser &> /dev/null; then        PYTHON_CMD="python3"

    CHROME_VERSION=$(chromium-browser --version | cut -d' ' -f2)        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)

    print_success "Chromium encontrado (versão $CHROME_VERSION)"    elif command -v python &> /dev/null; then

    CHROME_FOUND=true        PYTHON_CMD="python"

elif [[ "$OS" == "Mac" ]] && [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then        PYTHON_VERSION=$(python --version | cut -d' ' -f2)

    CHROME_VERSION=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version | cut -d' ' -f3)    else

    print_success "Google Chrome encontrado (versão $CHROME_VERSION)"        print_error "Python não encontrado após instalação!"

    CHROME_FOUND=true        exit 1

fi    fi

    

if [ "$CHROME_FOUND" = false ]; then    print_success "Python $PYTHON_VERSION encontrado"

    print_warning "Google Chrome não encontrado. Instalando..."    

        # Verificar pip

    if [[ "$OS" == "Linux" ]]; then    if ! $PYTHON_CMD -m pip --version &> /dev/null; then

        if command -v apt-get &> /dev/null; then        print_warning "pip não encontrado. Instalando..."

            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -        $PYTHON_CMD -m ensurepip --upgrade

            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list    fi

            sudo apt-get update -qq    

            sudo apt-get install -y google-chrome-stable    print_success "pip OK"

        elif command -v dnf &> /dev/null; then}

            sudo dnf install -y wget

            wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm# Instalar Google Chrome

            sudo dnf localinstall -y google-chrome-stable_current_x86_64.rpminstall_chrome() {

            rm google-chrome-stable_current_x86_64.rpm    print_step "Verificando Google Chrome..."

        fi    

    elif [[ "$OS" == "Mac" ]]; then    if command -v google-chrome &> /dev/null || \

        if command -v brew &> /dev/null; then       command -v chromium-browser &> /dev/null || \

            brew install --cask google-chrome       [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then

        else        print_success "Chrome/Chromium já instalado"

            print_warning "Instale o Chrome manualmente: https://www.google.com/chrome/"        return

        fi    fi

    fi    

        print_warning "Google Chrome não encontrado. Instalando..."

    print_success "Google Chrome instalado!"    

fi    if [[ "$MACHINE" == "Linux" ]]; then

        if command -v apt-get &> /dev/null; then

echo ""            wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

            sudo apt-get install -y /tmp/chrome.deb 2>&1 | grep -v "already" || true

# 4. Determinar diretório de instalação            rm /tmp/chrome.deb

print_step "Escolhendo diretório de instalação..."        elif command -v dnf &> /dev/null || command -v yum &> /dev/null; then

            wget -q -O /tmp/chrome.rpm https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

INSTALL_DIR="$HOME/bci-on1"            sudo ${PKG_MANAGER} install -y /tmp/chrome.rpm 2>&1 | grep -v "already" || true

            rm /tmp/chrome.rpm

if [ -d "$INSTALL_DIR" ]; then        fi

    print_warning "Diretório $INSTALL_DIR já existe!"    elif [[ "$MACHINE" == "Mac" ]]; then

    read -p "Deseja remover e reinstalar? [s/N]: " -n 1 -r        brew install --cask google-chrome 2>&1 | grep -v "already" || true

    echo    fi

    if [[ $REPLY =~ ^[Ss]$ ]]; then    

        print_info "Removendo diretório antigo..."    print_success "Google Chrome instalado!"

        rm -rf "$INSTALL_DIR"}

        print_success "Diretório removido!"

    else# Clonar ou atualizar repositório

        print_info "Instalação cancelada."setup_repository() {

        exit 0    print_step "Configurando repositório..."

    fi    

fi    REPO_URL="https://github.com/dhqdev/auto-oxbci.git"

    PROJECT_DIR="$HOME/auto-oxbci"

echo ""    

    if [ -d "$PROJECT_DIR" ]; then

# 5. Clonar repositório        print_warning "Diretório já existe!"

print_step "Clonando repositório do GitHub..."        

        # Fazer backup de credenciais se existirem

if git clone https://github.com/dhqdev/bci-on1.git "$INSTALL_DIR"; then        BACKUP_DIR="$HOME/.auto-oxbci-backup-$(date +%Y%m%d_%H%M%S)"

    print_success "Repositório clonado com sucesso!"        if [ -f "$PROJECT_DIR/credentials.json" ]; then

else            print_info "Fazendo backup de credenciais..."

    print_error "Falha ao clonar repositório"            mkdir -p "$BACKUP_DIR"

    exit 1            cp "$PROJECT_DIR/credentials.json" "$BACKUP_DIR/" 2>/dev/null || true

fi            print_success "Backup salvo em: $BACKUP_DIR"

        fi

cd "$INSTALL_DIR"        

        # Remover diretório antigo

echo ""        print_info "Removendo instalação antiga..."

        rm -rf "$PROJECT_DIR"

# 6. Executar instalador local        print_success "Diretório antigo removido!"

print_step "Executando instalador local..."        

echo ""        # Clonar nova versão

        print_info "Clonando versão mais recente do GitHub..."

chmod +x install.sh        if git clone "$REPO_URL" "$PROJECT_DIR"; then

            cd "$PROJECT_DIR"

if bash install.sh; then            print_success "Repositório clonado!"

    echo ""            

    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"            # Restaurar credenciais se houver backup

    echo -e "${GREEN}║${NC}  ${BOLD}✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}                  ${GREEN}║${NC}"            if [ -f "$BACKUP_DIR/credentials.json" ]; then

    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"                print_info "Restaurando credenciais..."

    echo ""                cp "$BACKUP_DIR/credentials.json" "$PROJECT_DIR/" 2>/dev/null || true

    echo -e "${BOLD}📍 Projeto instalado em:${NC} $INSTALL_DIR"                print_success "Credenciais restauradas!"

    echo ""            fi

    echo -e "${BOLD}🚀 Como executar:${NC}"        else

    echo ""            print_error "Falha ao clonar repositório!"

    echo -e "   ${CYAN}Interface Desktop:${NC}"            exit 1

    echo -e "   cd $INSTALL_DIR"        fi

    echo -e "   bash run.sh"    else

    echo ""        print_info "Clonando repositório do GitHub..."

    echo -e "   ${CYAN}Interface Web:${NC}"        if git clone "$REPO_URL" "$PROJECT_DIR"; then

    echo -e "   cd $INSTALL_DIR"            cd "$PROJECT_DIR"

    echo -e "   bash web/run_web.sh"            print_success "Repositório clonado!"

    echo -e "   Depois acesse: ${BOLD}http://localhost:5000${NC}"        else

    echo ""            print_error "Falha ao clonar repositório!"

else            exit 1

    print_error "Falha na instalação"        fi

    exit 1    fi

fi    

    print_success "Repositório configurado em: $PROJECT_DIR"
}

# Criar ambiente virtual
setup_venv() {
    print_step "Criando ambiente virtual Python..."
    
    if [ -d "venv" ]; then
        print_warning "Removendo ambiente virtual antigo..."
        rm -rf venv
    fi
    
    $PYTHON_CMD -m venv venv
    
    print_success "Ambiente virtual criado!"
}

# Instalar dependências Python
install_python_dependencies() {
    print_step "Instalando dependências Python..."
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    print_info "Atualizando pip..."
    pip install --upgrade pip -q
    
    # Instalar dependências
    if [ -f "requirements.txt" ]; then
        print_info "Instalando dependências do requirements.txt..."
        pip install -r requirements.txt || {
            print_warning "Falha ao instalar algumas dependências, tentando individualmente..."
            pip install selenium webdriver-manager requests beautifulsoup4 python-dotenv
        }
    else
        print_info "Instalando dependências essenciais..."
        pip install selenium webdriver-manager requests beautifulsoup4 python-dotenv
    fi
    
    # Verificar dependências principais
    if ! python -c "import selenium" 2>/dev/null; then
        print_warning "Selenium não detectado, instalando novamente..."
        pip install --upgrade selenium
    fi
    
    if ! python -c "from webdriver_manager.chrome import ChromeDriverManager" 2>/dev/null; then
        print_warning "WebDriver Manager não detectado, instalando novamente..."
        pip install --upgrade webdriver-manager
    fi
    
    print_success "Dependências Python instaladas!"
}

# Verificar instalação
verify_installation() {
    print_step "Verificando instalação..."
    
    source venv/bin/activate
    
    # Teste de importações essenciais
    $PYTHON_CMD -c "
import sys
errors = []

# Dependências obrigatórias
try:
    import selenium
    print('✓ Selenium: OK')
except ImportError as e:
    errors.append(f'Selenium: {e}')

try:
    from webdriver_manager.chrome import ChromeDriverManager
    print('✓ WebDriver Manager: OK')
except ImportError as e:
    errors.append(f'WebDriver Manager: {e}')

try:
    import tkinter
    print('✓ Tkinter: OK')
except ImportError as e:
    errors.append(f'Tkinter: {e}')

# Dependências opcionais (não causam falha)
try:
    import requests
    print('✓ Requests: OK')
except ImportError:
    print('⚠ Requests: Ausente (opcional)')

try:
    from bs4 import BeautifulSoup
    print('✓ BeautifulSoup: OK')
except ImportError:
    print('⚠ BeautifulSoup: Ausente (opcional)')

if errors:
    print('')
    print('Erros encontrados:')
    for error in errors:
        print(f'  - {error}')
    sys.exit(1)
else:
    print('')
    print('✅ Todas as dependências essenciais verificadas!')
    sys.exit(0)
    " 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Todas as dependências verificadas!"
        return 0
    else
        print_error "Falha na verificação de dependências!"
        return 1
    fi
}

# Criar scripts de execução
create_run_scripts() {
    print_step "Criando scripts de execução..."
    
    # Script de execução
    cat > run.sh << 'EOF'
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
EOF
    
    chmod +x run.sh
    
    print_success "Scripts de execução criados!"
}

# Atualizar install.sh para ativar venv automaticamente
update_install_script() {
    print_step "Atualizando script de instalação..."
    
    if [ -f "install.sh" ]; then
        # Backup do script original
        cp install.sh install.sh.backup
        
        # Adicionar ativação automática ao final
        if ! grep -q "source venv/bin/activate" install.sh; then
            cat >> install.sh << 'EOF'

# Ativar ambiente virtual automaticamente
if [ -f "venv/bin/activate" ]; then
    print_status "Ativando ambiente virtual..."
    source venv/bin/activate
    print_success "Ambiente virtual ativado! Você já está dentro do ambiente."
    echo ""
    print_info "Para sair do ambiente virtual, digite: deactivate"
fi
EOF
        fi
    fi
    
    print_success "Script de instalação atualizado!"
}

# Criar atalho na área de trabalho (opcional)
create_desktop_shortcut() {
    if [[ "$MACHINE" == "Linux" ]]; then
        DESKTOP_DIR="$HOME/Desktop"
        if [ ! -d "$DESKTOP_DIR" ]; then
            DESKTOP_DIR="$HOME/Área de Trabalho"
        fi
        
        if [ -d "$DESKTOP_DIR" ]; then
            cat > "$DESKTOP_DIR/AutoOXBCI.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Auto OXBCI
Comment=Sistema de Automação Servopa + Todoist
Exec=bash $PROJECT_DIR/run.sh
Icon=system-run
Terminal=true
Categories=Utility;
EOF
            chmod +x "$DESKTOP_DIR/AutoOXBCI.desktop"
            print_success "Atalho criado na área de trabalho!"
        fi
    fi
}

# Função principal
main() {
    print_banner
    
    print_info "Sistema: $OS_NAME $OS_VERSION"
    print_info "Arquitetura: $(uname -m)"
    echo ""
    
    print_warning "Esta instalação irá:"
    echo "  1. Instalar dependências do sistema (requer sudo)"
    echo "  2. Clonar o repositório do GitHub"
    echo "  3. Configurar ambiente virtual Python"
    echo "  4. Instalar todas as dependências"
    echo "  5. Criar scripts de execução"
    echo ""
    
    print_info "⚠️  NOTA: Erros de GPG de outros repositórios (Spotify, MongoDB)"
    print_info "    serão ignorados e NÃO afetarão a instalação."
    echo ""
    
    read -p "$(echo -e ${CYAN}Deseja continuar? [S/n]:${NC} )" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]] && [[ ! -z $REPLY ]]; then
        print_warning "Instalação cancelada pelo usuário"
        exit 0
    fi
    
    echo ""
    print_step "Iniciando instalação..."
    echo ""
    
    # Verificações iniciais
    check_root
    detect_os
    
    # Instalação
    install_system_dependencies
    setup_python
    install_chrome
    setup_repository
    setup_venv
    install_python_dependencies
    
    # Verificação
    if verify_installation; then
        create_run_scripts
        update_install_script
        create_desktop_shortcut
        
        # Sucesso
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║${NC}  ${BOLD}🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}                    ${GREEN}║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${BOLD}📂 Projeto instalado em:${NC}"
        echo ""
        echo -e "   ${CYAN}$PROJECT_DIR${NC}"
        echo ""
        echo -e "${BOLD}🚀 Como executar:${NC}"
        echo ""
        echo -e "   ${YELLOW}Opção 1 - De qualquer lugar (RECOMENDADO):${NC}"
        echo -e "   ${CYAN}bash $PROJECT_DIR/run.sh${NC}"
        echo ""
        echo -e "   ${YELLOW}Opção 2 - Entrar no diretório:${NC}"
        echo -e "   ${CYAN}cd $PROJECT_DIR${NC}"
        echo -e "   ${CYAN}./run.sh${NC}"
        echo ""
        echo -e "${BOLD}🔄 Como atualizar:${NC}"
        echo ""
        echo -e "   ${CYAN}bash $PROJECT_DIR/update.sh${NC}  ${BLUE}# Funciona de qualquer lugar!${NC}"
        echo ""
        echo -e "${BOLD}💡 Dica:${NC} Adicione um alias ao seu ~/.bashrc para facilitar:"
        echo -e "   ${CYAN}echo 'alias oxbci=\"bash $PROJECT_DIR/run.sh\"' >> ~/.bashrc${NC}"
        echo ""
        
        # Perguntar se quer executar agora
        read -p "$(echo -e ${CYAN}Deseja executar o sistema agora? [S/n]:${NC} )" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
            echo ""
            print_info "Iniciando sistema..."
            cd "$PROJECT_DIR"
            ./run.sh
        fi
    else
        print_error "Instalação falhou na verificação!"
        print_info "Verifique os erros acima e tente novamente"
        exit 1
    fi
}

# Executar instalação
main
