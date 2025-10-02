#!/bin/bash
# run_web.sh
# Script para iniciar interface web moderna

echo "=================================="
echo "🚀 OXCASH - Interface Web Moderna"
echo "=================================="

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verifica Python
echo -e "${BLUE}📦 Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    exit 1
fi

echo -e "${GREEN}✅ Python encontrado${NC}"

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo -e "${BLUE}🔧 Ativando ambiente virtual...${NC}"
    source venv/bin/activate
fi

# Instala dependências se necessário
if [ ! -f ".web_deps_installed" ]; then
    echo -e "${BLUE}📥 Instalando dependências web...${NC}"
    pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
    touch .web_deps_installed
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
fi

# Inicia servidor Flask
echo ""
echo "=================================="
echo "🌐 Iniciando servidor web..."
echo "=================================="
echo ""

cd web && python3 app.py
