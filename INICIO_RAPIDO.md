# ⚡ INÍCIO RÁPIDO - BCI-ON1 (Linux)

## 🎯 Para Começar AGORA (2 comandos)

### Se já instalou:
```bash
cd /home/david/bci-on1
bash iniciar.sh
```

### Se ainda NÃO instalou:
```bash
cd /home/david/bci-on1
bash install.sh
```

---

## 📖 O que é o BCI-ON1?

**Robô automatizado** que:
- 📥 Pega protocolos do **Todoist**
- 🎯 Faz lances no **Servopa** automaticamente
- 💬 Envia notificações pelo **WhatsApp**
- 🔄 Agenda novos ciclos sozinho

---

## 🚀 PASSO A PASSO VISUAL

### **1️⃣ Abrir o Terminal**

Pressione: `Ctrl + Alt + T`

### **2️⃣ Navegar até a pasta**

```bash
cd /home/david/bci-on1
```

### **3️⃣ Executar o Launcher**

```bash
bash iniciar.sh
```

### **4️⃣ Você verá este menu:**

```
╔════════════════════════════════════════════════════════════╗
║  🤖 BCI-ON1 - Sistema de Automação                        ║
║     Servopa + Todoist + Evolution API                     ║
╚════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════
  MENU PRINCIPAL
═══════════════════════════════════════════════════════════

  [1] 🌐 Iniciar Interface Web (Recomendado)
  [2] 📊 Ver Status do Sistema
  [3] 📝 Ver Logs e Histórico
  [4] ⚙️  Configurar Credenciais
  [5] 🔄 Reinstalar Sistema
  [0] 🚪 Sair

═══════════════════════════════════════════════════════════

Escolha uma opção [0-5]:
```

### **5️⃣ Digite 1 e pressione ENTER**

O sistema vai:
1. ✅ Ativar ambiente Python
2. ✅ Verificar dependências
3. ✅ Iniciar servidor web
4. ✅ Mostrar: "Acesse http://localhost:5000"

### **6️⃣ Abrir navegador**

No navegador, acesse:
```
http://localhost:5000
```

### **7️⃣ Configurar credenciais (primeira vez)**

Na página web:
1. Clique em **"Configurar Credenciais"**
2. Preencha:
   - 📧 Email Servopa
   - 🔑 Senha Servopa
   - 🆔 CPF
   - 🎫 Token Todoist
   - 📱 Dados Evolution API (WhatsApp)
3. Clique **"Salvar"**

### **8️⃣ Executar automação**

1. Clique em **"Automação Dia 8"** ou **"Dia 16"**
2. Clique **"Iniciar Automação"**
3. Acompanhe o progresso na tela

---

## 🎬 Visual dos Passos

```
Terminal → cd bci-on1 → bash iniciar.sh → [1] → Navegador → Configurar → Executar
   ↓           ↓              ↓           ↓         ↓            ↓           ↓
  Abrir    Navegar       Launcher      Menu     Acesso      Credenciais  Automação
                                                localhost
```

---

## ❓ Problemas Comuns

### ❌ "ModuleNotFoundError: No module named 'flask'"

**CAUSA:** Você executou `python app.py` diretamente

**SOLUÇÃO:** Use sempre:
```bash
bash iniciar.sh   # ou
bash web/run_web.sh
```

Estes scripts ativam o ambiente virtual automaticamente!

---

### ❌ "Ambiente virtual não encontrado"

**CAUSA:** Sistema não foi instalado

**SOLUÇÃO:**
```bash
cd /home/david/bci-on1
bash install.sh
```

---

### ❌ "Chrome não encontrado"

**SOLUÇÃO:**
```bash
sudo apt install google-chrome-stable
```

---

### ❌ Servidor não inicia

**SOLUÇÃO:** Verifique se porta 5000 está livre:
```bash
sudo lsof -i :5000
# Se algo estiver usando, mate o processo ou mude a porta
```

---

## 🆘 Comandos de Emergência

### Ver status do sistema
```bash
bash iniciar.sh
# Escolha opção [2]
```

### Ver logs recentes
```bash
bash iniciar.sh
# Escolha opção [3]
```

### Reinstalar tudo
```bash
bash install.sh
```

### Verificar ambiente Python
```bash
cd /home/david/bci-on1
source venv/bin/activate
python --version
pip list | grep -i flask
deactivate
```

---

## 📱 Criar Atalho no Desktop

### Opção 1: Alias no Terminal

Adicione ao `~/.bashrc`:
```bash
echo "alias bci='cd /home/david/bci-on1 && bash iniciar.sh'" >> ~/.bashrc
source ~/.bashrc
```

Depois use apenas: `bci`

### Opção 2: Atalho Gráfico

Crie arquivo `~/Desktop/BCI-ON1.desktop`:
```desktop
[Desktop Entry]
Name=BCI-ON1
Comment=Sistema de Automação Servopa
Exec=gnome-terminal -- bash -c "cd /home/david/bci-on1 && bash iniciar.sh; exec bash"
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Utility;
```

Torne executável:
```bash
chmod +x ~/Desktop/BCI-ON1.desktop
```

---

## 📚 Documentação Completa

Para mais detalhes, leia:

- **📖 GUIA_RAPIDO_LINUX.md** - Guia completo
- **📝 COMO_EXECUTAR_LINUX.sh** - Guia visual (execute-o!)
- **🔧 TROUBLESHOOTING.md** - Solução de problemas

---

## ✅ Checklist Antes de Usar

- [ ] Python 3.8+ instalado
- [ ] Google Chrome instalado
- [ ] Sistema instalado (`bash install.sh`)
- [ ] Credenciais Servopa em mãos
- [ ] Token Todoist disponível
- [ ] Evolution API configurada (opcional)

---

## 🎯 Resumo Ultra-Rápido

```bash
# Terminal
cd /home/david/bci-on1
bash iniciar.sh

# Digite: 1

# Navegador
http://localhost:5000

# Configure e execute!
```

---

## 💡 DICA IMPORTANTE

**NUNCA execute `python` diretamente!**

❌ ERRADO:
```bash
cd web
python app.py  # ❌ Vai dar erro de módulos!
```

✅ CERTO:
```bash
bash iniciar.sh      # ✅ Ativa ambiente automaticamente
bash web/run_web.sh  # ✅ Ativa ambiente automaticamente
```

---

## 🎉 Pronto!

Agora você sabe como executar o BCI-ON1!

```bash
bash iniciar.sh
```

**Boa automação!** 🚀
