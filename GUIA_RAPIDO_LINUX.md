# 🚀 Guia Rápido - BCI-ON1 para Linux

## 📋 O que é o BCI-ON1?

O **BCI-ON1** é um sistema automatizado que integra:
- 🏦 **Servopa** (Sistema de leilões)
- ✅ **Todoist** (Gerenciador de tarefas)
- 💬 **Evolution API** (Envio de mensagens WhatsApp)

### Como funciona?
1. **Extrai protocolos** de PDFs do Todoist
2. **Faz login automático** no Servopa
3. **Registra lances** automaticamente
4. **Envia notificações** via WhatsApp
5. **Agenda novas tentativas** automaticamente

---

## 🎯 Instalação Rápida (3 passos)

### **Passo 1: Baixar o instalador**
```bash
curl -O https://raw.githubusercontent.com/dhqdev/bci-on1/main/install.sh
chmod +x install.sh
```

### **Passo 2: Executar a instalação**
```bash
bash install.sh
```

O instalador vai:
- ✅ Verificar Python, Chrome e Git
- ✅ Clonar o repositório
- ✅ Criar ambiente virtual
- ✅ Instalar todas as dependências
- ✅ Configurar o sistema

### **Passo 3: Iniciar o sistema**
```bash
cd /home/david/bci-on1
bash iniciar.sh
```

---

## 🎮 Como Usar o Sistema

### **Método 1: Launcher Interativo (MAIS FÁCIL)** 🌟

```bash
cd /home/david/bci-on1
bash iniciar.sh
```

Você verá um menu visual:

```
╔════════════════════════════════════════════════════════════╗
║  🤖 BCI-ON1 - Sistema de Automação                        ║
║     Servopa + Todoist + Evolution API                     ║
╚════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════
  MENU PRINCIPAL
═══════════════════════════════════════════════════════════

  [1] 🌐 Iniciar Interface Web (Recomendado)
      Abre o sistema no navegador (http://localhost:5000)

  [2] 📊 Ver Status do Sistema
      Verifica Python, Chrome, credenciais e dependências

  [3] 📝 Ver Logs e Histórico
      Visualiza histórico de execuções

  [4] ⚙️  Configurar Credenciais
      Configura Servopa, Todoist e Evolution API

  [5] 🔄 Reinstalar Sistema
      Executa instalação novamente

  [0] 🚪 Sair

═══════════════════════════════════════════════════════════
```

**Escolha a opção 1** e acesse no navegador: `http://localhost:5000`

---

### **Método 2: Comando Direto**

```bash
cd /home/david/bci-on1
bash web/run_web.sh
```

Depois acesse: `http://localhost:5000`

---

## ⚙️ Configuração Inicial

### **1. Configurar Credenciais**

Após iniciar o sistema web, configure:

#### **Servopa:**
- Email
- Senha
- CPF (números apenas)

