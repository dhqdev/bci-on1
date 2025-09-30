# 🤖 Sistema de Automação Servopa + Todoist v4.0 - CICLO COMPLETO

## 🎉 NOVA VERSÃO 4.0 - CICLO COMPLETO IMPLEMENTADO!

Sistema completo de automação com **ciclo inteligente** entre Servopa e Todoist!

### ✨ O que mudou?

✅ **Extrai TODAS as colunas e linhas** do board do Todoist  
✅ **Processa coluna por coluna, linha por linha**  
✅ **Alterna automaticamente** entre Servopa e Todoist  
✅ **Marca checkboxes** como concluído após cada lance  
✅ **Mantém ambas as abas abertas** durante todo o processo  
✅ **Relatório completo** com estatísticas ao final  

---

## 🚀 Início Rápido

### 1️⃣ Verificar Instalação
```bash
python verify_installation.py
```

### 2️⃣ Instalar (se necessário)
```bash
# Windows: execute como administrador
install.bat

# Linux/Mac
bash install.sh
```

### 3️⃣ Configurar
```bash
python main_gui.py
```
- Ir para aba "🔐 Credenciais"
- Preencher Servopa e Todoist
- Clicar "💾 Salvar"

### 4️⃣ Executar
- Ir para aba "🚀 Automação"
- Clicar "🚀 Iniciar"
- Acompanhar logs em tempo real

**Pronto!** 🎉

---

## 📚 Documentação Completa

### 🎯 Para Começar
- ⚡ **[QUICKSTART.md](QUICKSTART.md)** - 3 passos para começar (2 minutos)
- 🔧 **[verify_installation.py](verify_installation.py)** - Verifica instalação

### 👤 Para Usuários
- 📘 **[README_V4.md](README_V4.md)** - Guia completo do usuário
- 📋 **[SUMMARY.md](SUMMARY.md)** - Resumo executivo

### Para Desenvolvedores
- 🔧 **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Documentação técnica
- 📝 **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças
- 📂 **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Estrutura do projeto

### 🧪 Scripts
- 🔬 **[test_cycle_complete.py](test_cycle_complete.py)** - Teste completo

---



## ✨ Características## ✨ Funcionalidades



- 🎨 **Interface Moderna**: Design profissional com sistema de abas### 🔐 Autenticação Automática

- 🔐 **Gerenciamento de Credenciais**: Aba dedicada para configurar senhas- **Login no Servopa** (`https://www.consorcioservopa.com.br/vendas/login`)

- 📊 **Status em Tempo Real**: Cards visuais mostrando progresso de cada etapa- **Login no Todoist** (`https://app.todoist.com/auth/login`) em nova aba

- 📝 **Log Detalhado**: Acompanhamento completo com cores e timestamps

- 🚀 **Controles Completos**: Iniciar, parar e limpar automação### 🎯 Automação Completa

- 🌐 **Gerenciamento de Navegadores**: Fechamento correto de abas1. **Extração automática** do número da tarefa "1550 - dia 8" do projeto "Lances Servopa Outubro Dia 8"

2. **Busca de clientes** no sistema Servopa com o número extraído

## 🚀 Instalação Rápida3. **Seleção automática** do primeiro cliente da lista

4. **Navegação automática** para a página de lances

### Para Usuários sem Python Instalado

### 🖥️ Interface Moderna

**Windows:**- **Interface gráfica** com acompanhamento em tempo real

```bash- **Logs coloridos** com timestamps

# Execute como administrador- **Barra de progresso** e status dos componentes

install.bat- **Dados extraídos** exibidos dinamicamente

```

## 🚀 Como usar

**Linux/Mac:**

```bash### Instalação

# Execute no terminal```bash

bash install.shpip install -r requirements.txt

``````



Estes scripts instalam automaticamente:### Execução com Interface Gráfica (Recomendado)

- Python 3.11+```bash

- Google Chromepython main_gui.py

- Todas as dependências necessárias```

- Ambiente virtual configurado

### Execução via Linha de Comando

### Para Usuários com Python```bash

python main.py

```bash```

# Instalar dependências

pip install -r requirements.txt### Testes Individuais

```bash

# Executar sistema# Apenas autenticação Servopa

python main_gui.pypython auth/servopa_auth.py

```

# Apenas autenticação Todoist  

## 🎮 Como Usarpython auth/todoist_auth.py



### 1. Instalação (Primeira vez)# Apenas automação Servopa

python automation/servopa_automation.py

**Método Fácil (Recomendado):**```

- Windows: Clique duas vezes em `install.bat`

- Linux/Mac: Execute `bash install.sh` no terminal## 📁 Estrutura do Projeto



### 2. Configurar Credenciais```

Auto - BCi/

1. Execute o sistema: `python main_gui.py` ou clique em `run.bat`├── 🔐 auth/                    # Módulos de autenticação

2. Vá para a aba "🔐 Credenciais"│   ├── servopa_auth.py         # Login no Servopa

3. Preencha usuário e senha dos sites (dados já preenchidos automaticamente)│   ├── todoist_auth.py         # Login e extração Todoist

