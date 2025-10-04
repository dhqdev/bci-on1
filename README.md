# 🤖 BCI-ON1 - Sistema de Automação Servopa + Todoist

Sistema completo de automação para gerenciamento de lances no Servopa, integrado com Todoist e WhatsApp via Evolution API. **Interface Web Moderna** (Flask + Bootstrap 5).

---

## 📋 Sobre o Projeto

O **BCI-ON1** é um sistema de automação desenvolvido para simplificar e automatizar processos de licitação no portal Servopa. O sistema realiza login automático, extrai protocolos do Todoist, envia lances e notifica clientes via WhatsApp nos dias 8 e 16 de cada mês.

### 🎯 Funcionalidades Principais

- ✅ **Automação Dia 8**: Login Servopa → Extração Todoist → Envio de Lances → Notificação WhatsApp
- ✅ **Automação Dia 16**: Mesma rotina para o segundo ciclo mensal
- ✅ **WhatsApp Bulk Send**: Envio em massa via Evolution API com suporte a grupos
- ✅ **Interface Web Moderna**: Dashboard com gráficos, logs em tempo real e controle remoto
- ✅ **Histórico Completo**: Registro de todas as execuções em JSON
- ✅ **Gerenciamento de Credenciais**: Interface amigável para configurar logins

---

## 🚀 Instalação

### Requisitos

- **Python**: 3.8 ou superior
- **Google Chrome**: Versão estável
- **Sistema Operacional**: Windows, Linux ou macOS
- **Conexão Internet**: Para automação e WhatsApp

### Instalação Rápida (Recomendado)

**Instala TUDO com 1 comando diretamente do GitHub:**

#### Linux / macOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-linux.sh)
```

#### Windows (PowerShell como Administrador)

**🌟 MÉTODO MAIS FÁCIL (Sem problemas de ExecutionPolicy):**
```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex
```

**OPÇÃO 2 - Download e Execução Manual:**
```powershell
# Se der erro de ExecutionPolicy, use este antes:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Depois execute:
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.ps1 -OutFile setup.ps1; .\setup.ps1
```

🆕 **O instalador rápido agora usa o winget automaticamente (quando disponível)** para instalar Git, Python 3.11 e Google Chrome, configurando o PATH do sistema mesmo em máquinas novas. Se o winget não estiver presente, o script baixa os instaladores oficiais em modo silencioso e finaliza a configuração para você.

**OPÇÃO 3 - Sem PowerShell (Prompt de Comando):**
```cmd
git clone https://github.com/dhqdev/bci-on1.git
cd bci-on1
install.bat
```

⚠️ **Problemas com ExecutionPolicy?** Veja: [INSTALACAO_WINDOWS_POWERSHELL.md](INSTALACAO_WINDOWS_POWERSHELL.md)

**OPÇÃO 3 - Instalador Batch Simplificado (se os outros travarem):**
```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows-simple.bat -OutFile setup.bat; .\setup.bat
```

> ⚠️ **Nota:** Use a OPÇÃO 1 (PowerShell) se tiver problemas com as outras.  
> Se já tem instalado e o instalador travar, delete manualmente a pasta `%USERPROFILE%\bci-on1` antes de reinstalar.

**🎉 Após instalação, um atalho "BCI-ON1 Web" (.lnk) é criado automaticamente na sua área de trabalho!**

---

### Instalação Manual

**Se preferir clonar primeiro e depois instalar:**

#### Linux / macOS

```bash
# Clone o repositório
git clone https://github.com/dhqdev/bci-on1.git
cd bci-on1

