#!/bin/bash
# update.sh - Script de Atualização Automática
# Sistema de Automação Servopa + Todoist
# 
# Atualiza o projeto local com as últimas mudanças do GitHub

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
    echo -e "${CYAN}║${NC}  ${BOLD}🔄 Atualizador Automático - Auto OXBCI${NC}                 ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}     Sistema de Automação Servopa + Todoist                ${CYAN}║${NC}"
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

# Detectar e navegar para o diretório do projeto
detect_and_navigate_to_project() {
    print_step "Detectando diretório do projeto..."
    
    # Obter o diretório onde o script está localizado
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    
    # Se o script está no diretório auto-oxbci, usar esse diretório
    if [ -f "$SCRIPT_DIR/main_gui.py" ] && [ -d "$SCRIPT_DIR/.git" ]; then
        cd "$SCRIPT_DIR"
        print_success "Encontrado em: $SCRIPT_DIR"
        return 0
    fi
    
    # Procurar em possíveis localizações
    POSSIBLE_PATHS=(
        "$HOME/auto-oxbci"
        "$HOME/Área de trabalho/auto-oxbci"
        "$HOME/Desktop/auto-oxbci"
        "$HOME/Downloads/auto-oxbci"
        "$HOME/Documents/auto-oxbci"
        "./auto-oxbci"
        "../auto-oxbci"
    )
    
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -d "$path" ] && [ -f "$path/main_gui.py" ] && [ -d "$path/.git" ]; then
            cd "$path"
            print_success "Projeto encontrado em: $path"
            return 0
        fi
    done
    
    # Última tentativa: procurar recursivamente a partir do diretório home
    print_info "Procurando projeto no diretório home..."
    PROJECT_PATH=$(find "$HOME" -maxdepth 4 -type d -name "auto-oxbci" 2>/dev/null | head -1)
    
    if [ -n "$PROJECT_PATH" ] && [ -f "$PROJECT_PATH/main_gui.py" ] && [ -d "$PROJECT_PATH/.git" ]; then
        cd "$PROJECT_PATH"
        print_success "Projeto encontrado em: $PROJECT_PATH"
        return 0
    fi
    
    # Não encontrado
    print_error "Não foi possível encontrar o diretório do projeto auto-oxbci!"
    echo ""
    print_info "Por favor, navegue até o diretório do projeto e execute novamente:"
    echo ""
    echo "  cd /caminho/para/auto-oxbci"
    echo "  ./update.sh"
    echo ""
    exit 1
}

# Verificar se está no diretório correto
check_directory() {
    if [ ! -d ".git" ]; then
        print_error "Este não é um repositório Git válido!"
        print_info "Execute este script dentro do diretório do projeto"
        exit 1
    fi
    
    if [ ! -f "main_gui.py" ]; then
        print_error "Arquivos do projeto não encontrados!"
        print_info "Execute este script dentro do diretório auto-oxbci"
        exit 1
    fi
    
    print_success "Diretório do projeto verificado: $(pwd)"
}

# Verificar conexão com internet
check_internet() {
    print_step "Verificando conexão com internet..."
    
    if ping -c 1 github.com &> /dev/null || ping -c 1 8.8.8.8 &> /dev/null; then
        print_success "Conexão com internet OK"
        return 0
    else
        print_error "Sem conexão com internet!"
        print_info "Verifique sua conexão e tente novamente"
        exit 1
    fi
}

# Fazer backup das configurações
backup_config() {
    print_step "Fazendo backup das configurações..."
    
    BACKUP_DIR=".backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup de arquivos importantes
    if [ -f "credentials.json" ]; then
        cp credentials.json "$BACKUP_DIR/" 2>/dev/null || true
        print_success "Backup de credentials.json criado"
    fi
    
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/" 2>/dev/null || true
        print_success "Backup de .env criado"
    fi
    
    if [ -d "venv" ]; then
        print_info "Ambiente virtual preservado (não incluído no backup)"
    fi
    
    echo "$BACKUP_DIR" > .last_backup
    print_success "Backup completo em: $BACKUP_DIR"
}

# Verificar mudanças locais não commitadas
check_local_changes() {
    print_step "Verificando mudanças locais..."
    
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        print_warning "Você tem mudanças não commitadas!"
        echo ""
        echo "Mudanças detectadas:"
        git status --short
        echo ""
        
        read -p "$(echo -e ${YELLOW}Deseja fazer stash das mudanças? [S/n]:${NC} )" -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
            git stash push -m "Auto-backup antes de atualização $(date +%Y%m%d_%H%M%S)"
            print_success "Mudanças salvas em stash"
            STASHED=true
        else
            print_warning "Atualização pode sobrescrever suas mudanças!"
            read -p "$(echo -e ${YELLOW}Continuar mesmo assim? [s/N]:${NC} )" -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Ss]$ ]]; then
                print_info "Atualização cancelada"
                exit 0
            fi
        fi
    else
        print_success "Nenhuma mudança local detectada"
    fi
}

