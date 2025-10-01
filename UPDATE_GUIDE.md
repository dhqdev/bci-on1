# 🔄 Guia de Atualização - Auto OXBCI

Sistema de Automação Servopa + Todoist

---

## ⚡ Atualização Rápida (RECOMENDADO)

### 🐧 Linux / 🍎 macOS

**Execute de QUALQUER LUGAR** (o script encontra o projeto automaticamente):

```bash
bash ~/auto-oxbci/update.sh
```

Ou se o projeto estiver em outro local:

```bash
bash "/caminho/completo/para/auto-oxbci/update.sh"
```

---

### 🪟 Windows

**Execute de QUALQUER LUGAR:**

```batch
%USERPROFILE%\auto-oxbci\update.bat
```

Ou clique duplo no arquivo `update.bat` dentro da pasta do projeto.

---

## 📋 O Que o Script de Atualização Faz Automaticamente

✅ **Detecta automaticamente o diretório do projeto** (funciona de qualquer lugar!)  
✅ Verifica conexão com internet  
✅ Faz backup automático de suas configurações (`credentials.json`, `.env`)  
✅ Salva mudanças locais (git stash) se necessário  
✅ Verifica se há atualizações disponíveis no GitHub  
✅ Mostra o que mudou (changelog)  
✅ Aplica as atualizações  
✅ Atualiza dependências Python automaticamente  
✅ Limpa arquivos temporários  
✅ Restaura suas configurações  
✅ Mostra resumo completo  
✅ Oferece executar o sistema imediatamente  

---

## 🎯 Você Já Está na Versão Mais Recente?

Se ao executar o `update.sh` você ver:

```
✓ Você já está na versão mais recente! 🎉
```

**Parabéns!** Seu sistema está atualizado e não precisa fazer nada. 🎉

---

## ❓ Onde Meu Projeto Está Instalado?

### Localização Padrão

**Linux/macOS:**
```
~/auto-oxbci
```
(Equivalente a: `/home/seu-usuario/auto-oxbci`)

**Windows:**
```
%USERPROFILE%\auto-oxbci
```
(Equivalente a: `C:\Users\SeuUsuario\auto-oxbci`)

### Como Encontrar

**Linux/macOS:**
```bash
# Método 1: Find
find ~ -name "auto-oxbci" -type d 2>/dev/null

# Método 2: Locate (se instalado)
locate auto-oxbci | grep -E "auto-oxbci$"
```

**Windows (PowerShell):**
```powershell
Get-ChildItem -Path C:\Users\$env:USERNAME -Filter "auto-oxbci" -Directory -Recurse -ErrorAction SilentlyContinue
```

---

## 🆘 Solução de Problemas

### ❌ Erro: "Não foi possível encontrar o diretório do projeto"

**Solução:** Entre no diretório manualmente e execute:

```bash
# Linux/macOS
cd ~/auto-oxbci  # ou onde você instalou
./update.sh

# Windows
cd %USERPROFILE%\auto-oxbci
update.bat
```

---

### ❌ Erro: "Sem conexão com internet"

**Solução:**

1. Verifique sua conexão com a internet
2. Tente novamente após alguns minutos
3. Verifique se `github.com` está acessível:
   ```bash
   ping github.com
   ```

---

### ❌ Erro: "Você tem mudanças não commitadas"

O script detectou que você modificou arquivos do projeto localmente.

**Opções:**

1. **Fazer stash (Recomendado)**: O script oferecerá salvar suas mudanças temporariamente
   - Escolha `S` quando perguntado
   - Suas mudanças ficarão salvas e podem ser restauradas depois com `git stash pop`

2. **Continuar mesmo assim**: Suas mudanças locais serão substituídas pelas do GitHub
   - ⚠️ **ATENÇÃO**: Você perderá suas modificações!

3. **Cancelar**: Faça backup manual das suas mudanças antes

---

### ❌ Erro: "Conflitos ao restaurar mudanças"

Se você fez stash e houve conflitos ao restaurar:

