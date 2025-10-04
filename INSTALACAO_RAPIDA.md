# 🚀 GUIA RÁPIDO - INSTALAÇÃO EM 1 COMANDO

## ⚡ Instalação Instantânea (Windows)

**Cole este comando no PowerShell e pressione ENTER:**

```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex
```

**Pronto!** O script vai:
- ✅ Pedir permissão de Administrador (se necessário)
- ✅ Instalar Git automaticamente
- ✅ Instalar Python automaticamente  
- ✅ Configurar tudo sozinho
- ✅ Criar atalho na área de trabalho

---

## 📌 Como Iniciar Depois de Instalado

### **OPÇÃO 1 - Mais Fácil:**
Clique duas vezes no atalho **"BCI-ON1 Web"** na sua área de trabalho

### **OPÇÃO 2 - Manual:**
Clique duas vezes em: `Desktop\bci-on1\INICIAR_BCI.bat`

**Acesse no navegador:** http://localhost:5000

---

## ❓ Perguntas Frequentes

### **Preciso instalar Git ou Python antes?**
❌ **NÃO!** O script instala tudo automaticamente.

### **Preciso configurar PATH ou variáveis de ambiente?**
❌ **NÃO!** Tudo é configurado automaticamente.

### **Funciona em qualquer Windows?**
✅ **SIM!** Windows 10 e 11.

### **E se eu não souber nada de programação?**
✅ **Perfeito!** Foi feito exatamente para isso.

---

## 🆘 Deu Erro?

### **Erro de Permissão:**
1. Feche o PowerShell
2. Botão direito no PowerShell
3. Escolha **"Executar como Administrador"**
4. Cole o comando novamente

### **Git/Python não instalou:**
O script tenta instalar automaticamente. Se falhar:
1. Reinicie o computador
2. Execute o comando novamente

### **Ainda com problemas?**
Consulte: `MELHORIAS_INSTALADOR_AUTOMATICO.md`

---

## 📚 Mais Informações

- **Documentação Completa:** `README.md`
- **Changelog:** `CHANGELOG_MODIFICACOES.txt`
- **Melhorias do Instalador:** `MELHORIAS_INSTALADOR_AUTOMATICO.md`

---

**Versão:** 2.0 - Instalação 100% Automática  
**Atualizado:** $(Get-Date -Format "dd/MM/yyyy")