# Obter informações sobre atualizações
fetch_updates() {
    print_step "Buscando atualizações do GitHub..."
    
    git fetch origin main
    
    CURRENT_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/main)
    
    if [ "$CURRENT_COMMIT" = "$REMOTE_COMMIT" ]; then
        echo ""
        print_success "Você já está na versão mais recente! 🎉"
        echo ""
        print_info "Versão atual: $(git log -1 --pretty=format:'%h - %s')"
        echo ""
        exit 0
    fi
    
    print_success "Atualizações disponíveis!"
    echo ""
    echo -e "${BOLD}Últimas mudanças:${NC}"
    echo ""
    git log HEAD..origin/main --oneline --color=always | head -10
    echo ""
    
    COMMITS_BEHIND=$(git rev-list --count HEAD..origin/main)
    print_info "Você está $COMMITS_BEHIND commit(s) atrás"
}

# Aplicar atualizações
apply_updates() {
    print_step "Aplicando atualizações..."
    
    # Fazer pull das mudanças
    if git pull origin main; then
        print_success "Atualizações aplicadas com sucesso!"
    else
        print_error "Falha ao aplicar atualizações!"
        print_info "Pode haver conflitos. Verifique com: git status"
        exit 1
    fi
}

# Atualizar dependências Python
update_dependencies() {
    print_step "Verificando dependências Python..."
    
    if [ ! -d "venv" ]; then
        print_warning "Ambiente virtual não encontrado!"
        print_info "Execute: bash install.sh"
        return
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    if [ -f "requirements.txt" ]; then
        print_info "Atualizando dependências..."
        pip install --upgrade pip -q
        pip install -r requirements.txt --upgrade -q
        print_success "Dependências atualizadas!"
    fi
}

# Limpar arquivos temporários
cleanup() {
    print_step "Limpando arquivos temporários..."
    
    # Remover cache Python
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # Remover backups antigos (manter últimos 5)
    ls -dt .backup_* 2>/dev/null | tail -n +6 | xargs rm -rf 2>/dev/null || true
    
    print_success "Limpeza concluída!"
}

# Restaurar mudanças do stash
restore_stash() {
    if [ "$STASHED" = true ]; then
        echo ""
        read -p "$(echo -e ${CYAN}Deseja restaurar suas mudanças do stash? [S/n]:${NC} )" -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
            if git stash pop; then
                print_success "Mudanças restauradas com sucesso!"
            else
                print_warning "Conflitos ao restaurar mudanças"
                print_info "Use 'git stash list' e 'git stash apply' manualmente"
            fi
        else
            print_info "Mudanças permanecem no stash"
            print_info "Use 'git stash list' para ver e 'git stash pop' para restaurar"
        fi
    fi
}

# Mostrar resumo
show_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  ${BOLD}✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!${NC}                  ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}📊 Resumo:${NC}"
    echo ""
    echo -e "   ${CYAN}Versão atual:${NC} $(git log -1 --pretty=format:'%h - %s')"
    echo -e "   ${CYAN}Data:${NC} $(git log -1 --pretty=format:'%cd' --date=format:'%d/%m/%Y %H:%M')"
    echo -e "   ${CYAN}Autor:${NC} $(git log -1 --pretty=format:'%an')"
    echo ""
    
    if [ -f ".last_backup" ]; then
        BACKUP_DIR=$(cat .last_backup)
        echo -e "   ${CYAN}Backup:${NC} $BACKUP_DIR"
        echo ""
    fi
    
    echo -e "${BOLD}🚀 Para executar o sistema:${NC}"
    echo ""
    echo -e "   ${CYAN}./run.sh${NC}"
    echo ""
}

# Função principal
main() {
    print_banner
    
    # Detectar e navegar para o diretório do projeto
    detect_and_navigate_to_project
    echo ""
    
    # Verificações iniciais
    check_directory
    echo ""
    check_internet
    
    echo ""
    print_info "Iniciando processo de atualização..."
    echo ""
    
    # Processo de atualização
    backup_config
    echo ""
    check_local_changes
    echo ""
    fetch_updates
    echo ""
    
    read -p "$(echo -e ${CYAN}Deseja aplicar as atualizações? [S/n]:${NC} )" -n 1 -r
    echo
    echo ""
    
    if [[ ! $REPLY =~ ^[Ss]$ ]] && [[ ! -z $REPLY ]]; then
        print_warning "Atualização cancelada pelo usuário"
        exit 0
    fi
    
    apply_updates
    echo ""
    update_dependencies
    echo ""
    cleanup
    restore_stash
    show_summary
    
    # Perguntar se quer executar o sistema
    read -p "$(echo -e ${CYAN}Deseja executar o sistema agora? [S/n]:${NC} )" -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ss]$ ]] || [[ -z $REPLY ]]; then
        echo ""
        print_info "Iniciando sistema..."
        echo ""
        ./run.sh
    fi
}

# Executar atualização
main
