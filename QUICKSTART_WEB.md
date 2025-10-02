# 🚀 Guia Rápido - Interface Web OXCASH

## 📋 Início Rápido (3 passos)

### 1️⃣ **Instalar Dependências Web**
```bash
# Linux/Mac
pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio

# Ou deixe o script instalar automaticamente
```

### 2️⃣ **Iniciar Servidor**
```bash
# Linux/Mac
./run_web.sh

# Windows
run_web.bat
```

### 3️⃣ **Acessar no Navegador**
```
http://localhost:5000
```

---

## 🎯 Funcionalidades Principais

### 📊 **Dashboard** (Página Inicial)
- **Veja estatísticas:** Total de lances, sucessos, falhas
- **Gráficos:** Pizza interativo Dia 8 e Dia 16
- **Status:** Veja se automações estão rodando
- **Ações rápidas:** Botões para todas as páginas

### 🤖 **Automação Dia 8**
1. Acesse: Menu > Dia 8
2. Configure credenciais (se ainda não fez)
3. Clique em **"🚀 Iniciar Automação"**
4. Acompanhe logs em tempo real
5. Veja progresso na barra
6. Pare a qualquer momento com **"⏹️ Parar"**

### 🤖 **Automação Dia 16**
- Mesma interface do Dia 8
- Usa board diferente do Todoist
- Histórico separado

### 📱 **WhatsApp**
1. **Configure API:**
   - URL (bloqueada): `https://zap.tekvosoft.com`
   - Nome da Instância
   - API Key
   
2. **Grupo Dia 8:**
   - Cole contatos (um por linha)
   - Formato: `5519995378302 - Nome Cliente`
   - Digite mensagem (use `{nome}` para personalizar)
   - Clique **"📤 Enviar Agora"**

3. **Grupo Dia 16:**
   - Mesmos passos do Dia 8

### 📈 **Histórico**
- **Tab Dia 8:** Veja todos os lances do dia 8
- **Tab Dia 16:** Veja todos os lances do dia 16
- **Atualização automática:** A cada 10 segundos
- **Informações:** Hora, Grupo, Cota, Nome, Valor, Protocolo, Status

### 🔐 **Credenciais**
1. **Servopa:**
   - Digite usuário
   - Digite senha
   
2. **Todoist:**
   - Digite usuário (email)
   - Digite senha

3. Clique **"💾 Salvar Credenciais"**

---

## 💡 Dicas de Uso

### ✅ **Boas Práticas**
- Configure credenciais **ANTES** de iniciar automação
- Acompanhe os logs para ver o que está acontecendo
- Use **"⏹️ Parar"** se encontrar problemas
- Verifique histórico após execução
- Mantenha navegador aberto durante automação

### ⚡ **Atalhos Úteis**
- `Ctrl + R`: Recarrega página
- `F5`: Atualiza dados
- `F12`: Console do navegador (debug)

### 🔍 **Monitoramento**
- **Dashboard:** Visão geral de tudo
- **Cards coloridos:** Status visual rápido
  - 🟢 Verde = Sucesso
  - 🔴 Vermelho = Erro
  - 🟡 Amarelo = Executando
  - ⚫ Cinza = Parado

### 🌐 **WebSocket**
- Conexão em tempo real
- Badge no canto superior direito:
  - 🟢 "Conectado" = OK
  - 🔴 "Desconectado" = Problemas

---

## 🐛 Resolução de Problemas

### ❌ **"Porta 5000 em uso"**
```bash
# Linux/Mac
sudo lsof -i :5000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### ❌ **"Module 'flask' not found"**
```bash
pip install Flask Flask-SocketIO Flask-CORS
```

### ❌ **"WebSocket não conecta"**
1. Verifique se servidor está rodando
2. Recarregue página (F5)
3. Veja console do navegador (F12)

### ❌ **"Credenciais não salvam"**
1. Verifique permissões do arquivo `credentials.json`
2. Veja console do navegador (F12) para erros
3. Tente via interface desktop (Tkinter)

---

## 🎨 Personalizações

### **Mudar Porta**
Edite `web/app.py`, última linha:
```python
socketio.run(app, host='0.0.0.0', port=SUAPORTA, debug=True)
```

### **Acessar de Outros Dispositivos**
1. Descubra seu IP: `ifconfig` (Linux/Mac) ou `ipconfig` (Windows)
2. Acesse: `http://SEU_IP:5000`
3. Certifique-se que firewall permite conexões

---

## 📱 Mobile

A interface é **responsiva** e funciona em:
- 📱 Smartphones
- 📱 Tablets
- 💻 Desktop

Acesse pelo navegador do dispositivo móvel usando o IP do servidor.

---

## 🆚 Interface Desktop vs Web

### **Desktop (Tkinter)** - `./run.sh`
- ✅ Interface tradicional
- ✅ Tudo funciona offline
- ✅ Não precisa navegador

### **Web (Flask)** - `./run_web.sh`
- ✅ Interface moderna
- ✅ Gráficos interativos
- ✅ Acesso remoto
- ✅ Melhor visualização

**🎯 Use a que preferir! Ambas têm as mesmas funcionalidades.**

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique logs no console
2. Veja terminal onde servidor roda
3. Teste interface desktop (`./run.sh`)
4. Verifique `web/README_WEB.md` para mais detalhes

---

**Desenvolvido para OXCASH** 🏆
*Simples. Moderno. Eficiente.*
