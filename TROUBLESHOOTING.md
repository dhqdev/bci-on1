# 🔧 Guia de Solução de Problemas - BCI-ON1

## ❌ Problemas Comuns Durante a Instalação

### 1. "Diretório já existe" e trava ao escolher opção

**Sintoma:** O instalador pergunta se quer remover e reinstalar, você digita "s" mas nada acontece.

**Causa:** Arquivos do diretório podem estar sendo usados por outro programa.

**Solução:**
1. Feche todos os programas que possam estar usando o BCI-ON1:
   - Navegador (Chrome, Edge, Firefox)
   - VS Code ou qualquer editor de código
   - Terminal/PowerShell abertos na pasta do projeto
   - Explorador de Arquivos na pasta do projeto

2. Execute o instalador novamente

3. **OU** escolha opção `[1] Atualizar projeto existente` ao invés de remover

4. **OU** delete manualmente a pasta:
   ```powershell
   Remove-Item -Recurse -Force "$env:USERPROFILE\bci-on1"
   ```

---

### 2. "Git não encontrado" ou erro ao instalar Git

**Solução:**
1. Execute o PowerShell **como Administrador**
2. Execute o instalador novamente

**OU** instale o Git manualmente:
- Download: https://git-scm.com/download/win
- Instale e reinicie o PowerShell

---

### 3. "Python não encontrado"

**Solução:**
1. Baixe Python 3.8+ em: https://www.python.org/downloads/
2. Durante instalação, marque **"Add Python to PATH"**
3. Reinicie o PowerShell
4. Execute o instalador novamente

---

### 4. "Chrome não instalado" ou erro ao instalar Chrome

**Solução:**
- Instale manualmente: https://www.google.com/chrome/
- Reinicie o instalador

---

### 5. Erro ao clonar repositório do GitHub

**Sintomas:**
- `fatal: unable to access`
- `Connection timeout`
- `Could not resolve host`

**Soluções:**
1. Verifique sua conexão com internet
2. Se estiver atrás de proxy/firewall corporativo, configure o Git:
   ```bash
   git config --global http.proxy http://proxy:porta
   ```
3. Tente clonar manualmente:
   ```powershell
   cd $env:USERPROFILE
   git clone https://github.com/dhqdev/bci-on1.git
   cd bci-on1
   .\install.bat
   ```

---

## ❌ Problemas ao Executar

### 1. "Ambiente virtual não encontrado"

**Solução:**
```powershell
cd $env:USERPROFILE\bci-on1
.\install.bat
```

---

### 2. Porta 5000 já está em uso

**Sintoma:** Erro ao iniciar: `Address already in use`

**Solução:**

**Opção 1:** Feche o programa usando a porta 5000
```powershell
# Ver o que está usando a porta 5000
netstat -ano | findstr :5000

# Matar o processo (substitua PID pelo número da última coluna)
taskkill /PID <PID> /F
```

**Opção 2:** Mude a porta no arquivo `web/app.py`:
```python
# Na última linha, mude de:
socketio.run(app, host='0.0.0.0', port=5000, debug=True)

# Para:
socketio.run(app, host='0.0.0.0', port=8080, debug=True)
```

---

### 3. Erro "Module not found"

**Sintoma:** `ModuleNotFoundError: No module named 'flask'`

**Solução:**
```powershell
cd $env:USERPROFILE\bci-on1
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

### 4. Erro ao fazer login no Servopa/Todoist

**Causas possíveis:**
- Credenciais incorretas
- Servopa/Todoist mudou layout do site
- ChromeDriver incompatível

**Soluções:**
1. Verifique credenciais em: http://localhost:5000/credentials
2. Atualize o ChromeDriver:
   ```powershell
   pip install --upgrade selenium webdriver-manager
   ```
3. Verifique se o Chrome está atualizado

---

### 5. Atalho da área de trabalho não funciona

**Solução:**

**Opção 1:** Recriar o atalho
```powershell
cd $env:USERPROFILE\bci-on1
.\INICIAR_WEB.bat
```

**Opção 2:** Criar manualmente
1. Crie um arquivo `BCI-ON1-Web.bat` na área de trabalho
2. Cole este conteúdo:
```bat
@echo off
cd /d %USERPROFILE%\bci-on1
call venv\Scripts\activate.bat
cd web
python app.py
pause
```

---

## 🆘 Reinstalação Completa

Se nada funcionar, faça uma reinstalação limpa:

```powershell
# 1. Remover instalação antiga (feche todos os programas primeiro!)
Remove-Item -Recurse -Force "$env:USERPROFILE\bci-on1"

# 2. Baixar e executar instalador
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.bat -OutFile setup.bat
.\setup.bat
```

---

## 📧 Suporte

Se o problema persistir:
1. Anote a mensagem de erro completa
2. Tire screenshot se possível
3. Verifique se seguiu todos os passos acima
4. Entre em contato com o desenvolvedor

---

## 🔍 Logs e Diagnóstico

Para verificar logs detalhados:

1. **Logs do servidor web:**
   - Aparecem no terminal quando executa `BCI-ON1-Web.bat`
   
2. **Verificar instalação Python:**
   ```powershell
   python --version
   pip list
   ```

3. **Verificar ambiente virtual:**
   ```powershell
   cd $env:USERPROFILE\bci-on1
   .\venv\Scripts\activate
   python -c "import flask; print(flask.__version__)"
   ```

4. **Testar conexão com Servopa/Todoist:**
   - Abra manualmente os sites no Chrome
   - Verifique se consegue fazer login manualmente

---

**Última atualização:** Outubro 2025