#### **Todoist:**
- Token API (encontre em: https://todoist.com/prefs/integrations)
- ID do Quadro (opcional)

#### **Evolution API:**
- URL base (ex: https://sua-api.com)
- Token de acesso
- Nome da instância

### **2. Testar Conexões**

Na interface web, clique em:
- ✅ **"Testar Credenciais"** - verifica login no Servopa
- ✅ **"Verificar Conexão"** - testa Evolution API

---

## 🔧 Estrutura do Projeto

```
bci-on1/
├── venv/                    # Ambiente virtual Python (criado na instalação)
├── web/                     # Interface web
│   ├── app.py              # Servidor Flask
│   └── templates/          # Páginas HTML
├── auth/                    # Autenticação
│   ├── servopa_auth.py     # Login Servopa
│   └── todoist_auth.py     # API Todoist
├── automation/              # Automações
│   ├── servopa_lances.py   # Registro de lances
│   └── cycle_orchestrator.py  # Orquestrador
├── utils/                   # Utilitários
│   └── protocol_extractor.py  # Extração de protocolos
├── credentials.json         # Suas credenciais (criar)
├── evolution_config.json    # Config Evolution API
├── iniciar.sh              # 🌟 LAUNCHER PRINCIPAL
├── install.sh              # Instalador
└── web/run_web.sh          # Inicia interface web
```

---

## 🎯 Modos de Operação

### **1. Ciclo Dia 8 (Primeira tentativa)**
- Extrai protocolos do Todoist
- Faz lances no Servopa
- Envia notificações WhatsApp
- Agenda próximo ciclo para dia 16

### **2. Ciclo Dia 16 (Segunda tentativa)**
- Verifica protocolos pendentes
- Tenta novos lances
- Envia notificações finais

---

## 🐛 Solução de Problemas

### **Erro: "ModuleNotFoundError: No module named 'flask'"**

**Causa:** Ambiente virtual não está ativado

**Solução:**
```bash
cd /home/david/bci-on1
bash iniciar.sh
```
Ou:
```bash
bash web/run_web.sh
```

---

### **Erro: "Ambiente virtual não encontrado"**

**Causa:** Sistema não foi instalado

**Solução:**
```bash
cd /home/david/bci-on1
bash install.sh
```

---

### **Erro: "Chrome não encontrado"**

**Solução:**
```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# Fedora/RHEL
sudo dnf install google-chrome-stable
```

---

### **Erro: "Python não encontrado"**

**Solução:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip
```

---

## 📊 Verificar Status do Sistema

Use o launcher interativo:
```bash
cd /home/david/bci-on1
bash iniciar.sh
```

Escolha opção **[2] Ver Status do Sistema**

Você verá:
```
📊 Verificando status do sistema...

   ✅ Python: 3.12.3
   ✅ Chrome: 136.0.7103.92
   ✅ Ambiente Virtual: Configurado
   ✅ Credenciais: Configuradas
```

---

## 🌐 Usando a Interface Web

### **1. Iniciar o servidor**
```bash
bash iniciar.sh  # Opção 1
```

### **2. Acessar no navegador**
```
http://localhost:5000
```

### **3. Páginas disponíveis**

- **🏠 Home** - Visão geral
- **⚙️ Credenciais** - Configurar acesso
- **🤖 Automação Dia 8** - Primeira tentativa de lances
- **🔄 Automação Dia 16** - Segunda tentativa
- **💬 WhatsApp** - Configurar Evolution API
- **📊 Histórico** - Ver execuções anteriores

---

## 🔐 Segurança

### **Arquivo credentials.json**

Este arquivo contém suas senhas. **NUNCA compartilhe!**

```json
{
  "servopa": {
    "email": "seu@email.com",
    "password": "sua_senha",
    "cpf": "12345678900"
  },
  "todoist": {
    "token": "seu_token_todoist"
  }
}
```

### **Arquivo evolution_config.json**

Configuração da API WhatsApp:

```json
{
  "base_url": "https://sua-evolution-api.com",
  "api_key": "seu_token",
  "instance_name": "nome_instancia"
}
```

---

## 📝 Comandos Úteis

### **Iniciar sistema (interface gráfica)**
```bash
bash iniciar.sh
```

### **Iniciar interface web diretamente**
```bash
bash web/run_web.sh
```

### **Verificar logs**
```bash
cat history_dia8.json | tail -20
```

### **Reinstalar sistema**
```bash
bash install.sh
```

### **Atualizar do GitHub**
```bash
git pull origin main
bash install.sh  # Reinstalar dependências
```

---

## 🎓 Fluxo de Trabalho Típico

### **Configuração Inicial (uma vez)**
1. `bash install.sh` - Instalar
2. `bash iniciar.sh` - Abrir menu
3. Opção [1] - Iniciar interface web
4. Configurar credenciais no navegador
5. Testar conexões

### **Uso Diário**
1. `bash iniciar.sh` - Abrir menu
2. Opção [1] - Interface web
3. Acessar `http://localhost:5000`
4. Clicar em **"Automação Dia 8"** ou **"Dia 16"**
5. Iniciar automação
6. Acompanhar pelo histórico

---

## 📞 Suporte

### **Problemas Comuns**

| Erro | Solução |
|------|---------|
| Flask não encontrado | `bash web/run_web.sh` (ativa venv automaticamente) |
| Chrome não abre | Verificar se Chrome está instalado |
| Login falha | Verificar credenciais em `credentials.json` |
| API WhatsApp falha | Verificar `evolution_config.json` |

### **Logs de Debug**

```bash
# Ver últimas execuções
tail -f history_dia8.json

# Ver erros do servidor web
bash web/run_web.sh  # Mostra erros em tempo real
```

---

## ✅ Checklist Rápido

Antes de começar, verifique:

- [ ] Python 3.8+ instalado
- [ ] Google Chrome instalado
- [ ] Git instalado
- [ ] Conexão com internet
- [ ] Credenciais do Servopa
- [ ] Token do Todoist
- [ ] Evolution API configurada (opcional)

---

## 🎉 Pronto para Usar!

```bash
cd /home/david/bci-on1
bash iniciar.sh
```

**Escolha opção [1]** e acesse: `http://localhost:5000`

Boa automação! 🚀
