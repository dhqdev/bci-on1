# 🚀 TESTE RÁPIDO - Correções OXCASH

## ⚡ Teste em 5 Minutos

### **1. Reiniciar Servidor**
```bash
cd web
python app.py
```

Aguarde ver:
```
🚀 OXCASH - Interface Web Moderna
📍 Servidor iniciado em: http://localhost:5000
```

---

### **2. Teste WebSocket (Dia 8)** ⏱️ 2 min

**Passos:**
1. Acesse: `http://localhost:5000/automation/dia8`
2. Abra o **Console do Navegador** (F12 → Console)
3. Clique em **"Iniciar Automação"**

**✅ PASSOU se ver:**
```
✅ Conectado ao servidor
🚀 Iniciando automação DIA8...
🖥️ Abrindo navegador Chrome...
[logs aparecendo em tempo real]
```

**❌ FALHOU se:**
- Console mostrar: `❌ Socket global não encontrado!`
- Logs não aparecerem
- Ficar travado em "Aguardando início..."

---

### **3. Teste Layout WhatsApp** ⏱️ 30 seg

**Passos:**
1. Acesse: `http://localhost:5000/whatsapp`

**✅ PASSOU se ver:**
```
┌──────────────┐  ┌──────────────┐
│  📅 DIA 8   │  │  📅 DIA 16  │
│             │  │             │
│ [Campos]    │  │ [Campos]    │
└──────────────┘  └──────────────┘
```

**❌ FALHOU se:**
- Grupos estiverem empilhados (um abaixo do outro)
- Ocupar tela inteira verticalmente

---

### **4. Teste Badge de Boletos** ⏱️ 1 min

**Passos:**
1. Olhe o **menu lateral** (ícone 📄 Boletos)
2. Veja o badge → deve mostrar **"0"** se não importou ainda
3. Vá em: `http://localhost:5000/boletos`
4. Clique em **"Importar do Todoist"**
5. Aguarde 5 segundos
6. Olhe o **badge no menu lateral** novamente

**✅ PASSOU se:**
- Badge mudou de "0" para número real (ex: 70)
- Mensagem: "Importado: X boletos (dia 08) e Y boletos (dia 16)"

**❌ FALHOU se:**
- Badge continua mostrando "0"
- Badge mostra "70" fixo mesmo sem importar

---

### **5. Teste Histórico** ⏱️ 1 min

**Passos:**
1. Acesse: `http://localhost:5000/history`
2. Em **outra aba**, vá em: `http://localhost:5000/automation/dia8`
3. Inicie a automação
4. **Volte para a aba de histórico**
5. Observe a tabela

**✅ PASSOU se:**
- Registros aparecem **automaticamente** (sem atualizar página)
- Contador nas tabs aumenta: `Dia 8 [1]`, `Dia 8 [2]`, etc.
- Informações completas: hora, grupo, cota, nome, status

**❌ FALHOU se:**
- Nada aparece
- Precisa atualizar (F5) para ver registros
- Campos vazios

---

## 🎯 Checklist Rápida

**Antes de Testar:**
- [ ] Servidor reiniciado
- [ ] Navegador aberto (Chrome recomendado)
- [ ] Console do navegador aberto (F12)

**Testes:**
- [ ] WebSocket Dia 8 funciona
- [ ] WebSocket Dia 16 funciona (mesmos passos)
- [ ] Layout WhatsApp lado a lado
- [ ] Badge atualiza após importação
- [ ] Histórico atualiza em tempo real

---

## 🐛 Se Algo Falhar

### **WebSocket não funciona:**
```bash
# Verifique se Socket.IO está instalado
pip install python-socketio flask-socketio

# Reinicie servidor
cd web
python app.py
```

### **Badge não atualiza:**
1. Abra Console (F12)
2. Digite: `updateBoletosBadge()`
3. Veja se retorna erro

### **Layout WhatsApp empilhado:**
1. Recarregue página (Ctrl+F5)
2. Limpe cache do navegador
3. Teste em modo anônimo

### **Histórico não atualiza:**
1. Verifique Console (F12)
2. Procure por: `Socket global não encontrado`
3. Reinicie navegador

---

## ✅ Tudo Funcionando?

**Parabéns!** 🎉 Todas as correções estão ativas!

### **O que está funcionando agora:**
- ✅ Logs em tempo real nas automações
- ✅ WhatsApp com grupos lado a lado
- ✅ Badge mostrando contagem real
- ✅ Histórico atualizando automaticamente

### **Pode usar normalmente:**
- Automação Dia 8
- Automação Dia 16
- Disparo WhatsApp
- Visualização de histórico
- Importação de boletos

---

## 📞 Suporte Rápido

### **Comandos Úteis:**

**Ver logs do servidor:**
```bash
cd web
python app.py
# Deixe rodando e observe mensagens
```

**Testar WebSocket manualmente:**
```javascript
// No Console do navegador (F12)
socket.emit('test_connection');
// Deve retornar: ✅ Conexão WebSocket OK
```

**Forçar atualização badge:**
```javascript
// No Console do navegador (F12)
updateBoletosBadge();
// Veja badge atualizar imediatamente
```

**Limpar histórico:**
```bash
# No terminal
rm history_dia8.json
rm history_dia16.json
```

---

**Status:** ✅ Pronto para testes  
**Tempo Estimado:** 5 minutos  
**Dificuldade:** Fácil  

**Boa sorte nos testes!** 🚀
