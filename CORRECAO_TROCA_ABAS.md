# 🔧 Correção: Automação Parando ao Trocar de Abas

## ❌ Problema Identificado

Quando o usuário trocava de aba do navegador durante a automação, o sistema **parava a execução automaticamente**.

### Causa Raiz

1. **Mudança de visibilidade da página**: Quando você troca de aba, o navegador dispara o evento `visibilitychange`
2. **Reconexão do WebSocket**: O navegador pode pausar/desconectar o WebSocket quando a aba fica invisível
3. **Verificação automática de status**: Ao reconectar (quando volta para a aba), o código fazia `fetch('/api/automation/status/...')` 
4. **Conflito de estado**: Essa verificação poderia desabilitar os botões ou interferir na execução

## ✅ Solução Implementada

### 1. Detecção de Troca de Abas

Adicionado listener para `visibilitychange`:

```javascript
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Usuário trocou de aba - marca para não verificar status ao voltar
        console.log('🔒 Aba ficou invisível - bloqueando verificações automáticas');
        window.tabSwitched = true;
    } else {
        // Usuário voltou para a aba
        console.log('👁️ Aba ficou visível - desbloqueando após 3s');
        // Aguarda 3 segundos antes de permitir verificações novamente
        setTimeout(() => {
            window.tabSwitched = false;
        }, 3000);
    }
});
```

### 2. Proteção na Reconexão

Modificado o `socket.on('connect')` para respeitar a flag `window.tabSwitched`:

```javascript
socket.on('connect', function() {
    addLog('Conectado ao servidor', 'success');
    
    // Verifica status atual da automação
    // MAS respeita se usuário está tentando parar OU se acabou de trocar de aba
    if (!window.isStopping && !window.tabSwitched) {
        fetch(`/api/automation/status/${dia}`)
            .then(res => res.json())
            .then(data => {
                if (data.running) {
                    updateAutomationStatus(true);
                } else {
                    updateAutomationStatus(false);
                }
            })
            .catch(err => console.error('Erro ao verificar status:', err));
    } else {
        console.log('⏸️ Verificação de status bloqueada (isStopping ou tabSwitched)');
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

- ✅ `web/templates/automation_dia8.html`
- ✅ `web/templates/automation_dia16.html`

## 🧪 Como Testar

1. Inicie a automação (Dia 8 ou Dia 16)
2. Troque para outra aba do navegador
3. Aguarde alguns segundos
4. Volte para a aba da automação
5. ✅ **Resultado esperado**: Automação continua rodando sem parar

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
