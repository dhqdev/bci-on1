#!/bin/bash
# setup-linux.sh - Instalador Autônomo para Linux/Mac
# Sistema de Automação Servopa + Todoist
# 
# COMO USAR:
# wget -O - https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash
# OU
# curl -fsSL https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash
# OU baixe e execute: bash setup-linux.sh

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Função para imprimir banner
print_banner() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}🤖 Sistema de Automação Servopa + Todoist${NC}              ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}     Instalador Automático Completo                        ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Funções para mensagens
print_step() {
    echo -e "${BLUE}▶${NC} ${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Detectar sistema operacional
detect_os() {
    OS="$(uname -s)"
    case "${OS}" in
        Linux*)     
            MACHINE="Linux"
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                OS_NAME=$NAME
                OS_VERSION=$VERSION_ID
            fi
            ;;
        Darwin*)    
            MACHINE="Mac"
            OS_NAME="macOS"
            OS_VERSION=$(sw_vers -productVersion)
            ;;
        *)          
            MACHINE="UNKNOWN"
            print_error "Sistema operacional não suportado: ${OS}"
            exit 1
            ;;
    esac
}

# Verificar se está executando como root (não recomendado)
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Não execute este script como root/sudo!"
        print_info "Execute: bash setup-linux.sh"
        exit 1
    fi
}

# Instalar dependências do sistema
install_system_dependencies() {
    print_step "Instalando dependências do sistema..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        # Detectar gerenciador de pacotes
        if command -v apt-get &> /dev/null; then
            PKG_MANAGER="apt-get"
            print_info "Usando apt-get (Debian/Ubuntu)"
            
            # Atualizar lista de pacotes (ignorando erros de GPG de outros repos)
            sudo apt-get update 2>&1 | grep -v "GPG" | grep -v "NO_PUBKEY" | grep -v "não está assinado" || true
            
            # Instalar pacotes necessários
            sudo apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                python3-tk \
                git \
                wget \
                curl \
                2>&1 | grep -v "already" || true
                
        elif command -v dnf &> /dev/null; then
            PKG_MANAGER="dnf"
            print_info "Usando dnf (Fedora/RHEL 8+)"
            sudo dnf install -y \
                python3 \
                python3-pip \
                python3-tkinter \
                git \
                wget \
                curl \
                2>&1 | grep -v "already" || true
                
        elif command -v yum &> /dev/null; then
            PKG_MANAGER="yum"
            print_info "Usando yum (CentOS/RHEL)"
            sudo yum install -y \
                python3 \
                python3-pip \
                python3-tkinter \
                git \
                wget \
                curl \
                2>&1 | grep -v "already" || true
        else
            print_error "Gerenciador de pacotes não suportado!"
            print_info "Instale manualmente: python3, python3-pip, python3-venv, git"
            exit 1
        fi
        
    elif [[ "$MACHINE" == "Mac" ]]; then
        # Verificar Homebrew
        if ! command -v brew &> /dev/null; then
            print_warning "Homebrew não encontrado. Instalando..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        print_info "Usando Homebrew (macOS)"
        brew install python@3.11 git 2>&1 | grep -v "already" || true
    fi
    
    print_success "Dependências do sistema instaladas!"
}

# Verificar e instalar Python
setup_python() {
    print_step "Verificando Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    else
        print_error "Python não encontrado após instalação!"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION encontrado"
    
    # Verificar pip
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_warning "pip não encontrado. Instalando..."
        $PYTHON_CMD -m ensurepip --upgrade
    fi
    
    print_success "pip OK"
}

# Instalar Google Chrome
install_chrome() {
    print_step "Verificando Google Chrome..."
    
    if command -v google-chrome &> /dev/null || \
       command -v chromium-browser &> /dev/null || \
       [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
        print_success "Chrome/Chromium já instalado"
        return
    fi
    
    print_warning "Google Chrome não encontrado. Instalando..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        if command -v apt-get &> /dev/null; then
            wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
            sudo apt-get install -y /tmp/chrome.deb 2>&1 | grep -v "already" || true
            rm /tmp/chrome.deb
        elif command -v dnf &> /dev/null || command -v yum &> /dev/null; then
            wget -q -O /tmp/chrome.rpm https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            sudo ${PKG_MANAGER} install -y /tmp/chrome.rpm 2>&1 | grep -v "already" || true
            rm /tmp/chrome.rpm
        fi
    elif [[ "$MACHINE" == "Mac" ]]; then
        brew install --cask google-chrome 2>&1 | grep -v "already" || true
    fi
    
    print_success "Google Chrome instalado!"
}

# Clonar ou atualizar repositório
setup_repository() {
    print_step "Configurando repositório..."
    
    REPO_URL="https://github.com/dhqdev/auto-oxbci.git"
    PROJECT_DIR="$HOME/auto-oxbci"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Diretório já existe!"
        
        # Fazer backup de credenciais se existirem
        BACKUP_DIR="$HOME/.auto-oxbci-backup-$(date +%Y%m%d_%H%M%S)"
        if [ -f "$PROJECT_DIR/credentials.json" ]; then
            print_info "Fazendo backup de credenciais..."
            mkdir -p "$BACKUP_DIR"
            cp "$PROJECT_DIR/credentials.json" "$BACKUP_DIR/" 2>/dev/null || true
            print_success "Backup salvo em: $BACKUP_DIR"
        fi
        
        # Remover diretório antigo
        print_info "Removendo instalação antiga..."
        rm -rf "$PROJECT_DIR"
        print_success "Diretório antigo removido!"
        
        # Clonar nova versão
        print_info "Clonando versão mais recente do GitHub..."
        if git clone "$REPO_URL" "$PROJECT_DIR"; then
            cd "$PROJECT_DIR"
            print_success "Repositório clonado!"
            
            # Restaurar credenciais se houver backup
            if [ -f "$BACKUP_DIR/credentials.json" ]; then
                print_info "Restaurando credenciais..."
                cp "$BACKUP_DIR/credentials.json" "$PROJECT_DIR/" 2>/dev/null || true
                print_success "Credenciais restauradas!"
            fi
        else
            print_error "Falha ao clonar repositório!"
            exit 1
        fi
    else
        print_info "Clonando repositório do GitHub..."
        if git clone "$REPO_URL" "$PROJECT_DIR"; then
            cd "$PROJECT_DIR"
            print_success "Repositório clonado!"
        else
            print_error "Falha ao clonar repositório!"
            exit 1
        fi
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
