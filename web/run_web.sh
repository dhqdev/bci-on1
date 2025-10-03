#!/bin/bash
# run_web.sh - Script para iniciar interface web moderna do BCI-ON1

# Vai para o diretório raiz do projeto
cd "$(dirname "$0")/.."

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # Sem cor

clear
echo -e "${CYAN}============================================================${NC}"
echo -e "${GREEN}🌐 BCI-ON1 - Interface Web Moderna${NC}"
echo -e "${GREEN}   Sistema de Automação Servopa + Todoist${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""

# Verifica se Python está instalado
echo -e "${BLUE}[1/4] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    echo -e "${YELLOW}Instale Python 3: sudo apt install python3${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version) encontrado${NC}"
echo ""

# Verifica se o ambiente virtual existe
echo -e "${BLUE}[2/4] Verificando ambiente virtual...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo -e "${YELLOW}Execute primeiro: bash install.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Ambiente virtual encontrado${NC}"
echo ""

# Ativa ambiente virtual
echo -e "${BLUE}[3/4] Ativando ambiente virtual...${NC}"
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao ativar ambiente virtual!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Ambiente virtual ativado!${NC}"
echo ""

# Verifica dependências Flask
echo -e "${BLUE}[4/4] Verificando dependências web...${NC}"
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Flask não encontrado. Instalando dependências...${NC}"
    pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao instalar dependências!${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Todas as dependências estão OK!${NC}"
echo ""

# Inicia servidor Flask
echo -e "${CYAN}============================================================${NC}"
echo -e "${GREEN}🚀 Iniciando servidor web...${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""
echo -e "${YELLOW}📍 Acesse no navegador:${NC}"
echo -e "${CYAN}   http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}⚠️  Para parar o servidor: pressione Ctrl+C${NC}"
echo ""
echo -e "${CYAN}============================================================${NC}"
echo ""

# Inicia o servidor
cd web
python app.py

# Desativa ambiente virtual ao sair
deactivate
