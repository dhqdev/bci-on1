# 🧪 Como Testar a Nova Interface Simplificada

## ⚡ Teste Rápido (5 minutos)

### 1️⃣ Abrir a Aplicação
```bash
cd "/home/david/Área de trabalho/localbci1/auto-oxbci"
python main_gui.py
```

### 2️⃣ Procurar as Novas Abas
Agora você verá **DUAS** novas abas:
- 📱 **Dia 8**
- 📱 **Dia 16**

*(A aba antiga "📱 Envio de Mensagem" foi removida)*

---

## 📱 Teste da Aba "Dia 8"

### Passo 1: Configurar API (PRIMEIRA VEZ APENAS)

1. Clique na aba **"📱 Dia 8"**

2. Verifique se os campos estão preenchidos:
   ```
   URL da API: https://zap.tekvosoft.com
   Nome da Instância: david-tekvo
   API Key: 634A7E882CE5-4314-8C5B-BC79C0A9EBBA
   ```

3. Clique em **"🧪 Testar Conexão"**

4. Aguarde o resultado:
   - ✅ **"Conexão OK"** → Tudo certo!
   - ❌ **"Falhou"** → Verifique os dados no log

### Passo 2: Adicionar Contatos

No campo **"👥 Contatos"**, adicione um contato de teste:
```
5519995378302 - João Teste
```

*(Você pode adicionar vários, um por linha)*

### Passo 3: Escrever Mensagem

No campo **"💬 Mensagem do Dia 8"**, escreva:
```
Olá {nome}! 🎉

Esta é uma mensagem de teste do Dia 8.

Obrigado!
```

*(O `{nome}` será substituído automaticamente por "João Teste")*

### Passo 4: Enviar

1. Clique em **"📤 Enviar Mensagens Dia 8"**

2. Acompanhe no **"📝 Log de Envio"** (parte inferior):
   ```
   [14:32:15] 📤 Iniciando envio DIA8 para 1 contato(s)...
   [14:32:15] DEBUG: URL = https://zap.tekvosoft.com/message/sendText/david-tekvo
   [14:32:15] DEBUG: Payload = {"number": "5519995378302@c.us", "text": "..."}
   [14:32:16] ✅ Enviado para João Teste (5519995378302@c.us)
   [14:32:16] ✅ 1 enviadas
   ```

### Passo 5: Verificar Resultado

No topo da seção **"📤 Envio de Mensagens"**, você verá:
- ✅ **"✅ 1 enviadas"** → Sucesso!
- ⚠️ **"⚠️ 0/1"** → Algo falhou (veja o log)
- ❌ **"❌ Erro"** → Erro crítico (veja o log)

---

## 📱 Teste da Aba "Dia 16"

### Passo 1: Ir para Aba Dia 16

1. Clique na aba **"📱 Dia 16"**

2. Note que há uma mensagem:
   ```
   ℹ️ Configuração da API está na aba 'Dia 8'
   ```
   *(Não precisa configurar novamente!)*

### Passo 2: Adicionar Contatos Diferentes

No campo **"👥 Contatos"**, adicione:
```
5519988776655 - Maria Teste
```

### Passo 3: Escrever Mensagem Diferente

No campo **"💬 Mensagem do Dia 16"**, escreva:
```
Oi {nome}! 👋

Esta é a mensagem do Dia 16.

Até logo!
```

### Passo 4: Enviar

1. Clique em **"📤 Enviar Mensagens Dia 16"**

2. Verifique o log (mesma área, compartilhada):
   ```
   [14:35:20] 📤 Iniciando envio DIA16 para 1 contato(s)...
   [14:35:21] ✅ Enviado para Maria Teste (5519988776655@c.us)
   ```

---

## 🔍 O Que Observar no Log

### ✅ Envio Com Sucesso
```
[14:32:16] ✅ Enviado para João Silva (5519995378302@c.us)
```
- Mensagem foi enviada
- Formato do telefone: `5519995378302@c.us` (correto!)

### ❌ Erro 404 (Ainda Ocorrendo)
```
[14:32:16] DEBUG: URL = https://zap.tekvosoft.com/message/sendText/david-tekvo
[14:32:16] DEBUG: Status Code: 404
[14:32:16] DEBUG: Response: {"error": "Instance not found"}
[14:32:16] ❌ Falha para João Silva: Status 404
```

**Se você ver isso, copie e cole TODO o log aqui!**

Precisamos verificar:
1. O nome da instância está correto? (`david-tekvo`)
2. A instância está ativa no painel da Evolution API?
3. O endpoint está correto? (`/message/sendText/`)