4. Clique em "💾 Salvar Credenciais" se precisar alterar│   └── __init__.py

├── 🤖 automation/              # Módulos de automação

### 3. Executar Automação│   ├── servopa_automation.py   # Automação completa Servopa

│   └── __init__.py

1. Vá para a aba "🚀 Automação"├── 🖥️ ui/                      # Interface gráfica

2. Clique em "🚀 Iniciar Automação"│   ├── automation_gui.py       # Interface principal

3. Acompanhe o progresso nos cards de status│   └── __init__.py

4. Visualize logs detalhados na área inferior├── ⚙️ utils/                   # Utilitários e configurações

│   ├── config.py              # Configurações globais

## 🔐 Gerenciamento de Credenciais│   └── __init__.py

├──  main_gui.py              # Executável principal (GUI)

O sistema possui uma aba dedicada para gerenciar credenciais:├── 📋 main.py                  # Executável linha de comando

├── 📄 requirements.txt         # Dependências

- **Carregamento Automático**: Dados carregados automaticamente do `credentials.json`└── 📖 README.md               # Esta documentação

- **Campos Seguros**: Senhas ocultadas por padrão```

- **Toggle Visualização**: Botão para mostrar/ocultar senhas

- **Salvamento Seguro**: Credenciais salvas localmente## ⚙️ Configurações



## 🤖 Fluxo de Automação### Credenciais Servopa

- **URL:** `https://www.consorcioservopa.com.br/vendas/login`

1. **🌐 Login Servopa**: Acesso ao sistema Servopa- **Login:** `26.350.659/0001-61` (configurável via env SERVOPA_LOGIN)

2. **📋 Extração Todoist**: Abre nova aba e extrai dados da tarefa- **Senha:** `43418` (configurável via env SERVOPA_SENHA)

3. **👤 Seleção Cliente**: Busca e seleciona cliente no Servopa

4. **🎯 Acesso Lances**: Navega para página de lances### Credenciais Todoist

5. **✅ Finalização**: Mantém navegador aberto para verificação- **URL:** `https://app.todoist.com/auth/login`

- **Email:** `oscarifn6@gmail.com`

## 📁 Arquivos Principais- **Senha:** `spfctri12`

- **Projeto:** "Lances Servopa Outubro Dia 8"

- `main_gui.py` - Interface principal do sistema- **Tarefa:** "1550 - dia 8"

- `run.bat` - Execução rápida (Windows)

- `install.bat` - Instalação automática (Windows)  ### Configurações de Performance

- `install.sh` - Instalação automática (Linux/Mac)- **Timeouts:** 20 segundos

- `credentials.json` - Arquivo de credenciais (preenchido automaticamente)- **Delays entre ações:** 1-3 segundos

- **Digitação natural:** 0.1s por caractere

## 🛠️ Requisitos

## 🔄 Fluxo de execução

- Python 3.8+

- Google Chrome### 🚀 Interface Gráfica

- Conexão com internet1. **Inicialização** - Interface moderna é carregada

2. **Login Servopa** - Autenticação automática com delays naturais

**Versão Atual: 1.0** - Interface moderna, credenciais integradas, automação completa3. **Todoist** - Nova aba, login e extração do número da tarefa
4. **Busca Clientes** - Preenchimento do número e busca no sistema
5. **Seleção Cliente** - Clique automático no primeiro cliente da lista
6. **Navegação Lances** - Redirecionamento para página de lances
7. **Finalização** - Logs de confirmação

### 📊 Monitoramento em Tempo Real
- Status de cada componente (Servopa, Todoist, Cliente, Lances)
- Barra de progresso com percentual
- Log colorido com timestamps
- Dados extraídos exibidos dinamicamente

## ️ Tratamento de erros

- ✅ Timeouts configuráveis (20s padrão)
- ✅ Mensagens detalhadas com timestamps
- ✅ Interface visual para acompanhamento
- ✅ Limpeza automática de recursos
- ✅ Validações em cada etapa
- ✅ Logs coloridos por tipo de mensagem

## 🎨 Interface Visual

### Características
- **Design moderno** com cores profissionais
- **Responsiva** e intuitiva
- **Logs em tempo real** com syntax highlighting
- **Status visual** de cada componente
- **Barra de progresso** animada
- **Botões de controle** (Iniciar/Parar/Limpar)

### Cores
- 🔵 **Azul** - Informações e links
- 🟢 **Verde** - Sucessos e confirmações  
- 🟡 **Amarelo** - Avisos e processos em andamento
- 🔴 **Vermelho** - Erros e falhas
- ⚫ **Cinza** - Timestamps e dados secundários

## 🔧 Desenvolvimento

### Estrutura Modular
- **Separação de responsabilidades** - Auth vs Automation vs UI
- **Código reutilizável** - Funções independentes
- **Configurações centralizadas** - Fácil manutenção
- **Tratamento robusto de erros** - Logs detalhados

### Extensibilidade
- Fácil adição de novos sites
- Interface plugável para outras automações
- Configurações via arquivo de config
- Logs estruturados para análise