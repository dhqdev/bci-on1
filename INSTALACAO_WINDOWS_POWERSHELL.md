# 🪟 Instalação no Windows - Guia Completo

## ❌ Problema Comum: "Execução de Scripts Desabilitada"

Quando você tenta executar:
```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.ps1 -OutFile setup.ps1; .\setup.ps1
```

E recebe o erro:
```
O arquivo setup.ps1 não pode ser carregado porque a execução de scripts foi
desabilitada neste sistema.
```

**Causa**: Por padrão, o Windows bloqueia execução de scripts PowerShell por segurança.

---

## ✅ SOLUÇÃO 1: Instalador Rápido (RECOMENDADO)

### Passo 1: Abrir PowerShell como Administrador

1. Pressione `Win + X` ou clique com botão direito no menu Iniciar
2. Escolha: **"Windows PowerShell (Administrador)"** ou **"Terminal (Administrador)"**
3. Clique em **"Sim"** quando pedir permissão

### Passo 2: Executar Instalador Rápido

Cole este comando e pressione Enter:

```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex
```

**O que esse comando faz:**
- `irm` = baixa o script da internet
- `| iex` = executa diretamente (sem salvar arquivo, não precisa de ExecutionPolicy)

### Passo 3: Aguardar Instalação

O instalador vai:
1. ✅ Verificar Git e Python
2. 📥 Clonar repositório
3. 🔧 Criar ambiente virtual
4. 📦 Instalar dependências
5. 🎨 Criar atalho no Desktop

---

## ✅ SOLUÇÃO 2: Liberar Execução de Scripts (Manual)

### Opção A: Liberação Temporária (Mais Seguro)

1. Abra PowerShell como **Administrador**
2. Execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

3. Agora execute o instalador:

```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.ps1 -OutFile setup.ps1
.\setup.ps1
```

**Vantagem**: A liberação vale só para esta janela do PowerShell.

### Opção B: Liberação Permanente (Cuidado!)

⚠️ **AVISO**: Isso libera execução de scripts no sistema todo!

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

Depois execute o instalador normalmente.

---

## ✅ SOLUÇÃO 3: Instalação Manual (Sem PowerShell)

### Passo 1: Instalar Pré-requisitos

1. **Git**: https://git-scm.com/download/win
2. **Python 3.11+**: https://www.python.org/downloads/
   - ⚠️ Marque: **"Add Python to PATH"**

### Passo 2: Clonar Repositório

Abra **Prompt de Comando** (não precisa ser Admin):

```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/dhqdev/bci-on1.git
cd bci-on1
```

### Passo 3: Executar Instalador .BAT

```cmd
install.bat
```

**Vantagem**: Arquivos `.bat` não precisam de ExecutionPolicy!

---

## 🎯 Depois da Instalação

### Iniciar o Sistema

**Opção 1**: Clique no atalho no Desktop
- 🖼️ **"BCI-ON1 Web"** (ícone OXCASH)

**Opção 2**: Execute manualmente
```cmd
cd %USERPROFILE%\Desktop\bci-on1
run.bat
```

**Opção 3**: Via PowerShell (se configurou ExecutionPolicy)
```powershell
cd $env:USERPROFILE\Desktop\bci-on1
.\run.bat
```

### Acessar Interface

Abra o navegador em: **http://localhost:5000**

---

## 🔍 Verificar Políticas Atuais

Para ver a política de execução atual:

```powershell
Get-ExecutionPolicy -List
```

Resultado esperado:
```
        Scope ExecutionPolicy
        ----- ---------------
MachinePolicy       Undefined
   UserPolicy       Undefined
      Process       Undefined
  CurrentUser    RemoteSigned  <- Ideal
 LocalMachine       Undefined
```

---

## 🛡️ Segurança: O Que Significam as Políticas

| Política | Descrição | Segurança |
|----------|-----------|-----------|
| **Restricted** | Nenhum script pode executar | 🔒 Máxima |
| **AllSigned** | Só scripts assinados digitalmente | 🔒 Alta |
| **RemoteSigned** | Scripts locais OK, da internet precisam assinatura | ⚠️ Média |
| **Unrestricted** | Qualquer script pode executar (com aviso) | ⚠️ Baixa |
| **Bypass** | Sem bloqueios nem avisos | ❌ Nenhuma |

**Recomendação**: Use `RemoteSigned` para `CurrentUser` (bom equilíbrio).

---

## ❓ Perguntas Frequentes

### P: Por que usar `| iex` em vez de salvar o arquivo?

**R**: `iex` (Invoke-Expression) executa o script na memória sem precisar salvar arquivo. Scripts que não são salvos em disco não são bloqueados pela ExecutionPolicy!

### P: É seguro usar `| iex`?

**R**: Sim, SE você confia na fonte! Nosso repositório é público (https://github.com/dhqdev/bci-on1) e você pode ver o código antes de executar.

### P: Posso usar sem ser Administrador?

**R**: Para instalação inicial, precisa de Admin (para criar venv, instalar pacotes). Depois disso, pode rodar normalmente.

### P: E se não quiser mexer no PowerShell?

**R**: Use a **SOLUÇÃO 3** (instalação manual com `.bat`). Funciona sem problemas de ExecutionPolicy!

---

## 📚 Links Úteis

- **Repositório GitHub**: https://github.com/dhqdev/bci-on1
- **Documentação Oficial Microsoft**: https://go.microsoft.com/fwlink/?LinkID=135170
- **Python para Windows**: https://www.python.org/downloads/
- **Git para Windows**: https://git-scm.com/download/win

---

## 🆘 Problemas Comuns

### "Git não encontrado"
```powershell
# Instale o Git e reinicie o PowerShell
# Download: https://git-scm.com/download/win
```

### "Python não encontrado"
```powershell
# Instale Python e marque "Add to PATH"
# Download: https://www.python.org/downloads/
```

### "Acesso negado" ao criar venv
```powershell
# Execute PowerShell como Administrador
```

### "Módulo não encontrado" ao rodar
```cmd
# Reinstale dependências
cd %USERPROFILE%\Desktop\bci-on1
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🎉 Pronto!

Agora seu amigo pode instalar o sistema sem problemas de ExecutionPolicy! 🚀

**Método Mais Simples**: Copie e cole isto (PowerShell como Admin):

```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex
```

Feito! ✨
