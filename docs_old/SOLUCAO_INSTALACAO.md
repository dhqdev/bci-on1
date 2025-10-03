# 🆘 Soluções para Problemas de Instalação

## ❌ Problemas Comuns e Soluções

### 1. "Espaço insuficiente no disco" ao instalar Git

**Causa**: Disco C:\ está cheio

**Solução**:
1. Libere espaço no disco C:\ (pelo menos 500 MB)
2. Ou instale Git manualmente em outro disco:
   - Baixe: https://git-scm.com/download/win
   - Durante instalação, escolha outro disco (D:\, E:\, etc)

---

### 2. "Python não foi encontrado" ou "Python nÒo foi encontrado"

**Causa**: Python não está instalado ou não está no PATH

**Solução Rápida**:
```powershell
# Baixe Python e instale manualmente
# https://www.python.org/downloads/

# IMPORTANTE: Durante instalação, marque:
# ✅ "Add Python to PATH"
```

**Solução Alternativa**:
1. Baixe: https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe
2. Execute o instalador
3. **MARQUE** "Add Python to PATH" na primeira tela
4. Clique "Install Now"
5. Reinicie o computador
6. Execute o instalador novamente

---

### 3. "Git não é reconhecido como nome de cmdlet"

**Causa**: Git não foi instalado ou não está no PATH

**Solução FÁCIL - Download Manual**:
1. Baixe o projeto: https://github.com/dhqdev/bci-on1/archive/refs/heads/main.zip
2. Clique com botão direito → "Extrair tudo"
3. Extraia para `C:\Users\SEU_USUARIO\Desktop\bci-on1`
4. Entre na pasta
5. Clique duas vezes em `install.bat`

**Solução Alternativa**:
1. Baixe Git: https://git-scm.com/download/win
2. Instale normalmente (Next, Next, Finish)
3. **Reinicie o PowerShell**
4. Execute o instalador novamente

---

### 4. Instalação Travou ou Não Responde

**Solução**:
1. Pressione `Ctrl + C` para cancelar
2. Feche o PowerShell
3. Tente a **INSTALAÇÃO MANUAL** (veja abaixo)

---

## 🛠️ INSTALAÇÃO MANUAL COMPLETA (Passo a Passo)

Se o instalador automático falhou, siga estes passos:

### Passo 1: Instalar Pré-requisitos

#### 1.1 Git
```
1. Acesse: https://git-scm.com/download/win
2. Baixe "64-bit Git for Windows Setup"
3. Execute o instalador
4. Clique "Next" até o final
5. Reinicie o computador
```

#### 1.2 Python
```
1. Acesse: https://www.python.org/downloads/
2. Baixe "Python 3.11.x" (versão estável)
3. Execute o instalador
4. ⚠️ IMPORTANTE: MARQUE "Add Python to PATH"
5. Clique "Install Now"
6. Reinicie o computador
```

#### 1.3 Google Chrome (Opcional, mas recomendado)
```
1. Acesse: https://www.google.com/chrome/
2. Baixe e instale normalmente
```

### Passo 2: Baixar o Projeto

**Opção A - Com Git (Recomendado)**:
```powershell
# Abra PowerShell (não precisa ser Admin)
cd Desktop
git clone https://github.com/dhqdev/bci-on1.git
cd bci-on1
```

**Opção B - Download ZIP (Mais Fácil)**:
```
1. Acesse: https://github.com/dhqdev/bci-on1
2. Clique em "Code" (botão verde)
3. Clique em "Download ZIP"
4. Extraia para Desktop\bci-on1
```

### Passo 3: Instalar Dependências

```powershell
# Abra PowerShell como ADMINISTRADOR
cd Desktop\bci-on1
.\install.bat
```

Aguarde 5-10 minutos. Será criado:
- ✅ Ambiente virtual Python (venv)
- ✅ Instalação de pacotes (Flask, Selenium, etc)
- ✅ Atalho no Desktop

### Passo 4: Executar o Sistema

**Opção 1**: Clique no atalho do Desktop "BCI-ON1 Web"

**Opção 2**: Via PowerShell:
```powershell
cd Desktop\bci-on1
.\run.bat
```

Acesse: http://localhost:5000

---

## 🔍 Verificar se Programas Estão Instalados

Abra PowerShell e execute:

```powershell
# Verificar Git
git --version
# Deve mostrar: git version 2.x.x

# Verificar Python
python --version
# Deve mostrar: Python 3.11.x

# Verificar Chrome
Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe"
# Deve mostrar: True
```

---

## 💡 Dicas Importantes

### Python não funciona após instalação?
1. Reinicie o computador (sério!)
2. Abra um NOVO PowerShell
3. Tente novamente

### Git não funciona após instalação?
1. Feche TODAS as janelas do PowerShell
2. Abra uma NOVA janela
3. Tente novamente

### Ainda não funciona?
1. Verifique se instalou como Administrador
2. Verifique se marcou "Add to PATH" no Python
3. Reinicie o computador
4. Tente a instalação manual (Opção B - Download ZIP)

---

## 📞 Precisa de Mais Ajuda?

### Problema com espaço em disco:
- Limpe arquivos temporários: `Win + R` → `temp` → Delete tudo
- Use Limpeza de Disco: `Win + R` → `cleanmgr`
- Desinstale programas não usados

### Erro de permissão:
- Execute PowerShell como Administrador:
  - Clique direito no menu Iniciar
  - "Windows PowerShell (Administrador)"

### Internet lenta/instável:
- Use a Opção B (Download ZIP)
- Não precisa de Git
- Download é mais rápido (20 MB)

---

## ✅ Checklist Final

Antes de pedir ajuda, verifique:

- [ ] Executou como Administrador?
- [ ] Python está instalado? (`python --version`)
- [ ] Python está no PATH? (marcou durante instalação)
- [ ] Git está instalado? (`git --version`)
- [ ] Reiniciou o computador após instalar Python/Git?
- [ ] Tem espaço em disco? (mínimo 2 GB livres)
- [ ] Tem conexão com internet?

Se todos estão OK e ainda falha, use a **INSTALAÇÃO MANUAL** acima!

---

## 🎯 Atalho Rápido (Sem Instalador)

Se quiser pular tudo e só rodar:

```powershell
# 1. Instale Python: https://www.python.org/downloads/ (MARQUE "Add to PATH")
# 2. Reinicie o computador
# 3. Execute:

cd Desktop
Invoke-WebRequest -Uri "https://github.com/dhqdev/bci-on1/archive/refs/heads/main.zip" -OutFile "bci-on1.zip"
Expand-Archive -Path "bci-on1.zip" -DestinationPath "."
Rename-Item "bci-on1-main" "bci-on1"
cd bci-on1
.\install.bat
.\run.bat
```

Acesse: http://localhost:5000

---

## 🚀 Resumo para Preguiçosos

**DOWNLOAD MANUAL É MAIS FÁCIL!**

1. Python: https://www.python.org/downloads/ (Marque "Add to PATH")
2. Projeto: https://github.com/dhqdev/bci-on1/archive/refs/heads/main.zip
3. Extraia ZIP
4. Clique em `install.bat`
5. Clique em `run.bat`
6. Acesse: http://localhost:5000

**PRONTO!** 🎉