```bash
cd ~/auto-oxbci  # ou onde está o projeto

# Ver lista de stashes
git stash list

# Restaurar manualmente
git stash apply stash@{0}

# Se houver conflitos, resolva-os manualmente e depois:
git add .
git stash drop stash@{0}
```

---

### ❌ Erro na instalação de dependências Python

**Solução:**

```bash
cd ~/auto-oxbci
source venv/bin/activate  # Linux/macOS
# OU
venv\Scripts\activate.bat  # Windows

# Reinstalar dependências
pip install --upgrade -r requirements.txt

# Se falhar, instalar individualmente:
pip install --upgrade selenium webdriver-manager requests beautifulsoup4
```

---

## 🔍 Verificar Versão Atual

```bash
cd ~/auto-oxbci
git log -1 --oneline
```

Exemplo de saída:
```
abc1234 feat: adiciona nova funcionalidade X
```

---

## 📜 Ver Histórico de Mudanças

```bash
cd ~/auto-oxbci

# Últimas 10 mudanças
git log --oneline -10

# Mudanças completas
git log

# Ver changelog
cat docs/CHANGELOG.md
```

---

## 🚀 Executar Após Atualização

### Opção 1 - Automática

O script oferece executar automaticamente ao final. Basta responder `S` quando perguntado.

### Opção 2 - Manual

```bash
# Linux/macOS
cd ~/auto-oxbci
./run.sh

# Windows
cd %USERPROFILE%\auto-oxbci
run.bat
```

---

## 🎨 Funcionalidades Adicionais do update.sh

### Backup Automático

Toda vez que você atualiza, o script cria um backup com timestamp:

```
.backup_20251001_143022/
├── credentials.json
└── .env
```

**Ver backups disponíveis:**
```bash
ls -d .backup_* 2>/dev/null
```

**Restaurar um backup:**
```bash
cp .backup_20251001_143022/credentials.json credentials.json
```

---

### Limpeza Automática

O script mantém apenas os **últimos 5 backups** automaticamente, removendo os mais antigos.

---

## 💡 Dicas Úteis

### Criar Alias para Facilitar

**Linux/macOS:**

Adicione ao seu `~/.bashrc` ou `~/.zshrc`:

```bash
# Alias para executar
alias oxbci="bash ~/auto-oxbci/run.sh"

# Alias para atualizar
alias oxbci-update="bash ~/auto-oxbci/update.sh"
```

Depois execute:
```bash
source ~/.bashrc  # ou ~/.zshrc
```

Agora você pode executar de qualquer lugar:
```bash
oxbci          # Executa o sistema
oxbci-update   # Atualiza o sistema
```

---

**Windows (PowerShell):**

Adicione ao seu perfil do PowerShell (`$PROFILE`):

```powershell
function Start-OXBCI { & "$env:USERPROFILE\auto-oxbci\run.bat" }
function Update-OXBCI { & "$env:USERPROFILE\auto-oxbci\update.bat" }

Set-Alias oxbci Start-OXBCI
Set-Alias oxbci-update Update-OXBCI
```

---

## 📞 Suporte

- **GitHub Issues**: https://github.com/dhqdev/auto-oxbci/issues
- **Documentação**: Pasta `/docs` no projeto

---

## ✅ Checklist de Atualização

Antes de atualizar, certifique-se de:

- [ ] Ter conexão com internet estável
- [ ] Não estar executando o sistema no momento
- [ ] Ter feito backup de arquivos importantes (se modificou algo)
- [ ] Ter pelo menos 500MB de espaço livre no disco

Após atualizar, verifique se:

- [ ] O sistema inicia normalmente
- [ ] Suas credenciais ainda estão salvas
- [ ] Todas as funcionalidades funcionam

---

**Versão do Guia**: 1.0  
**Última Atualização**: Outubro 2025

---

<div align="center">

**⭐ Mantenha seu sistema sempre atualizado para ter acesso às últimas funcionalidades e correções! ⭐**

[🏠 README Principal](README.md) | [📥 Instalação](INSTALL.md) | [⚡ Quick Start](docs/QUICKSTART.md)

</div>
