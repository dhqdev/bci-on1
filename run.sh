#!/bin/bash
# Script de execução do sistema BCI-ON1

# Vai para o diretório do script
cd "$(dirname "$0")"

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

clear
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🚀 BCI-ON1 - Sistema de Automação Servopa + Todoist${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo -e "${YELLOW}Execute primeiro: bash install.sh${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Ativando ambiente virtual...${NC}"
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao ativar ambiente virtual!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ambiente virtual ativado!${NC}"
echo ""
echo -e "${YELLOW}⚠️  NOTA: A versão desktop foi desativada${NC}"
echo -e "${BLUE}🌐 Redirecionando para interface web...${NC}"
echo ""
sleep 2

# Redireciona para a versão web
cd web
python app.py

# Desativa ambiente virtual ao sair
deactivate
