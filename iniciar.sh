#!/bin/bash
# iniciar.sh - Launcher Visual do BCI-ON1 para Linux
# Sistema de Automação Servopa + Todoist

# Vai para o diretório do script
cd "$(dirname "$0")"

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # Sem cor

# Função para exibir o cabeçalho
show_header() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}${GREEN}🤖 BCI-ON1 - Sistema de Automação${NC}${CYAN}                    ║${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}   Servopa + Todoist + Evolution API${NC}${CYAN}                   ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Função para verificar instalação
check_installation() {
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
        echo ""
        echo -e "${YELLOW}O sistema ainda não foi instalado.${NC}"
        echo -e "${YELLOW}Execute primeiro: ${CYAN}bash install.sh${NC}"
        echo ""
        read -p "Pressione ENTER para sair..."
        exit 1
    fi
}

# Função para verificar status do sistema
check_system_status() {
    echo -e "${BLUE}📊 Verificando status do sistema...${NC}"
    echo ""
    
    # Verifica Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "   ${GREEN}✅${NC} Python: ${GREEN}$PYTHON_VERSION${NC}"
    else
        echo -e "   ${RED}❌${NC} Python: Não encontrado"
    fi
    
    # Verifica Chrome
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version 2>&1 | cut -d' ' -f3)
        echo -e "   ${GREEN}✅${NC} Chrome: ${GREEN}$CHROME_VERSION${NC}"
    elif command -v chromium-browser &> /dev/null; then
        CHROME_VERSION=$(chromium-browser --version 2>&1 | cut -d' ' -f2)
        echo -e "   ${GREEN}✅${NC} Chromium: ${GREEN}$CHROME_VERSION${NC}"
    else
        echo -e "   ${YELLOW}⚠️${NC}  Chrome: Não encontrado"
    fi
    
    # Verifica ambiente virtual
    if [ -d "venv" ]; then
        echo -e "   ${GREEN}✅${NC} Ambiente Virtual: Configurado"
    else
        echo -e "   ${RED}❌${NC} Ambiente Virtual: Não encontrado"
    fi
    
    # Verifica e cria credenciais se necessário
    if [ ! -f "credentials.json" ] && [ -f "credentials.json.template" ]; then
        cp credentials.json.template credentials.json
        echo -e "   ${YELLOW}⚠️${NC}  Credenciais: Arquivo criado (precisa configurar)"
    elif [ -f "credentials.json" ]; then
        echo -e "   ${GREEN}✅${NC} Credenciais: Configuradas"
    else
        echo -e "   ${YELLOW}⚠️${NC}  Credenciais: Não configuradas"
    fi
    
    echo ""
}

# Função para mostrar menu principal
show_menu() {
    echo -e "${BOLD}${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  MENU PRINCIPAL${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}[1]${NC} 🌐 Iniciar Interface Web ${CYAN}(Recomendado)${NC}"
    echo -e "      Abre o sistema no navegador (http://localhost:5000)"
    echo ""
    echo -e "  ${GREEN}[2]${NC} 📊 Ver Status do Sistema"
    echo -e "      Verifica Python, Chrome, credenciais e dependências"
    echo ""
    echo -e "  ${GREEN}[3]${NC} 📝 Ver Logs e Histórico"
    echo -e "      Visualiza histórico de execuções"
    echo ""
    echo -e "  ${GREEN}[4]${NC} ⚙️  Configurar Credenciais"
    echo -e "      Configura Servopa, Todoist e Evolution API"
    echo ""
    echo -e "  ${GREEN}[5]${NC} 🔄 Reinstalar Sistema"
    echo -e "      Executa instalação novamente"
    echo ""
    echo -e "  ${GREEN}[0]${NC} 🚪 Sair"
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Função para iniciar interface web
start_web() {
    show_header
    echo -e "${CYAN}🌐 Iniciando Interface Web...${NC}"
    echo ""
    bash web/run_web.sh
}

# Função para ver logs
show_logs() {
    show_header
    echo -e "${CYAN}📝 Histórico de Execuções${NC}"
    echo ""
    
    if [ -f "history_dia8.json" ]; then
        echo -e "${GREEN}Arquivo encontrado:${NC} history_dia8.json"
        echo ""
        echo -e "${YELLOW}Últimas linhas:${NC}"
        tail -20 history_dia8.json
    else
        echo -e "${YELLOW}Nenhum histórico encontrado ainda.${NC}"
    fi
    
    echo ""
    read -p "Pressione ENTER para voltar..."
}

# Função para configurar credenciais
configure_credentials() {
    show_header
    echo -e "${CYAN}⚙️  Configuração de Credenciais${NC}"
    echo ""
    
    echo -e "${YELLOW}Para configurar as credenciais:${NC}"
    echo ""
    echo -e "  1. Inicie a interface web (opção 1 do menu)"
    echo -e "  2. Acesse: ${CYAN}http://localhost:5000${NC}"
    echo -e "  3. Clique em ${GREEN}'Configurar Credenciais'${NC}"
    echo ""
    echo -e "Ou edite manualmente o arquivo: ${CYAN}credentials.json${NC}"
    echo ""
    
    read -p "Deseja abrir a interface web agora? [S/n]: " resposta
    if [[ "$resposta" =~ ^[Ss]?$ ]]; then
        start_web
    fi
}

# Função para reinstalar
reinstall() {
    show_header
    echo -e "${YELLOW}⚠️  REINSTALAÇÃO DO SISTEMA${NC}"
    echo ""
    echo -e "${RED}ATENÇÃO: Isso irá reinstalar todas as dependências.${NC}"
    echo -e "${YELLOW}Suas credenciais e histórico serão mantidos.${NC}"
    echo ""
    
    read -p "Deseja continuar? [s/N]: " resposta
    if [[ "$resposta" =~ ^[Ss]$ ]]; then
        echo ""
        echo -e "${CYAN}Executando instalação...${NC}"
        bash install.sh
    else
        echo -e "${GREEN}Operação cancelada.${NC}"
        sleep 1
    fi
}

# Loop principal
main() {
    # Verifica instalação
    check_installation
    
    while true; do
        show_header
        show_menu
        
        read -p "Escolha uma opção [0-5]: " opcao
        
        case $opcao in
            1)
                start_web
                ;;
            2)
                show_header
                check_system_status
                read -p "Pressione ENTER para voltar..."
                ;;
            3)
                show_logs
                ;;
            4)
                configure_credentials
                ;;
            5)
                reinstall
                ;;
            0)
                clear
                echo -e "${GREEN}👋 Até logo!${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}Opção inválida!${NC}"
                sleep 1
                ;;
        esac
    done
}

# Executa o programa
main
