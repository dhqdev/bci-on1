#!/bin/bash
# verify_web_setup.sh - Validar configuração da interface web

echo "🔍 Verificando Configuração da Interface Web"
echo "=============================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

errors=0
warnings=0

# Verificar estrutura web/
echo "1. Verificando estrutura de arquivos..."

files=(
    "web/app.py"
    "web/run_web.sh"
    "web/run_web.bat"
    "web/templates/base.html"
    "web/templates/index.html"
    "web/templates/automation_dia8.html"
    "web/templates/automation_dia16.html"
    "web/templates/whatsapp.html"
    "web/templates/history.html"
    "web/templates/credentials.html"
    "web/static/css/style.css"
    "web/static/js/common.js"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✓${NC} $file"
    else
        echo -e "   ${RED}✗${NC} $file - AUSENTE"
        ((errors++))
    fi
done

echo ""

# Verificar requirements.txt
echo "2. Verificando requirements.txt..."

required_packages=(
    "Flask"
    "Flask-SocketIO"
    "Flask-CORS"
    "python-socketio"
    "python-engineio"
)

if [ -f "requirements.txt" ]; then
    for package in "${required_packages[@]}"; do
        if grep -qi "$package" requirements.txt; then
            echo -e "   ${GREEN}✓${NC} $package encontrado"
        else
            echo -e "   ${RED}✗${NC} $package - AUSENTE"
            ((errors++))
        fi
    done
else
    echo -e "   ${RED}✗${NC} requirements.txt não encontrado"
    ((errors++))
fi

echo ""

# Verificar se venv existe
echo "3. Verificando ambiente virtual..."

if [ -d "venv" ]; then
    echo -e "   ${GREEN}✓${NC} venv/ existe"
    
    # Ativar venv e verificar Flask
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        # Verificar se Flask está instalado
        if python -c "import flask" 2>/dev/null; then
            FLASK_VERSION=$(python -c "import flask; print(flask.__version__)")
            echo -e "   ${GREEN}✓${NC} Flask instalado (versão $FLASK_VERSION)"
        else
            echo -e "   ${YELLOW}⚠${NC} Flask não instalado no venv"
            ((warnings++))
        fi
        
        # Verificar Flask-SocketIO
        if python -c "import flask_socketio" 2>/dev/null; then
            echo -e "   ${GREEN}✓${NC} Flask-SocketIO instalado"
        else
            echo -e "   ${YELLOW}⚠${NC} Flask-SocketIO não instalado"
            ((warnings++))
        fi
        
        # Verificar Flask-CORS
        if python -c "import flask_cors" 2>/dev/null; then
            echo -e "   ${GREEN}✓${NC} Flask-CORS instalado"
        else
            echo -e "   ${YELLOW}⚠${NC} Flask-CORS não instalado"
            ((warnings++))
        fi
        
        deactivate
    elif [ -f "venv/Scripts/activate" ]; then
        # Windows path
        echo -e "   ${GREEN}✓${NC} Ambiente virtual Windows detectado"
    fi
else
    echo -e "   ${YELLOW}⚠${NC} venv/ não encontrado - execute install.sh primeiro"
    ((warnings++))
fi

echo ""

# Verificar sintaxe app.py
echo "4. Verificando sintaxe de app.py..."

if [ -f "web/app.py" ]; then
    if python -m py_compile web/app.py 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} app.py sem erros de sintaxe"
    else
        echo -e "   ${RED}✗${NC} app.py tem erros de sintaxe"
        ((errors++))
    fi
else
    echo -e "   ${RED}✗${NC} web/app.py não encontrado"
    ((errors++))
fi

echo ""

# Verificar scripts executáveis
echo "5. Verificando permissões de execução..."

if [ -f "web/run_web.sh" ]; then
    if [ -x "web/run_web.sh" ]; then
        echo -e "   ${GREEN}✓${NC} run_web.sh é executável"
    else
        echo -e "   ${YELLOW}⚠${NC} run_web.sh não é executável (execute: chmod +x web/run_web.sh)"
        ((warnings++))
    fi
fi

if [ -f "install.sh" ]; then
    if [ -x "install.sh" ]; then
        echo -e "   ${GREEN}✓${NC} install.sh é executável"
    else
        echo -e "   ${YELLOW}⚠${NC} install.sh não é executável"
        ((warnings++))
    fi
fi

if [ -f "update.sh" ]; then
    if [ -x "update.sh" ]; then
        echo -e "   ${GREEN}✓${NC} update.sh é executável"
    else
        echo -e "   ${YELLOW}⚠${NC} update.sh não é executável"
        ((warnings++))
    fi
fi

echo ""

# Verificar documentação
echo "6. Verificando documentação..."

docs=(
    "web/README_WEB.md"
    "QUICKSTART_WEB.md"
    "WEB_SUMMARY.md"
    "INSTALLER_FIXES.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "   ${GREEN}✓${NC} $doc"
    else
        echo -e "   ${YELLOW}⚠${NC} $doc - ausente"
        ((warnings++))
    fi
done

echo ""

# Resumo
echo "=============================================="
echo "📊 RESUMO DA VERIFICAÇÃO"
echo "=============================================="
echo ""

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}✅ TUDO OK! Sistema pronto para uso!${NC}"
    echo ""
    echo "Para iniciar a interface web:"
    echo ""
    echo "   bash web/run_web.sh"
    echo ""
    echo "Depois acesse: http://localhost:5000"
    exit 0
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠ $warnings aviso(s) encontrado(s)${NC}"
    echo ""
    echo "O sistema deve funcionar, mas há algumas recomendações:"
    echo ""
    if [ $warnings -gt 0 ]; then
        echo "- Execute: bash install.sh (para instalar dependências)"
        echo "- Execute: chmod +x web/run_web.sh install.sh update.sh"
    fi
    exit 0
else
    echo -e "${RED}✗ $errors erro(s) e $warnings aviso(s) encontrado(s)${NC}"
    echo ""
    echo "Ações necessárias:"
    echo ""
    echo "1. Execute o instalador: bash install.sh"
    echo "2. Verifique se todos os arquivos foram copiados corretamente"
    echo "3. Execute este script novamente: bash verify_web_setup.sh"
    exit 1
fi
