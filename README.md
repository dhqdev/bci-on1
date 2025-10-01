# 🤖 Auto OXBCI - Sistema de Automação Servopa + Todoist# 🤖 Sistema de Automação Servopa + Todoist v4.0 - CICLO COMPLETO



![Version](https://img.shields.io/badge/version-4.0-blue)## 🎉 NOVA VERSÃO 4.### 1️⃣ Instalar Dependências

![Python](https://img.shields.io/badge/python-3.11+-green)

![License](https://img.shields.io/badge/license-MIT-orange)**Windows:**

```bash

Sistema completo e inteligente de automação que integra o Servopa (sistema de consórcios) com o Todoist (gerenciamento de tarefas), realizando buscas e preenchimentos automáticos de forma cíclica e eficiente.install.bat

```

---

**Linux/Mac:**

## 📋 Índice```bash

bash install.sh

- [Sobre o Sistema](#-sobre-o-sistema)```

- [Instalação Rápida](#-instalação-rápida)

- [Como Usar](#-como-usar)*O ambiente virtual será ativado automaticamente!*

- [Funcionalidades](#-funcionalidades)

- [Atualização](#-atualização)### 2️⃣ Verificar Instalação (Opcional)

- [Estrutura do Projeto](#-estrutura-do-projeto)```bash

- [Tecnologias](#-tecnologias)python verify_installation.py

- [Solução de Problemas](#-solução-de-problemas)```

- [Comandos Rápidos](#-comandos-rápidos)

### 3️⃣ ConfigurarETO IMPLEMENTADO!

---

Sistema completo de automação com **ciclo inteligente** entre Servopa e Todoist!

## 🎯 Sobre o Sistema

### ✨ O que mudou?

O **Auto OXBCI** é um robô de automação que:

✅ **Extrai TODAS as colunas e linhas** do board do Todoist  

### O que ele faz?✅ **Processa coluna por coluna, linha por linha**  

✅ **Alterna automaticamente** entre Servopa e Todoist  

1. **Conecta-se ao Todoist** e extrai todas as tarefas organizadas em boards (colunas)✅ **Marca checkboxes** como concluído após cada lance  

2. **Para cada tarefa**, extrai o número do cliente e informações relevantes✅ **Mantém ambas as abas abertas** durante todo o processo  

3. **Acessa o Servopa** automaticamente com suas credenciais✅ **Relatório completo** com estatísticas ao final  

4. **Busca o cliente** no sistema

5. **Navega até a página de lances** do consórcio---

6. **Preenche automaticamente** os campos necessários

7. **Marca a tarefa como concluída** no Todoist# 🤖 Sistema de Automação Servopa + Todoist v4.0 - CICLO COMPLETO

8. **Repete o processo** para todas as tarefas, alternando entre Servopa e Todoist

## 🎉 NOVA VERSÃO 4.0 - CICLO COMPLETO IMPLEMENTADO!

### Por que usar?

Sistema completo de automação com **ciclo inteligente** entre Servopa e Todoist!

✅ **Automatiza tarefas repetitivas** - economize horas de trabalho manual  

✅ **Reduz erros humanos** - preenchimento preciso e consistente  ---

✅ **Trabalha 24/7** - pode ser agendado para rodar automaticamente  

✅ **Organizado e rastreável** - mantém histórico e logs completos  ## 🚀 Instalação Rápida em Um Comando (Novo!)

✅ **Interface moderna e intuitiva** - fácil de usar e configurar  

### 🐧 **Linux / macOS**

### Como funciona?

Copie e cole no terminal (instala tudo automaticamente):

```

┌─────────────┐     ┌──────────────┐     ┌─────────────┐```bash

│   Todoist   │────▶│  Auto OXBCI  │────▶│   Servopa   │wget https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh && bash setup-linux.sh

│  (Tarefas)  │◀────│   (Robô)     │◀────│ (Consórcios)│```

└─────────────┘     └──────────────┘     └─────────────┘

                            │**Alternativa com curl:**

                            ▼```bash

                    ┌──────────────┐curl -fsSL https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash

                    │  Logs e      │```

                    │  Relatórios  │

                    └──────────────┘### 🪟 **Windows**

```

**Opção 1 - PowerShell (Como Administrador):**

---```powershell

irm https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat -OutFile setup.bat; .\setup.bat

## 🚀 Instalação Rápida```



### Para Computadores **SEM** Experiência em Programação**Opção 2 - Download Direto:**

1. Baixe: [setup-windows.bat](https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat)

O sistema instala **TUDO automaticamente**: Python, Git, Chrome, dependências!2. Clique com botão direito → **"Executar como administrador"**



#### 🐧 Linux / 🍎 macOS---



Abra o terminal e cole este comando:### ✨ O que o instalador faz automaticamente:



```bash✅ Instala Python, Git, Google Chrome  

wget https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh && bash setup-linux.sh✅ Clona o repositório do GitHub  

```✅ Configura ambiente virtual  

✅ Instala todas as dependências  

**Alternativa com curl:**✅ Ativa ambiente virtual automaticamente  

```bash✅ Cria atalhos de execução  

curl -fsSL https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash✅ Verifica tudo está funcionando  

```

**📖 Documentação detalhada**: [INSTALL.md](INSTALL.md)

#### 🪟 Windows

---

**Opção 1 - PowerShell (Recomendado):**

## 🎯 Após Instalação

Abra o PowerShell **como Administrador** e cole:

### Linux / macOS

```powershell```bash

irm https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat -OutFile setup.bat; .\setup.batcd ~/auto-oxbci

```./run.sh

```

**Opção 2 - Download Direto:**

### Windows

1. [Clique aqui para baixar setup-windows.bat](https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat)```batch

2. Clique com botão direito no arquivoREM Clique no atalho "Auto OXBCI" na área de trabalho

3. Selecione **"Executar como administrador"**REM OU

cd %USERPROFILE%\auto-oxbci

---run.bat

```

### Para Quem Já Tem o Projeto Clonado

---

Se você já clonou o repositório anteriormente:

## 📋 Se Já Tem o Projeto Clonado

#### Linux / macOS

```bash### 1️⃣ Instalar Dependências

cd ~/auto-oxbci  # ou onde você clonou```bash

bash install.shpython verify_installation.py

``````



#### Windows### 2️⃣ Instalar (se necessário)

```batch```bash

cd %USERPROFILE%\auto-oxbci# Windows: execute como administrador

install.batinstall.bat

```

# Linux/Mac

---bash install.sh

```

## 💻 Como Usar

### 3️⃣ Configurar

### 1️⃣ Primeira Execução - Configurar Credenciais```bash

python main_gui.py

Após a instalação, execute o sistema:```

- Ir para aba "🔐 Credenciais"

#### Linux / macOS- Preencher Servopa e Todoist

```bash- Clicar "💾 Salvar"

cd ~/auto-oxbci

./run.sh### 4️⃣ Executar

```- Ir para aba "🚀 Automação"

- Clicar "🚀 Iniciar"

#### Windows- Acompanhar logs em tempo real

- Clique no atalho **"Auto OXBCI"** na área de trabalho

- **OU** execute `run.bat` no diretório do projeto**Pronto!** 🎉



#### Na interface:---



1. Vá para a aba **"🔐 Credenciais"**## 📚 Documentação Completa

2. Preencha:

   - **Servopa**: Login e senha### 🎯 Para Começar

   - **Todoist**: API Token (encontre em Todoist → Configurações → Integrações)- ⚡ **[QUICKSTART.md](QUICKSTART.md)** - 3 passos para começar (2 minutos)

3. Clique em **"💾 Salvar Credenciais"**- 🔧 **[verify_installation.py](verify_installation.py)** - Verifica instalação



### 2️⃣ Organizar Tarefas no Todoist### 👤 Para Usuários

- 📘 **[README_V4.md](README_V4.md)** - Guia completo do usuário

No seu Todoist:- 📋 **[SUMMARY.md](SUMMARY.md)** - Resumo executivo



1. Crie um **Board** (visualização em quadros/colunas)### Para Desenvolvedores

2. Organize suas tarefas em colunas (ex: "A Fazer", "Em Andamento", "Concluído")- 🔧 **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Documentação técnica

3. **Formato das tarefas**: O sistema extrai automaticamente números de clientes- 📝 **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças

- 📂 **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Estrutura do projeto

Exemplo de tarefa:

```### 🧪 Scripts

Cliente 12345 - Verificar lance consórcio- 🔬 **[test_cycle_complete.py](test_cycle_complete.py)** - Teste completo

```

---

### 3️⃣ Executar a Automação



1. Vá para a aba **"🚀 Automação"**

2. Clique em **"🚀 Iniciar Automação"**## ✨ Características## ✨ Funcionalidades

3. Acompanhe o progresso em tempo real nos logs



O sistema irá:

- ✅ Extrair todas as tarefas do Todoist- 🎨 **Interface Moderna**: Design profissional com sistema de abas### 🔐 Autenticação Automática

- ✅ Para cada tarefa: buscar cliente → preencher dados → marcar concluído

- ✅ Alternar automaticamente entre Servopa e Todoist- 🔐 **Gerenciamento de Credenciais**: Aba dedicada para configurar senhas- **Login no Servopa** (`https://www.consorcioservopa.com.br/vendas/login`)

- ✅ Gerar relatório completo ao final

- 📊 **Status em Tempo Real**: Cards visuais mostrando progresso de cada etapa- **Login no Todoist** (`https://app.todoist.com/auth/login`) em nova aba

---

- 📝 **Log Detalhado**: Acompanhamento completo com cores e timestamps

## ✨ Funcionalidades

- 🚀 **Controles Completos**: Iniciar, parar e limpar automação### 🎯 Automação Completa

### Interface Moderna

- 🌐 **Gerenciamento de Navegadores**: Fechamento correto de abas1. **Extração automática** do número da tarefa "1550 - dia 8" do projeto "Lances Servopa Outubro Dia 8"

- **🎨 Design profissional** com temas claro/escuro

- **📊 Dashboard interativo** com métricas em tempo real2. **Busca de clientes** no sistema Servopa com o número extraído

- **🔐 Gerenciamento seguro** de credenciais

- **📝 Logs detalhados** e coloridos## 🚀 Instalação Rápida3. **Seleção automática** do primeiro cliente da lista

- **⚙️ Configurações avançadas** para personalização

4. **Navegação automática** para a página de lances

### Automação Inteligente

### Para Usuários sem Python Instalado

- **🔄 Ciclo completo** entre Todoist e Servopa

- **🎯 Extração automática** de dados das tarefas### 🖥️ Interface Moderna

- **🔍 Busca inteligente** de clientes

- **📝 Preenchimento automático** de formulários**Windows:**- **Interface gráfica** com acompanhamento em tempo real

- **✅ Marcação automática** de tarefas concluídas

- **🛡️ Tratamento de erros** robusto```bash- **Logs coloridos** com timestamps



### Segurança e Confiabilidade# Execute como administrador- **Barra de progresso** e status dos componentes



- **🔒 Credenciais criptografadas** localmenteinstall.bat- **Dados extraídos** exibidos dinamicamente

- **💾 Backup automático** de configurações

- **📋 Logs completos** para auditoria```

- **⚡ Recuperação de falhas** automática

- **🔄 Retry automático** em caso de erros temporários## 🚀 Como usar



---**Linux/Mac:**



## 🔄 Atualização```bash### Instalação



### Atualizar para a Versão Mais Recente# Execute no terminal```bash



Atualize o sistema com um único comando:bash install.shpip install -r requirements.txt



#### Linux / macOS``````

```bash

cd ~/auto-oxbci

./update.sh

```Estes scripts instalam automaticamente:### Execução com Interface Gráfica (Recomendado)



#### Windows- Python 3.11+```bash

```batch

cd %USERPROFILE%\auto-oxbci- Google Chromepython main_gui.py

update.bat

```- Todas as dependências necessárias```



### O que o Atualizador Faz:- Ambiente virtual configurado



✅ **Verifica** se há atualizações disponíveis  ### Execução via Linha de Comando

✅ **Faz backup** das suas configurações  

✅ **Salva** mudanças locais (git stash)  ### Para Usuários com Python```bash

✅ **Baixa** últimas atualizações do GitHub  

✅ **Atualiza** dependências Python  python main.py

✅ **Restaura** suas configurações  

✅ **Limpa** arquivos temporários  ```bash```

✅ **Mostra** resumo das mudanças  

# Instalar dependências

---

pip install -r requirements.txt### Testes Individuais

## 📁 Estrutura do Projeto

```bash

```

auto-oxbci/# Executar sistema# Apenas autenticação Servopa

├── 📄 README.md              # Este arquivo - documentação principal

├── 📄 requirements.txt       # Dependências Pythonpython main_gui.pypython auth/servopa_auth.py

├── 📄 credentials.json       # Suas credenciais (criado após configuração)

│```

├── 🚀 Scripts de Execução

│   ├── run.sh               # Executar no Linux/macOS# Apenas autenticação Todoist  

│   ├── run.bat              # Executar no Windows

│   ├── install.sh           # Instalar no Linux/macOS## 🎮 Como Usarpython auth/todoist_auth.py

│   ├── install.bat          # Instalar no Windows

│   ├── update.sh            # Atualizar no Linux/macOS

│   └── update.bat           # Atualizar no Windows

│### 1. Instalação (Primeira vez)# Apenas automação Servopa

├── 🐍 Python - Código Principal

│   ├── main_gui.py          # Interface gráfica principalpython automation/servopa_automation.py

│   └── main.py              # Versão linha de comando

│**Método Fácil (Recomendado):**```

├── 📦 Módulos

│   ├── auth/                # Autenticação- Windows: Clique duas vezes em `install.bat`

│   ├── automation/          # Lógica de automação

│   ├── ui/                  # Interface gráfica- Linux/Mac: Execute `bash install.sh` no terminal## 📁 Estrutura do Projeto

│   └── utils/               # Utilitários

│

├── 📸 screenshots/          # Capturas de tela

├── 🗂️ docs/                # Documentação adicional### 2. Configurar Credenciais```

└── 🔒 venv/                # Ambiente virtual (criado na instalação)

```Auto - BCi/



---1. Execute o sistema: `python main_gui.py` ou clique em `run.bat`├── 🔐 auth/                    # Módulos de autenticação



## 🛠️ Tecnologias2. Vá para a aba "🔐 Credenciais"│   ├── servopa_auth.py         # Login no Servopa



- **Python 3.11+** - Linguagem principal3. Preencha usuário e senha dos sites (dados já preenchidos automaticamente)│   ├── todoist_auth.py         # Login e extração Todoist

- **Tkinter** - Interface gráfica nativa

- **Selenium** - Automação web4. Clique em "💾 Salvar Credenciais" se precisar alterar│   └── __init__.py

- **WebDriver Manager** - Gerenciamento ChromeDriver

- **Requests** - API Todoist├── 🤖 automation/              # Módulos de automação

- **BeautifulSoup4** - Parsing HTML

### 3. Executar Automação│   ├── servopa_automation.py   # Automação completa Servopa

---

│   └── __init__.py

## 🆘 Solução de Problemas

1. Vá para a aba "🚀 Automação"├── 🖥️ ui/                      # Interface gráfica

### Problema: "Comando não encontrado"

2. Clique em "🚀 Iniciar Automação"│   ├── automation_gui.py       # Interface principal

**Solução Linux/macOS:**

```bash3. Acompanhe o progresso nos cards de status│   └── __init__.py

chmod +x run.sh install.sh update.sh

```4. Visualize logs detalhados na área inferior├── ⚙️ utils/                   # Utilitários e configurações



### Problema: "Python não encontrado"│   ├── config.py              # Configurações globais



**Solução:** Execute o instalador automático:## 🔐 Gerenciamento de Credenciais│   └── __init__.py

```bash

bash setup-linux.sh        # Linux/macOS├──  main_gui.py              # Executável principal (GUI)

setup-windows.bat          # Windows (como admin)

```O sistema possui uma aba dedicada para gerenciar credenciais:├── 📋 main.py                  # Executável linha de comando



### Problema: "Credenciais inválidas"├── 📄 requirements.txt         # Dependências



**Solução:**- **Carregamento Automático**: Dados carregados automaticamente do `credentials.json`└── 📖 README.md               # Esta documentação

1. Verifique login/senha do Servopa

2. Token Todoist em: Todoist → Configurações → Integrações- **Campos Seguros**: Senhas ocultadas por padrão```

3. Salve novamente na aba "🔐 Credenciais"

- **Toggle Visualização**: Botão para mostrar/ocultar senhas

### Problema: "Ambiente virtual não ativado"

- **Salvamento Seguro**: Credenciais salvas localmente## ⚙️ Configurações

**Solução:**

```bash

source venv/bin/activate   # Linux/macOS

venv\Scripts\activate.bat  # Windows## 🤖 Fluxo de Automação### Credenciais Servopa

```

- **URL:** `https://www.consorcioservopa.com.br/vendas/login`

---

1. **🌐 Login Servopa**: Acesso ao sistema Servopa- **Login:** `26.350.659/0001-61` (configurável via env SERVOPA_LOGIN)

## 📝 Comandos Rápidos

2. **📋 Extração Todoist**: Abre nova aba e extrai dados da tarefa- **Senha:** `43418` (configurável via env SERVOPA_SENHA)

```bash

# INSTALAR (primeira vez)3. **👤 Seleção Cliente**: Busca e seleciona cliente no Servopa

bash install.sh           # Linux/macOS

install.bat               # Windows4. **🎯 Acesso Lances**: Navega para página de lances### Credenciais Todoist



# EXECUTAR5. **✅ Finalização**: Mantém navegador aberto para verificação- **URL:** `https://app.todoist.com/auth/login`

./run.sh                  # Linux/macOS

run.bat                   # Windows- **Email:** `oscarifn6@gmail.com`



# ATUALIZAR## 📁 Arquivos Principais- **Senha:** `spfctri12`

./update.sh               # Linux/macOS

update.bat                # Windows- **Projeto:** "Lances Servopa Outubro Dia 8"



# ATIVAR AMBIENTE VIRTUAL- `main_gui.py` - Interface principal do sistema- **Tarefa:** "1550 - dia 8"

source venv/bin/activate  # Linux/macOS

venv\Scripts\activate.bat # Windows- `run.bat` - Execução rápida (Windows)



# DESATIVAR AMBIENTE VIRTUAL- `install.bat` - Instalação automática (Windows)  ### Configurações de Performance

deactivate                # Todos os sistemas

```- `install.sh` - Instalação automática (Linux/Mac)- **Timeouts:** 20 segundos



---- `credentials.json` - Arquivo de credenciais (preenchido automaticamente)- **Delays entre ações:** 1-3 segundos



## 🔄 Histórico de Versões- **Digitação natural:** 0.1s por caractere



### v4.0 - Atual ✨## 🛠️ Requisitos

- ✅ Ciclo completo Servopa ↔ Todoist

- ✅ Interface moderna com temas## 🔄 Fluxo de execução

- ✅ Instalador automático completo

- ✅ Script de atualização automática- Python 3.8+

- ✅ Documentação consolidada

- ✅ Melhor tratamento de erros- Google Chrome### 🚀 Interface Gráfica



---- Conexão com internet1. **Inicialização** - Interface moderna é carregada



## 📞 Suporte2. **Login Servopa** - Autenticação automática com delays naturais



- **Issues**: [GitHub Issues](https://github.com/dhqdev/auto-oxbci/issues)**Versão Atual: 1.0** - Interface moderna, credenciais integradas, automação completa3. **Todoist** - Nova aba, login e extração do número da tarefa

- **Documentação**: Pasta `/docs` para detalhes técnicos4. **Busca Clientes** - Preenchimento do número e busca no sistema

5. **Seleção Cliente** - Clique automático no primeiro cliente da lista

---6. **Navegação Lances** - Redirecionamento para página de lances

7. **Finalização** - Logs de confirmação

<div align="center">

### 📊 Monitoramento em Tempo Real

**⭐ Se este projeto foi útil, deixe uma estrela no GitHub! ⭐**- Status de cada componente (Servopa, Todoist, Cliente, Lances)

- Barra de progresso com percentual

[🏠 Início](#-auto-oxbci---sistema-de-automação-servopa--todoist) | [📥 Instalar](#-instalação-rápida) | [💻 Usar](#-como-usar) | [🔄 Atualizar](#-atualização)- Log colorido com timestamps

- Dados extraídos exibidos dinamicamente

---

## ️ Tratamento de erros

**Feito com ❤️ por [dhqdev](https://github.com/dhqdev)**

- ✅ Timeouts configuráveis (20s padrão)

**Versão 4.0** | **Última atualização: Outubro 2025**- ✅ Mensagens detalhadas com timestamps

- ✅ Interface visual para acompanhamento

</div>- ✅ Limpeza automática de recursos

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