---

## 🧹 Botão "🗑️ Limpar"

Em qualquer aba, clique em **"🗑️ Limpar"** para:
- Apagar todos os contatos
- Apagar a mensagem
- Recomeçar do zero

---

## 📊 Diferenças da Interface Antiga

### ❌ O Que FOI REMOVIDO
- Seleção de "Grupo 1" ou "Grupo 2"
- Seleção de "Dia 7" ou "Dia 15"
- Botão "Enviar para Grupo Selecionado"
- Layout de duas colunas (contatos | mensagem)

### ✅ O Que FOI ADICIONADO
- Aba separada para Dia 8
- Aba separada para Dia 16
- Layout vertical (melhor visibilidade)
- Configuração compartilhada
- Log compartilhado

---

## 🐛 Problemas Conhecidos

### 1. Erro 404 ao Enviar

**Sintoma:**
```
❌ Falha para João Silva: Status 404
```

**O que fazer:**
1. Copie TODO o log (desde o DEBUG: URL até o final)
2. Cole aqui no chat
3. Vamos verificar se o URL está correto

### 2. Teste de Conexão Passa, Mas Envio Falha

**Sintoma:**
```
✅ Conexão OK
...
❌ Falha para João Silva: Status 404
```

**Possível causa:**
- O teste de conexão pode estar verificando apenas se o servidor responde
- O envio real pode estar usando um endpoint diferente

**O que fazer:**
- Envie o log completo
- Vamos comparar o URL do teste com o URL do envio

---

## 📋 Checklist de Teste Completo

### Aba Dia 8
- [ ] Configuração da API está preenchida
- [ ] Botão "Testar Conexão" retorna ✅
- [ ] Adicionei contatos no formato correto
- [ ] Escrevi mensagem com `{nome}`
- [ ] Cliquei em "Enviar Mensagens Dia 8"
- [ ] Vi logs no painel inferior
- [ ] Status mostra resultado (✅ ou ❌)

### Aba Dia 16
- [ ] Vi a mensagem "Configuração da API está na aba 'Dia 8'"
- [ ] Adicionei contatos diferentes
- [ ] Escrevi mensagem diferente
- [ ] Cliquei em "Enviar Mensagens Dia 16"
- [ ] Vi logs no painel (compartilhado com Dia 8)
- [ ] Status mostra resultado

### Funcionalidades Gerais
- [ ] Botão "Limpar" funciona em ambas as abas
- [ ] Log mostra mensagens de ambas as abas
- [ ] Configuração persiste entre abas
- [ ] Posso alternar entre abas sem perder dados

---

## 📸 O Que Enviar Se Houver Problemas

### Informações Necessárias:

1. **Log Completo** (copie do painel inferior)
   ```
   [HH:MM:SS] ...todas as mensagens...
   ```

2. **Screenshot** da aba com erro (se possível)

3. **Confirme os dados da API:**
   - URL: `https://zap.tekvosoft.com`
   - Instância: `david-tekvo`
   - API Key: `634A7E88...` (primeiros caracteres)

4. **O que aconteceu:**
   - "Teste de conexão passou?"
   - "Conseguiu enviar mensagem?"
   - "Qual foi o erro exato?"

---

## ✅ Resultado Esperado

### Se Tudo Funcionar:

**Aba Dia 8:**
```
Status: ✅ 1 enviadas

Log:
[14:32:15] 📤 Iniciando envio DIA8 para 1 contato(s)...
[14:32:16] ✅ Enviado para João Teste (5519995378302@c.us)
```

**Aba Dia 16:**
```
Status: ✅ 1 enviadas

Log:
[14:35:20] 📤 Iniciando envio DIA16 para 1 contato(s)...
[14:35:21] ✅ Enviado para Maria Teste (5519988776655@c.us)
```

### Se Ainda Houver Erro 404:

Vamos precisar:
1. Verificar instância no painel da Evolution API
2. Confirmar endpoint exato
3. Testar com curl/postman primeiro
4. Ajustar código se necessário

---

## 🎉 Próximos Passos Após Teste

Se funcionar:
- ✅ Interface simplificada funcionando!
- ✅ Pode começar a usar no dia-a-dia
- ✅ Salvar contatos reais
- ✅ Configurar mensagens finais

Se não funcionar:
- 📋 Enviar logs completos
- 🔍 Investigar erro 404 juntos
- 🛠️ Ajustar configuração se necessário

---

**Dúvidas? Cole os logs aqui que ajudo a resolver! 🚀**