# Execute o instalador
bash install.sh
```

#### Windows

```
1. Clone ou baixe o repositório
2. Navegue até a pasta bci-on1
3. Clique duas vezes em: install.bat
```

---

### O Que o Instalador Faz

### O Que o Instalador Faz

O instalador irá:
- ✅ Instalar Git (se necessário)
- ✅ Verificar/Instalar Python 3.8+ (se necessário)
- ✅ Instalar Google Chrome (se necessário)
- ✅ Clonar repositório do GitHub (instalação rápida)
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências (Selenium, Flask, etc.)
- ✅ Configurar arquivos necessários
- ✅ Testar instalação

---

## 🎮 Como Usar

### Interface Web (Moderna) - RECOMENDADO

#### Opção 1: Usar o Atalho da Área de Trabalho (Windows)
```
Clique duas vezes em: BCI-ON1 Web
```

#### Opção 2: Linha de Comando

**Linux / macOS:**
```bash
bash web/run_web.sh
```

**Windows:**
```
cd web
run_web.bat
```

#### Opção 3: Manual
```bash
cd web
python app.py
```

**Depois acesse no navegador:**
```
http://localhost:5000
```

**Funcionalidades Web:**
- 📊 **Dashboard**: Estatísticas e gráficos interativos (Chart.js)
- 🎯 **Automação**: Controle Dia 8/16 com logs ao vivo via WebSocket
- 📱 **WhatsApp**: Envio em massa para grupos com preview
- 📜 **Histórico**: Visualização de execuções passadas
- ⚙️ **Credenciais**: Gerenciamento de logins
- 📱 **Responsivo**: Funciona em mobile e desktop
- 🔄 **Tempo Real**: Updates instantâneos via WebSocket

---

## ⚙️ Configuração

### 1. Credenciais Servopa e Todoist

**Interface Web:**
- Acesse http://localhost:5000/credentials
- Preencha os campos
- Clique em "Salvar Credenciais"

### 2. Configuração WhatsApp (Evolution API)

Edite o arquivo `evolution_config.json`:

```json
{
  "api": {
    "base_url": "https://sua-evolution-api.com",
    "instance_name": "sua-instancia",
    "api_key": "SUA-API-KEY"
  },
  "grupos": {
    "grupo1": {
      "nome": "Grupo Dia 8",
      "contatos": [
        {
          "phone": "5519999999999",
          "name": "Cliente 1"
        }
      ]
    },
    "grupo2": {
      "nome": "Grupo Dia 16",
      "contatos": [
        {
          "phone": "5519888888888",
          "name": "Cliente 2"
        }
      ]
    }
  },
  "mensagens": {
    "dia7": {
      "grupo1": "Olá {nome}! Lembrete: amanhã é dia 8...",
      "grupo2": "Oi {nome}! Importante: dia 8 é amanhã..."
    },
    "dia15": {
      "grupo1": "Olá {nome}! Lembrete: amanhã é dia 16...",
      "grupo2": "Oi {nome}! Importante: dia 16 é amanhã..."
    }
  },
  "configuracoes": {
    "delay_entre_mensagens": 2.0,
    "tentar_reenviar_falhas": true,
    "max_tentativas": 3
  }
}
```

---

## 📁 Estrutura do Projeto

```
bci-on1/
├── auth/                          # Módulos de autenticação
│   ├── servopa_auth.py           # Login Servopa
│   └── todoist_auth.py           # Login Todoist
├── automation/                    # Módulos de automação
│   ├── cycle_orchestrator.py    # Orquestrador de ciclo completo
│   ├── message_scheduler.py     # Agendamento de mensagens
│   ├── servopa_automation.py    # Automação Servopa
│   └── servopa_lances.py         # Envio de lances
├── ui/                            # Interfaces de usuário
│   ├── automation_gui.py         # GUI Tkinter simples
│   └── modern_automation_gui.py  # GUI Tkinter moderna
├── utils/                         # Utilitários
│   ├── auto_todolist_extractor.py      # Extração Todoist automática
│   ├── config.py                        # Configurações
│   ├── evolution_api.py                 # Cliente Evolution API
│   ├── protocol_extractor.py           # Extração de protocolos
│   ├── todoist_board_extractor.py      # Board Todoist
│   └── todoist_simple_extractor.py     # Extração simples
├── web/                           # Interface Web (Flask)
│   ├── app.py                    # Servidor Flask principal
│   ├── run_web.sh                # Script execução Linux/Mac
│   ├── run_web.bat               # Script execução Windows
│   ├── templates/                # Templates HTML
│   │   ├── base.html            # Template base
│   │   ├── index.html           # Dashboard
│   │   ├── automation_dia8.html # Controle Dia 8
│   │   ├── automation_dia16.html# Controle Dia 16
│   │   ├── whatsapp.html        # WhatsApp bulk send
│   │   ├── history.html         # Histórico
│   │   └── credentials.html     # Gerenciamento credenciais
│   └── static/                   # Arquivos estáticos
│       ├── css/style.css        # CSS customizado
│       └── js/common.js         # JavaScript utilities
├── credentials.json              # Credenciais (não versionar!)
├── evolution_config.json         # Config WhatsApp
├── history_dia8.json             # Histórico Dia 8
├── history_dia16.json            # Histórico Dia 16
├── main_gui.py                   # Launcher interface desktop
├── main.py                       # Script principal CLI
├── requirements.txt              # Dependências Python
├── install.sh                    # Instalador Linux/Mac
├── install.bat                   # Instalador Windows
├── update.sh                     # Atualizador Linux/Mac
├── update.bat                    # Atualizador Windows
├── run.sh                        # Executar desktop Linux/Mac
├── run.bat                       # Executar desktop Windows
└── README.md                     # Este arquivo
```

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**: Linguagem principal
- **Selenium**: Automação de navegador
- **Flask 3.0+**: Framework web
- **Flask-SocketIO**: WebSocket para tempo real
- **Requests**: Requisições HTTP
- **BeautifulSoup4**: Parsing HTML
- **Schedule**: Agendamento de tarefas

### Frontend (Interface Web)
- **Bootstrap 5**: Framework CSS
- **Chart.js 4.4**: Gráficos interativos
- **Socket.IO 4.5**: Cliente WebSocket
- **Font Awesome 6.4**: Ícones
- **JavaScript ES6+**: Interatividade

### Automação
- **ChromeDriver**: Driver Selenium para Chrome
- **Webdriver Manager**: Gerenciamento automático de drivers

---

## 📊 Dependências

Todas as dependências estão listadas em `requirements.txt`:

```
selenium>=4.15.0
webdriver-manager>=4.0.1
requests>=2.31.0
beautifulsoup4>=4.12.2
schedule>=1.2.0
Flask>=3.0.0
Flask-SocketIO>=5.3.0
Flask-CORS>=4.0.0
python-socketio>=5.10.0
python-engineio>=4.8.0
```

---

## 🔄 Atualização

Para atualizar o sistema com as últimas mudanças do GitHub:

### Linux / macOS
```bash
bash update.sh
```

### Windows
```
Clique duas vezes em: update.bat
```

O atualizador irá:
- ✅ Fazer backup das configurações
- ✅ Buscar atualizações do GitHub
- ✅ Aplicar mudanças
- ✅ Atualizar dependências Python
- ✅ Restaurar configurações

---

## 🧪 Testes

### Verificar Instalação Web

```bash
bash verify_web_setup.sh
```

Este script verifica:
- ✅ Estrutura de arquivos web
- ✅ Dependências Flask instaladas
- ✅ Ambiente virtual configurado
- ✅ Sintaxe Python válida
- ✅ Permissões de execução

### Testar Credenciais

```bash
python test_credentials.py
```

### Testar Ciclo Completo

```bash
python test_cycle_complete.py
```

---

## 📱 Evolution API - WhatsApp

O sistema integra com a Evolution API para envio de mensagens WhatsApp.

### Configuração

1. Configure sua instância Evolution API
2. Obtenha a API Key
3. Edite `evolution_config.json`
4. Configure grupos e mensagens

### Recursos

- ✅ Envio em massa com delay configurável
- ✅ Suporte a múltiplos grupos
- ✅ Mensagens personalizadas com variável `{nome}`
- ✅ Retry automático em caso de falha
- ✅ Logs detalhados de envio
- ✅ Interface web para envio manual

---

## 🔐 Segurança

### Credenciais

- ⚠️ **NUNCA** commite o arquivo `credentials.json`
- ⚠️ Adicione ao `.gitignore`
- ⚠️ Mantenha backups seguros
- ⚠️ Use variáveis de ambiente em produção

### Boas Práticas

- 🔒 Execute em rede segura
- 🔒 Use senhas fortes
- 🔒 Mantenha Python e dependências atualizadas
- 🔒 Revise logs regularmente
- 🔒 Faça backups periódicos

---

## 📝 Logs e Histórico

### Logs em Tempo Real

**Interface Desktop**: Console integrado
**Interface Web**: Logs via WebSocket no navegador

### Histórico JSON

- `history_dia8.json`: Todas as execuções do Dia 8
- `history_dia16.json`: Todas as execuções do Dia 16

Formato:
```json
{
  "timestamp": "2025-10-02 14:30:00",
  "status": "success",
  "servopa": "OK",
  "todoist": "OK",
  "cliente": "OK",
  "lances": "OK",
  "whatsapp": "5/5 enviados"
}
```

---

## 🐛 Solução de Problemas

### Problema: ModuleNotFoundError: No module named 'flask'

**Solução:**
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate.bat  # Windows

pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
```

