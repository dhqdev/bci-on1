# 🚀 Instalação Rápida - Auto OXBCI

Sistema de Automação Servopa + Todoist - Instalação em Um Comando

---

## 📥 Instalação Automática Completa

### 🐧 Linux / 🍎 macOS

**Opção 1: Download e Execução (Recomendado)**
```bash
wget https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh && bash setup-linux.sh
```

**Opção 2: Com curl**
```bash
curl -fsSL https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh | bash
```

**Opção 3: Manual**
```bash
# 1. Baixar o instalador
wget https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-linux.sh

# 2. Dar permissão de execução
chmod +x setup-linux.sh

# 3. Executar
./setup-linux.sh
```

---

### 🪟 Windows

**Opção 1: PowerShell (Executar como Administrador)**
```powershell
irm https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat | iex
```

**Opção 2: Download Manual**

1. Baixe o arquivo: [setup-windows.bat](https://raw.githubusercontent.com/dhqdev/auto-oxbci/main/setup-windows.bat)
2. Clique com botão direito no arquivo
3. Selecione **"Executar como administrador"**

---

## ✨ O que o instalador faz?

O instalador automático:

1. ✅ **Detecta seu sistema operacional**
2. ✅ **Instala Python 3.11** (se necessário)
3. ✅ **Instala Git** (se necessário - apenas Windows)
4. ✅ **Instala Google Chrome** (se necessário)
5. ✅ **Clona o repositório do GitHub**
6. ✅ **Cria ambiente virtual Python**
7. ✅ **Instala todas as dependências**
8. ✅ **Ativa o ambiente virtual automaticamente**
9. ✅ **Cria atalhos de execução**
10. ✅ **Verifica se tudo está funcionando**

---

## 🎯 Após a Instalação

### Linux / macOS

```bash
# O projeto será instalado em:
~/auto-oxbci

# Para executar (pode executar de qualquer lugar!):
# Opção 1: Execute diretamente de qualquer lugar
bash ~/auto-oxbci/run.sh

# Opção 2: Entre no diretório e execute
cd ~/auto-oxbci
./run.sh
```

### Windows

```batch
REM O projeto será instalado em:
%USERPROFILE%\auto-oxbci

REM Para executar:
REM Opção 1: Clique no atalho "Auto OXBCI" na área de trabalho
REM Opção 2: Execute diretamente de qualquer lugar
%USERPROFILE%\auto-oxbci\run.bat

REM Opção 3: Entre no diretório e execute
cd %USERPROFILE%\auto-oxbci
run.bat
```

---

## 📋 Pré-requisitos

### Absolutamente NENHUM! 🎉

O instalador automático cuida de tudo para você:

- ✅ Python será instalado automaticamente
- ✅ Git será instalado automaticamente (Windows)
- ✅ Chrome será instalado automaticamente
- ✅ Todas as dependências serão instaladas
- ✅ Ambiente virtual será configurado
- ✅ Tudo pronto para uso!

---

## 🔧 Instalação Manual (Se Preferir)

Se você já tem o repositório clonado ou prefere instalar manualmente:

### Linux / macOS

```bash
# 1. Clonar repositório (se ainda não tiver)
git clone https://github.com/dhqdev/auto-oxbci.git
cd auto-oxbci

# 2. Executar instalador
bash install.sh

# 3. Executar sistema (o ambiente virtual já está ativado!)
python main_gui.py
```

### Windows

```batch
REM 1. Clonar repositório (se ainda não tiver)
git clone https://github.com/dhqdev/auto-oxbci.git
cd auto-oxbci

REM 2. Executar instalador
install.bat

REM 3. Executar sistema (o ambiente virtual já está ativado!)
python main_gui.py
```

---

## 🆘 Solução de Problemas

### Erro: "Python não encontrado"

**Linux/macOS:**
```bash
sudo apt install python3 python3-pip python3-venv  # Ubuntu/Debian
sudo dnf install python3 python3-pip               # Fedora
brew install python@3.11                           # macOS
```

**Windows:**
Baixe de: https://www.python.org/downloads/

### Erro: "Git não encontrado" (Windows)

Baixe de: https://git-scm.com/download/win

### Erro: "Permissão negada" (Linux/macOS)

```bash
chmod +x setup-linux.sh
chmod +x install.sh
chmod +x run.sh
```

### Erro: "Ambiente virtual não ativado"

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```batch
venv\Scripts\activate.bat
```

---

## 🎓 Comandos Úteis

### Ativar Ambiente Virtual Manualmente

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```batch
venv\Scripts\activate.bat
```

### Desativar Ambiente Virtual

```bash
deactivate  # Funciona em todos os sistemas
```

### Atualizar Dependências

```bash
# Com ambiente virtual ativado:
pip install --upgrade -r requirements.txt
```

### Atualizar Projeto

```bash
cd ~/auto-oxbci         # ou %USERPROFILE%\auto-oxbci no Windows
git pull origin main
```

---

## 📞 Suporte

- 📧 **Issues**: https://github.com/dhqdev/auto-oxbci/issues
- 📖 **Documentação**: Veja os arquivos README.md e QUICKSTART.md
- 🔍 **Logs**: Verifique os logs de erro no terminal

---

## 🎉 Pronto!

Agora você tem o sistema completamente instalado e pronto para uso!

Execute e comece a automatizar! 🚀

---

**Versão**: 2.0  
**Última Atualização**: Outubro 2025
