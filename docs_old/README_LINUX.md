# 🚀 BCI-ON1 - Sistema de Automação Servopa

![Status](https://img.shields.io/badge/status-active-success.svg)
![Platform](https://img.shields.io/badge/platform-linux-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

Sistema automatizado de integração entre **Servopa**, **Todoist** e **Evolution API** (WhatsApp).

---

## 📋 O que faz o BCI-ON1?

O BCI-ON1 automatiza todo o fluxo de trabalho de lances no Servopa:

1. 📥 **Extrai protocolos** de PDFs no Todoist
2. 🔐 **Faz login automático** no Servopa
3. 💰 **Registra lances** automaticamente
4. 💬 **Envia notificações** via WhatsApp (Evolution API)
5. 🔄 **Agenda novos ciclos** automaticamente

### Ciclos de Automação

- **Dia 8**: Primeira tentativa de lances
- **Dia 16**: Segunda tentativa (casos pendentes)

---

## ⚡ Instalação Rápida (Linux)

```bash
# Baixar e executar instalador
curl -O https://raw.githubusercontent.com/dhqdev/bci-on1/main/install.sh
chmod +x install.sh
bash install.sh
```

O instalador configura automaticamente:
- ✅ Ambiente virtual Python
- ✅ Todas as dependências
- ✅ ChromeDriver para Selenium
- ✅ Interface web Flask

---

## 🎮 Como Usar

### **Método 1: Launcher Interativo (Recomendado)**

```bash
cd bci-on1
bash iniciar.sh
```

Você verá um menu visual com opções:
- 🌐 Iniciar Interface Web
- 📊 Ver Status do Sistema
- 📝 Ver Logs e Histórico
- ⚙️ Configurar Credenciais
- 🔄 Reinstalar Sistema

### **Método 2: Interface Web Direta**

```bash
cd bci-on1
bash web/run_web.sh
```

Acesse: **http://localhost:5000**

### **Método 3: Atalho Rápido**

Adicione ao seu `~/.bashrc`:

```bash
alias bci='cd ~/bci-on1 && bash iniciar.sh'
```

Depois use: `bci`

---

## 🖥️ Interface Web

A interface web oferece:

- **🏠 Dashboard** - Visão geral do sistema
- **⚙️ Credenciais** - Configurar Servopa, Todoist, Evolution API
- **🤖 Automação Dia 8** - Primeira tentativa de lances
- **🔄 Automação Dia 16** - Segunda tentativa
- **💬 WhatsApp** - Configurar mensagens automáticas
- **📊 Histórico** - Ver execuções anteriores

---

## ⚙️ Configuração

### 1. Credenciais do Servopa

```json
{
  "servopa": {
    "email": "seu@email.com",
    "password": "sua_senha",
    "cpf": "12345678900"
  }
}
```

### 2. Token do Todoist

Obtenha em: https://todoist.com/prefs/integrations

```json
{
  "todoist": {
    "token": "seu_token_aqui",
    "board_id": "id_do_quadro"
  }
}
```

### 3. Evolution API (WhatsApp)

```json
{
  "base_url": "https://sua-evolution-api.com",
  "api_key": "seu_token",
  "instance_name": "nome_instancia"
}
```

Configure tudo pela interface web em: **http://localhost:5000/credentials**

---

## 📁 Estrutura do Projeto

```
bci-on1/
├── 🚀 iniciar.sh              # Launcher principal (USE ESTE!)
├── 📖 GUIA_RAPIDO_LINUX.md    # Documentação completa
├── 📝 COMO_EXECUTAR_LINUX.sh  # Guia visual rápido
├── web/
│   ├── app.py                 # Servidor Flask
│   ├── run_web.sh             # Inicia servidor web
│   └── templates/             # Páginas HTML
├── auth/
│   ├── servopa_auth.py        # Autenticação Servopa
│   └── todoist_auth.py        # API Todoist
├── automation/
│   ├── servopa_lances.py      # Sistema de lances
│   └── cycle_orchestrator.py # Orquestrador de ciclos
├── utils/
│   └── protocol_extractor.py # Extração de protocolos PDF
├── credentials.json           # Suas credenciais
└── evolution_config.json      # Config WhatsApp
```

---

## 🔧 Requisitos

- **Python 3.8+**
- **Google Chrome** ou Chromium
- **Git**
- **Linux** (Ubuntu, Debian, Fedora, etc.)

---

## 🐛 Solução de Problemas

### ❌ Erro: "ModuleNotFoundError: No module named 'flask'"

**Causa:** Você executou `python app.py` diretamente sem ativar o ambiente virtual.

**Solução:**
```bash
bash web/run_web.sh  # Ativa ambiente automaticamente
```

---

### ❌ Erro: "Ambiente virtual não encontrado"

**Causa:** Sistema não foi instalado.

**Solução:**
```bash
bash install.sh
```

---

### ❌ Erro: "Chrome não encontrado"

**Solução:**
```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# Fedora/RHEL
sudo dnf install google-chrome-stable
```

---

### ❌ Erro: "Python não encontrado"

**Solução:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk

# Fedora/RHEL
sudo dnf install python3 python3-pip python3-tkinter
```

---

## 📊 Verificar Status

Use o launcher:

```bash
bash iniciar.sh
```

Escolha **[2] Ver Status do Sistema**

Resultado:
```
📊 Verificando status do sistema...

   ✅ Python: 3.12.3
   ✅ Chrome: 136.0.7103.92
   ✅ Ambiente Virtual: Configurado
   ✅ Credenciais: Configuradas
```

---

## 📝 Logs e Histórico

Ver logs recentes:
```bash
cat history_dia8.json | tail -20
```

Ou use o launcher:
```bash
bash iniciar.sh  # Opção [3]
```

---

## 🔄 Atualizar Sistema

```bash
cd bci-on1
git pull origin main
bash install.sh  # Reinstalar dependências
```

---

## 🎯 Fluxo de Trabalho

### Primeira Vez
1. `bash install.sh` - Instalar
2. `bash iniciar.sh` - Menu principal
3. Opção [1] - Iniciar web
4. Configurar credenciais
5. Testar conexões

### Uso Diário
1. `bash iniciar.sh`
2. Opção [1] - Web
3. Acessar automação
4. Iniciar ciclo
5. Acompanhar resultados

---

## 📚 Documentação Adicional

- 📖 **[GUIA_RAPIDO_LINUX.md](GUIA_RAPIDO_LINUX.md)** - Documentação completa
- 📝 **COMO_EXECUTAR_LINUX.sh** - Guia visual rápido
- 🔧 **TROUBLESHOOTING.md** - Solução de problemas
- 📋 **CHANGELOG_v2.0.md** - Histórico de alterações

---

## 🎓 Comandos Essenciais

```bash
# Iniciar (RECOMENDADO)
bash iniciar.sh

# Interface web direta
bash web/run_web.sh

# Verificar instalação
bash iniciar.sh  # Opção [2]

# Ver logs
bash iniciar.sh  # Opção [3]

# Reinstalar
bash install.sh
```

---

## ⚠️ Importante

- 🔐 **Nunca compartilhe** `credentials.json`
- 🔒 **Nunca faça commit** de senhas no Git
- 🔄 **Sempre use** os scripts fornecidos (não execute Python diretamente)
- 📝 **Acompanhe os logs** para diagnóstico

---

## 🚀 Começar Agora

```bash
cd bci-on1
bash iniciar.sh
```

Escolha **[1]** e acesse: **http://localhost:5000**

---

## 📞 Suporte

Para problemas:
1. Leia **GUIA_RAPIDO_LINUX.md**
2. Execute `bash iniciar.sh` → Opção [2] (Status)
3. Verifique **TROUBLESHOOTING.md**

---

## 📜 Licença

Este projeto é de uso interno e privado.

---

## ✨ Características

- ✅ Interface web moderna e responsiva
- ✅ Automação completa de lances
- ✅ Integração WhatsApp (Evolution API)
- ✅ Extração automática de protocolos
- ✅ Sistema de retry inteligente
- ✅ Logs detalhados e histórico
- ✅ Modo headless (sem interface gráfica)
- ✅ Scheduler automático

---

**Desenvolvido com ❤️ para automatizar o Servopa**