### Problema: Chrome/ChromeDriver incompatíveis

**Solução:**
```bash
# O webdriver-manager atualiza automaticamente
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### Problema: Porta 5000 já está em uso

**Solução:** Edite `web/app.py` linha final:
```python
socketio.run(app, host='0.0.0.0', port=5001, debug=False)
```

### Problema: Permission denied ao executar scripts

**Solução:**
```bash
chmod +x install.sh update.sh run.sh web/run_web.sh verify_web_setup.sh
```

### Problema: Evolution API retorna erro 401

**Solução:** Verifique `api_key` em `evolution_config.json`

---

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é de uso privado. Todos os direitos reservados.

---

## 👥 Autores

- **David** - Desenvolvimento e Manutenção

---

## 📞 Suporte

Para suporte e dúvidas:

1. Execute o script de verificação: `bash verify_web_setup.sh`
2. Verifique logs no terminal
3. Consulte este README
4. Abra uma issue no GitHub

---

## 🎉 Agradecimentos

- Selenium WebDriver
- Flask Framework
- Bootstrap
- Chart.js
- Evolution API
- Comunidade Python

---

## 📈 Roadmap

- [ ] Agendamento automático de execuções
- [ ] Dashboard com métricas avançadas
- [ ] Notificações por e-mail
- [ ] Suporte a múltiplos usuários
- [ ] API REST completa
- [ ] Modo headless para servidor
- [ ] Docker container
- [ ] Integração com mais APIs

---

**Versão**: 2.0.0  
**Última Atualização**: Outubro 2025  
**Status**: ✅ Produção

---

<div align="center">

**Desenvolvido com ❤️ por David**

[⬆ Voltar ao topo](#-bci-on1---sistema-de-automação-servopa--todoist)

</div>
