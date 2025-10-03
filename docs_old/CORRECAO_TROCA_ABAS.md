# 🔧 Correção: Automação Parando ao Trocar de Abas

## ❌ Problema Identificado

### Sintoma 1: Nas páginas de automação (Dia 8/16)
Quando o usuário trocava de aba do navegador durante a automação, o sistema **parava a execução automaticamente**.

**Causa**: O navegador desconectava o WebSocket ao trocar de aba, e ao reconectar (quando você voltava), ele verificava o status da automação, causando interferência.

### Sintoma 2: No Dashboard (Visualizador)
Quando o usuário trocava de aba, o **visualizador de screenshots parava de atualizar**, mesmo com a automação rodando no backend.

**Causa**: O navegador **pausa** `setInterval` quando a aba fica invisível. Ao voltar, o timer retoma, mas pode ter perdido várias atualizações, causando a impressão de que "parou".

## ✅ Solução Implementada

### 1. Proteção nas Páginas de Automação (Dia 8/16)

Adicionado listener para `visibilitychange` que bloqueia verificações de status ao trocar de aba:

```javascript
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Usuário trocou de aba - marca para não verificar status ao voltar
        console.log('🔒 Aba ficou invisível - bloqueando verificações automáticas');
        window.tabSwitched = true;
    } else {
        // Usuário voltou para a aba
        console.log('👁️ Aba ficou visível - desbloqueando após 3s');
        setTimeout(() => {
            window.tabSwitched = false;
        }, 3000);
    }
});
```

Modificado o `socket.on('connect')` para respeitar a flag:

```javascript
socket.on('connect', function() {
    if (!window.isStopping && !window.tabSwitched) {
        fetch(`/api/automation/status/${dia}`)...
    } else {
        console.log('⏸️ Verificação bloqueada');
    }
});
```

### 2. Proteção no Dashboard (Visualizador)

**Atualização forçada ao voltar para a aba:**

```javascript
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && currentViewerDia) {
        // Aba voltou a ficar visível e tem automação ativa
        console.log('👁️ Aba visível - forçando atualização de screenshot');
        updateViewerScreenshot(); // Atualiza IMEDIATAMENTE
    }
});
```

**Reconexão WebSocket atualiza automaticamente:**

```javascript
socket.on('connect', function() {
    // Se tinha automação ativa, força atualização
    if (currentViewerDia) {
        console.log('🔄 Reconectado - atualizando screenshot');
        updateViewerScreenshot();
    }
});
```

**Logs em tempo real via WebSocket:**

```javascript
socket.on('log', function(data) {
    // Adiciona logs do backend no visualizador
    if (currentViewerDia && (data.dia === currentViewerDia || data.dia === 'general')) {
        const type = getLogType(data.message);
        addViewerLog(data.message, type);
    }
});

socket.on('progress', function(data) {
    // Atualiza barra de progresso em tempo real
    if (currentViewerDia && data.dia === currentViewerDia) {
        updateViewerProgress(data.value, data.message);
    }
});
```

## 🎯 Como Funciona Agora

### Cenário 1: Usuário Troca de Aba Durante Automação

1. ✅ Automação está rodando
2. 🔄 Usuário clica em outra aba
3. 🔒 Sistema detecta `document.hidden = true`
4. 🚫 Define `window.tabSwitched = true` (bloqueia verificações)
5. ⏸️ WebSocket pode desconectar (normal do navegador)
6. 🔄 Usuário volta para a aba
7. 🔌 WebSocket reconecta
8. 🚫 Verificação de status é **bloqueada** por 3 segundos
9. ✅ Automação continua rodando normalmente!

### Cenário 2: Usuário Para Manualmente

1. ✅ Automação está rodando
2. 🛑 Usuário clica em "Parar"
3. 🔒 Sistema define `window.isStopping = true`
4. 📡 Envia POST para `/api/automation/stop/dia8`
5. ✅ Servidor para a automação
6. 🔓 Após 2 segundos, libera `window.isStopping = false`
7. 🎯 Status atualizado corretamente

## 📁 Arquivos Modificados

### Páginas de Automação:
- ✅ `web/templates/automation_dia8.html` - Proteção contra verificação de status
- ✅ `web/templates/automation_dia16.html` - Proteção contra verificação de status

### Dashboard:
- ✅ `web/templates/index.html` - Atualização forçada + WebSocket logs em tempo real

## 🧪 Como Testar

### Teste 1: Páginas de Automação (Dia 8/16)

1. Acesse http://localhost:5000/automation/dia8
2. Clique em **"Iniciar Automação"**
3. **Troque para outra aba** do navegador
4. Aguarde 5-10 segundos
5. **Volte para a aba da automação**
6. ✅ **Resultado esperado**: Automação continua rodando, logs aparecem

### Teste 2: Dashboard (Visualizador)

1. Acesse http://localhost:5000 (Dashboard)
2. Clique em **"Iniciar"** em Automação Dia 8
3. Observe o visualizador atualizando screenshots
4. **Troque para outra aba** do navegador
5. Aguarde 5-10 segundos
6. **Volte para o Dashboard**
7. ✅ **Resultado esperado**: 
   - Screenshot atualiza **IMEDIATAMENTE** ao voltar
   - Logs aparecem em tempo real
   - Progresso continua atualizando

## 🔍 Logs no Console

Ao trocar de aba, você verá no console do navegador (F12):

```
🔒 Aba ficou invisível - bloqueando verificações automáticas
❌ Desconectado do servidor
✅ Conectado ao servidor
⏸️ Verificação de status bloqueada (isStopping ou tabSwitched)
👁️ Aba ficou visível - desbloqueando após 3s
```

## ⚙️ Flags de Controle

| Flag | Propósito | Quando ativa |
|------|-----------|--------------|
| `window.isStopping` | Previne interferência durante parada manual | Usuário clica "Parar" |
| `window.tabSwitched` | Previne verificações após troca de aba | Usuário muda de aba (3s) |

## ⏱️ Timeouts

- **Verificação após troca de aba**: 3 segundos
- **Confirmação de parada**: 2 segundos

Esses tempos garantem que o sistema estabilize antes de permitir novas verificações.

## 📌 Observações

- ✅ A automação **continua executando no backend** mesmo quando a aba está invisível
- ✅ O Chrome headless **não é afetado** pela visibilidade da página
- ✅ Apenas a **interface** é protegida contra verificações indevidas
- ✅ O WebSocket **reconecta automaticamente** quando você volta para a aba

## 🎉 Resultado

**AGORA VOCÊ PODE TROCAR DE ABA LIVREMENTE SEM MEDO DA AUTOMAÇÃO PARAR!** 🚀
