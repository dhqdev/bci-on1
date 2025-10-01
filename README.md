# 🤖 Sistema de Automação Servopa + Todoist

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Status](https://img.shields.io/badge/status-production-success)

Sistema completo e inteligente de automação que integra o **Servopa** (sistema de consórcios) com o **Todoist** (gerenciamento de tarefas), realizando ciclos automáticos de busca, preenchimento de lances e marcação de tarefas concluídas.

---

## 📋 Índice

- [🎯 O Que o Sistema Faz](#-o-que-o-sistema-faz)
- [🚀 Instalação Rápida](#-instalação-rápida)
- [💻 Como Usar](#-como-usar)
- [🔄 Atualização](#-atualização)
- [✨ Funcionalidades](#-funcionalidades)
- [🛠️ Tecnologias](#️-tecnologias)
- [🆘 Solução de Problemas](#-solução-de-problemas)
- [📚 Documentação Completa](#-documentação-completa)

---

## 🎯 O Que o Sistema Faz

### Fluxo de Automação Completo

```
┌──────────────────────────────────────────────────────────────┐
│  1. EXTRAI BOARD DO TODOIST                                  │
│     • Todas as colunas (grupos de consórcio)                 │
│     • Todas as linhas (cotas dos clientes)                   │
├──────────────────────────────────────────────────────────────┤
│  2. PARA CADA TAREFA NO BOARD:                               │
│     ┌────────────────────────────────────────────────┐       │
│     │ a) Vai para SERVOPA ➜ Busca grupo             │       │
│     │    ├─ Seleciona cota do cliente                │       │
│     │    └─ Registra lance automaticamente           │       │
│     │                                                 │       │
│     │ b) Volta para TODOIST ➜ Marca checkbox ✅      │       │
│     │                                                 │       │
│     │ c) Retorna para SERVOPA ➜ Próxima tarefa      │       │
│     └────────────────────────────────────────────────┘       │
├──────────────────────────────────────────────────────────────┤
│  3. RELATÓRIO FINAL                                          │
│     • Estatísticas completas (sucesso/falha)                 │
│     • Taxa de conclusão                                      │
│     • Logs detalhados de cada operação                       │
└──────────────────────────────────────────────────────────────┘
```

### 🎯 Exemplo Prático

**Todoist:** Você tem 9 tarefas organizadas em 3 colunas (grupos de consórcio)

**O robô:**
1. Extrai todas as 9 tarefas automaticamente
2. Para cada uma: busca no Servopa → preenche lance → marca como concluída no Todoist
3. Alterna entre as duas abas mantendo ambas abertas
4. Mostra progresso em tempo real: \`Progresso: 5/9 tarefas concluídas ✅\`

**Resultado:** Todas as tarefas processadas automaticamente em ~5 minutos!

---

## 🚀 Instalação Rápida

### 🐧 Linux / 🍎 macOS

**Opção 1: Instalação Direta do GitHub (Recomendado)**

\`\`\`bash
wget https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh && bash setup-linux.sh
\`\`\`

**Alternativa com curl:**

\`\`\`bash
curl -fsSL https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash
\`\`\`

✅ **O que o instalador faz automaticamente:**
- Instala Python, Git, Google Chrome
- Clona o repositório do GitHub
- Configura ambiente virtual Python
- Instala todas as dependências (Selenium, WebDriver, etc)
- Cria scripts de execução (\`run.sh\`)
- Verifica se tudo está funcionando

**Opção 2: Se Já Tem o Projeto Clonado**

\`\`\`bash
cd ~/auto-oxbci  # ou onde você clonou
bash install.sh
\`\`\`

---

### 🪟 Windows

**Opção 1: PowerShell (Como Administrador)**

\`\`\`powershell
irm https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat -OutFile setup.bat; .\setup.bat
\`\`\`

**Opção 2: Download Direto**

1. [Clique aqui para baixar setup-windows.bat](https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat)
2. Clique com botão direito → **"Executar como administrador"**

**Opção 3: Se Já Tem o Projeto Clonado**

\`\`\`batch
cd %USERPROFILE%\auto-oxbci
install.bat
\`\`\`

---

## 💻 Como Usar

### 1️⃣ Primeira Execução - Configurar Credenciais

**Linux/Mac:**
\`\`\`bash
cd ~/auto-oxbci
./run.sh
\`\`\`

**Windows:**
\`\`\`batch
cd %USERPROFILE%\auto-oxbci
run.bat
\`\`\`

**Na interface que abrir:**

1. Vá para a aba **"🔐 Credenciais"**
2. Preencha:
   - **Servopa**: Login e senha do sistema
   - **Todoist**: API Token (encontre em Todoist → Configurações → Integrações)
3. Clique em **"💾 Salvar Credenciais"**

---

### 2️⃣ Organizar Tarefas no Todoist

No seu Todoist:

1. Crie um **Board** (visualização em quadros/colunas)
2. Organize suas tarefas em colunas por grupo de consórcio
3. **Formato das tarefas**: O sistema extrai automaticamente números de cota e nome

**Exemplo de estrutura:**

\`\`\`
┌──────────────────┬──────────────────┬──────────────────┐
│ Grupo 1550       │ Grupo 1600       │ Grupo 1650       │
├──────────────────┼──────────────────┼──────────────────┤
│ ☐ 1874 Gil       │ ☐ 2341 Maria     │ ☐ 3012 José      │
│ ☐ 1875 Ana       │ ☐ 2342 Pedro     │ ☐ 3013 Carlos    │
│ ☐ 1876 João      │ ☐ 2343 Paula     │ ☐ 3014 Lucia     │
└──────────────────┴──────────────────┴──────────────────┘
\`\`\`

---

### 3️⃣ Executar a Automação

1. Vá para a aba **"🚀 Automação"**
2. Clique em **"🚀 Iniciar Automação"**
3. Acompanhe o progresso em tempo real nos logs

**O que você verá:**

\`\`\`
[10:30:15] 🚀 Iniciando automação...
[10:30:20] ✅ Login Servopa concluído!
[10:30:35] ✅ Login Todoist concluído!
[10:30:45] 📊 Board extraído: 3 colunas, 9 tarefas

[10:30:50] ┌─────────────────────────────────┐
[10:30:50] │ COLUNA 1/3: Grupo 1550         │
[10:30:50] └─────────────────────────────────┘

[10:30:55] ┌─ Tarefa 1/3 ──────────────────
[10:30:55] │  📝 Cota: 1874
[10:30:55] │  👤 Nome: Gil
[10:31:00] 🌐 [SERVOPA] Processando lance...
[10:31:20] ✅ [SERVOPA] Lance registrado!
[10:31:22] 📋 [TODOIST] Marcando checkbox...
[10:31:25] ✅ [TODOIST] Tarefa marcada!
[10:31:27] 🎉 Tarefa concluída!
[10:31:27] 📊 Progresso: 1/9 tarefas
\`\`\`

**Ao final:**

\`\`\`
═══════════════════════════════════════════
🎉 CICLO COMPLETO FINALIZADO!
═══════════════════════════════════════════
✅ Tarefas concluídas: 8/9
❌ Tarefas com falha: 1/9
📊 Taxa de sucesso: 88.9%
═══════════════════════════════════════════
\`\`\`

---

## 🔄 Atualização

### Atualizar para a Versão Mais Recente

**Linux/Mac:**
\`\`\`bash
# Opção 1: Execute de qualquer lugar (o script encontra o projeto automaticamente)
bash ~/auto-oxbci/update.sh

# Opção 2: Entre no diretório e execute
cd ~/auto-oxbci
./update.sh
\`\`\`

**Windows:**
\`\`\`batch
REM Opção 1: Execute de qualquer lugar
%USERPROFILE%\auto-oxbci\update.bat

REM Opção 2: Entre no diretório e execute
cd %USERPROFILE%\auto-oxbci
update.bat
\`\`\`

**O que o atualizador faz automaticamente:**

✅ **Detecta automaticamente o diretório do projeto** (funciona de qualquer lugar!)  
✅ Verifica se há atualizações disponíveis  
✅ Faz backup das suas configurações (\`credentials.json\`)  
✅ Salva mudanças locais (git stash)  
✅ Baixa últimas atualizações do GitHub  
✅ Atualiza dependências Python  
✅ Restaura suas configurações  
✅ Limpa arquivos temporários  
✅ Mostra resumo das mudanças  

---

## ✨ Funcionalidades

### 🎨 Interface Moderna

- **Design profissional** com sistema de abas
- **Dashboard interativo** com métricas em tempo real
- **Logs detalhados** e coloridos com timestamps
- **Cards de status** mostrando progresso de cada componente
- **Barra de progresso** visual
- **Controles completos**: Iniciar, parar e limpar

### 🤖 Automação Completa

- **🔄 Ciclo completo** entre Todoist e Servopa
- **🎯 Extração automática** de boards completos do Todoist
- **🔍 Busca inteligente** de grupos e cotas no Servopa
- **📝 Preenchimento automático** de formulários de lance
- **✅ Marcação automática** de checkboxes no Todoist
- **🔄 Alternância automática** entre abas (mantém ambas abertas)
- **📊 Processamento sequencial**: coluna por coluna, linha por linha

### 🔐 Segurança e Confiabilidade

- **🔒 Credenciais criptografadas** armazenadas localmente
- **💾 Backup automático** de configurações
- **📋 Logs completos** para auditoria
- **⚡ Recuperação de falhas** automática
- **🔄 Retry automático** em caso de erros temporários
- **🛡️ Tratamento robusto de erros** com mensagens claras

---

## 🛠️ Tecnologias

- **Python 3.11+** - Linguagem principal
- **Tkinter** - Interface gráfica nativa
- **Selenium** - Automação web (controle do Chrome)
- **WebDriver Manager** - Gerenciamento automático do ChromeDriver
- **Requests** - Comunicação com APIs
- **BeautifulSoup4** - Parsing HTML para extração de dados
- **Git** - Controle de versão e atualizações

---

## 🆘 Solução de Problemas

### ❌ Erro: "W: Erro GPG" ou "E: O repositório não está assinado"

**Problema:** Erro nas chaves GPG do sistema (Spotify, MongoDB, etc) - **NÃO afeta o funcionamento do sistema**

**Solução:** Ignore esse erro, ele é relacionado a outros repositórios no seu sistema. O script continuará funcionando normalmente.

**Para corrigir permanentemente (opcional):**

\`\`\`bash
# Remover repositório problemático do Spotify
sudo rm /etc/apt/sources.list.d/spotify.list
sudo apt-get update
\`\`\`

---

### ❌ Erro: "Python não encontrado"

**Solução:** Execute o instalador automático que instala tudo:

\`\`\`bash
bash setup-linux.sh        # Linux/Mac
setup-windows.bat          # Windows (como admin)
\`\`\`

---

### ❌ Erro: "Credenciais inválidas"

**Solução:**

1. Verifique login/senha do Servopa no site manualmente
2. Token Todoist em: Todoist → Configurações → Integrações → API Token
3. Salve novamente na aba "🔐 Credenciais"

---

### ❌ Erro: "Elemento não encontrado" / "Timeout"

**Causas comuns:**
- Internet lenta
- Sites do Servopa/Todoist lentos ou fora do ar
- Sites mudaram estrutura HTML

**Soluções:**
1. Execute novamente em horário de menor tráfego
2. Verifique se consegue acessar os sites manualmente
3. Aguarde alguns minutos e tente novamente

---

## 📚 Documentação Completa

### 🎯 Para Começar

- ⚡ **[QUICKSTART.md](docs/QUICKSTART.md)** - 3 passos para começar (2 minutos)
- 🔧 **[verify_installation.py](verify_installation.py)** - Verifica instalação

### 👤 Para Usuários

- 📘 **[README_USER_GUIDE.md](docs/README_USER_GUIDE.md)** - Guia completo do usuário
- 📋 **[SUMMARY.md](docs/SUMMARY.md)** - Resumo executivo

### 👨‍💻 Para Desenvolvedores

- 🔧 **[TECHNICAL_DOCS.md](docs/TECHNICAL_DOCS.md)** - Documentação técnica
- 📝 **[CHANGELOG.md](docs/CHANGELOG.md)** - Histórico de mudanças
- 📂 **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Estrutura do projeto

---

## 🎮 Comandos Rápidos

\`\`\`bash
# ========== INSTALAR (primeira vez) ==========
bash setup-linux.sh        # Linux/Mac - instala TUDO do GitHub
setup-windows.bat          # Windows - instala TUDO do GitHub

bash install.sh            # Linux/Mac - se já clonou
install.bat                # Windows - se já clonou

# ========== EXECUTAR ==========
bash ~/auto-oxbci/run.sh   # Linux/Mac - de qualquer lugar!
./run.sh                   # Linux/Mac - dentro do diretório

run.bat                    # Windows

# ========== ATUALIZAR ==========
bash ~/auto-oxbci/update.sh   # Linux/Mac - de qualquer lugar!
./update.sh                   # Linux/Mac - dentro do diretório

update.bat                 # Windows - atualiza do GitHub

# ========== TESTES ==========
python verify_installation.py     # Verificar instalação
python test_credentials.py        # Testar credenciais
python test_cycle_complete.py     # Testar ciclo completo
\`\`\`

📖 **[Guia Completo de Atualização](UPDATE_GUIDE.md)** - Tudo sobre como atualizar e resolver problemas

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/dhqdev/auto-oxbci/issues)
- **Documentação**: Pasta \`/docs\` para detalhes técnicos

---

<div align="center">

**⭐ Se este projeto foi útil, deixe uma estrela no GitHub! ⭐**

[🏠 Início](#-sistema-de-automação-servopa--todoist) | [📥 Instalar](#-instalação-rápida) | [💻 Usar](#-como-usar) | [🔄 Atualizar](#-atualização)

---

**Feito com ❤️ por [dhqdev](https://github.com/dhqdev)**

**Versão 1.0** | **Última atualização: Outubro 2025**

</div>
