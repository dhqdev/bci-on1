#!/bin/bash
# setup-linux.sh - BCI-ON1 Installer
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-linux.sh)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  ${BOLD}BCI-ON1 - Instalador Automatico${NC}"
echo -e "${CYAN}  Sistema de Automacao Servopa + Todoist${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="Mac"
else
    echo -e "${RED}[ERRO]${NC} Sistema nao suportado"
    exit 1
fi

echo -e "${CYAN}[INFO]${NC} Sistema detectado: $OS"
echo ""

# Check Git
echo -e "${BLUE}[*]${NC} Verificando Git..."
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}[!]${NC} Instalando Git..."
    if [[ "$OS" == "Linux" ]]; then
        sudo apt-get update -qq && sudo apt-get install -y git
    else
        brew install git
    fi
fi
echo -e "${GREEN}[OK]${NC} Git instalado"

# Check Python
echo -e "${BLUE}[*]${NC} Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${YELLOW}[!]${NC} Instalando Python..."
    if [[ "$OS" == "Linux" ]]; then
        sudo apt-get install -y python3 python3-pip python3-venv
    else
        brew install python3
    fi
    PYTHON_CMD="python3"
fi
echo -e "${GREEN}[OK]${NC} Python instalado"

# Check Chrome
echo -e "${BLUE}[*]${NC} Verificando Chrome..."
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo -e "${YELLOW}[!]${NC} Instalando Chrome..."
    if [[ "$OS" == "Linux" ]]; then
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 2>/dev/null || true
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update -qq && sudo apt-get install -y google-chrome-stable
    else
        brew install --cask google-chrome
    fi
fi
echo -e "${GREEN}[OK]${NC} Chrome instalado"
echo ""

# Install directory
INSTALL_DIR="$HOME/bci-on1"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[!]${NC} Diretorio $INSTALL_DIR ja existe"
    read -p "Remover e reinstalar? [s/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        exit 0
    fi
fi

# Clone repo
echo -e "${BLUE}[*]${NC} Clonando repositorio..."
git clone https://github.com/dhqdev/bci-on1.git "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Run installer
echo -e "${BLUE}[*]${NC} Executando instalador..."
echo ""
chmod +x install.sh
bash install.sh

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  ${BOLD}INSTALACAO CONCLUIDA!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${BOLD}Projeto instalado em:${NC} $INSTALL_DIR"
echo ""
echo -e "${BOLD}Como executar:${NC}"
echo "  cd $INSTALL_DIR && bash run.sh"
echo "  ou"
echo "  cd $INSTALL_DIR && bash web/run_web.sh"
echo ""
