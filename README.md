# 🤖 Automação Servopa + Todoist

Sistema completo de automação com interface gráfica moderna que integra o sistema Servopa com o Todoist para extrair números de tarefas e preencher automaticamente consórcios.

## ✨ Funcionalidades

### 🔐 Autenticação Automática
- **Login no Servopa** (`https://www.consorcioservopa.com.br/vendas/login`)
- **Login no Todoist** (`https://app.todoist.com/auth/login`) em nova aba

### 🎯 Automação Completa
1. **Extração automática** do número da tarefa "1550 - dia 8" do projeto "Lances Servopa Outubro Dia 8"
2. **Busca de clientes** no sistema Servopa com o número extraído
3. **Seleção automática** do primeiro cliente da lista
4. **Navegação automática** para a página de lances

### 🖥️ Interface Moderna
- **Interface gráfica** com acompanhamento em tempo real
- **Logs coloridos** com timestamps
- **Barra de progresso** e status dos componentes
- **Dados extraídos** exibidos dinamicamente
- **Screenshots automáticos** para verificação

## 🚀 Como usar

### Instalação
```bash
pip install -r requirements.txt
```

### Execução com Interface Gráfica (Recomendado)
```bash
python main_gui.py
```

### Execução via Linha de Comando
```bash
python main.py
```

### Testes Individuais
```bash
# Apenas autenticação Servopa
python auth/servopa_auth.py

# Apenas autenticação Todoist  
python auth/todoist_auth.py

# Apenas automação Servopa
python automation/servopa_automation.py
```

## 📁 Estrutura do Projeto

```
Auto - BCi/
├── 🔐 auth/                    # Módulos de autenticação
│   ├── servopa_auth.py         # Login no Servopa
│   ├── todoist_auth.py         # Login e extração Todoist
│   └── __init__.py
├── 🤖 automation/              # Módulos de automação
│   ├── servopa_automation.py   # Automação completa Servopa
│   └── __init__.py
├── 🖥️ ui/                      # Interface gráfica
│   ├── automation_gui.py       # Interface principal
│   └── __init__.py
├── ⚙️ utils/                   # Utilitários e configurações
│   ├── config.py              # Configurações globais
│   └── __init__.py
├── 📸 screenshots/             # Screenshots automáticos
├── 📋 main_gui.py              # Executável principal (GUI)
├── 📋 main.py                  # Executável linha de comando
├── 📄 requirements.txt         # Dependências
└── 📖 README.md               # Esta documentação
```

## ⚙️ Configurações

### Credenciais Servopa
- **URL:** `https://www.consorcioservopa.com.br/vendas/login`
- **Login:** `26.350.659/0001-61` (configurável via env SERVOPA_LOGIN)
- **Senha:** `43418` (configurável via env SERVOPA_SENHA)

### Credenciais Todoist
- **URL:** `https://app.todoist.com/auth/login`
- **Email:** `oscarifn6@gmail.com`
- **Senha:** `spfctri12`
- **Projeto:** "Lances Servopa Outubro Dia 8"
- **Tarefa:** "1550 - dia 8"

### Configurações de Performance
- **Timeouts:** 20 segundos
- **Delays entre ações:** 1-3 segundos
- **Digitação natural:** 0.1s por caractere
- **Screenshots automáticos:** Ativado

## 🔄 Fluxo de execução

### 🚀 Interface Gráfica
1. **Inicialização** - Interface moderna é carregada
2. **Login Servopa** - Autenticação automática com delays naturais
3. **Todoist** - Nova aba, login e extração do número da tarefa
4. **Busca Clientes** - Preenchimento do número e busca no sistema
5. **Seleção Cliente** - Clique automático no primeiro cliente da lista
6. **Navegação Lances** - Redirecionamento para página de lances
7. **Finalização** - Screenshots e logs de confirmação

### 📊 Monitoramento em Tempo Real
- Status de cada componente (Servopa, Todoist, Cliente, Lances)
- Barra de progresso com percentual
- Log colorido com timestamps
- Dados extraídos exibidos dinamicamente

## 🖼️ Screenshots gerados

- `screenshots/servopa_login_success.png` - Login Servopa confirmado
- `screenshots/todoist_task_found.png` - Tarefa encontrada no Todoist
- `screenshots/clientes_encontrados.png` - Lista de clientes
- `screenshots/cliente_selecionado.png` - Cliente selecionado
- `screenshots/pagina_lances.png` - Página de lances carregada

## 🛠️ Tratamento de erros

- ✅ Timeouts configuráveis (20s padrão)
- ✅ Screenshots automáticos em caso de erro
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
- **Tratamento robusto de erros** - Screenshots e logs

### Extensibilidade
- Fácil adição de novos sites
- Interface plugável para outras automações
- Configurações via arquivo de config
- Logs estruturados para análise