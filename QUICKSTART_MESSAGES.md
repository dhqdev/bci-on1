# 🎉 NOVA FUNCIONALIDADE: Envio de Mensagens WhatsApp

## ✨ O que foi implementado?

Foi adicionada uma **nova aba "📱 Envio de Mensagem"** no sistema que permite:

✅ **Enviar mensagens WhatsApp** via Evolution API  
✅ **Envio manual** para qualquer lista de contatos  
✅ **Envio automático** para grupos configurados  
✅ **Agendamento** para dias 7 e 15 do mês  
✅ **Personalização** de mensagens com nome do cliente  
✅ **Gerenciamento** de múltiplos grupos de clientes  

---

## 🚀 Como Instalar/Atualizar

### Se é primeira instalação:
```bash
bash install.sh
```

### Se já tem o sistema instalado:
```bash
bash update.sh
```

O script irá:
- Instalar a nova dependência (`schedule`)
- Criar o arquivo `evolution_config.json` automaticamente
- Configurar tudo para você

---

## 📱 Como Usar

### 1. Abrir o Sistema
```bash
bash run.sh
```

### 2. Acessar a Nova Aba

Na interface, clique na aba **"📱 Envio de Mensagem"**

### 3. Configurar Evolution API

**🔧 Na seção "Configuração da Evolution API":**

1. **URL da API:** `https://zap.tekvosoft.com`
2. **Nome da Instância:** `david-tekvo` (ou o nome da sua instância)
3. **API Key:** `634A7E882CE5-4314-8C5B-BC79C0A9EBBA` (ou sua chave)

4. Clique em **🧪 Testar Conexão** para validar

---

## 📤 Modo de Uso 1: Envio Manual

**Para enviar mensagens para qualquer lista de contatos:**

1. **Adicionar Contatos** (campo da esquerda):
   ```
   5519995378302 - João Silva
   5519988776655 - Maria Santos
   19977665544 - Ana Costa
   ```
   - Um contato por linha
   - Formato: `TELEFONE - NOME`

2. **Escrever Mensagem** (campo da direita):
   ```
   Olá {nome}! 🎉
   
   Lembrando que hoje é o último dia para enviar seus lances!
   
   Não perca essa oportunidade! ⏰
   ```
   - Use `{nome}` para personalizar com o nome do contato

3. Clique em **📤 Enviar Mensagens**

4. Acompanhe o progresso no **Log de Envio**

---

## 📊 Modo de Uso 2: Envio por Grupo

**Para enviar para grupos pré-configurados:**

1. Selecione o **Grupo** (Grupo 1 ou Grupo 2)
2. Selecione o **Dia** (Dia 7 ou Dia 15)
3. Clique em **📤 Enviar para Grupo Selecionado**

As mensagens já configuradas serão enviadas automaticamente!

---

## ⚙️ Configurar Grupos e Mensagens

**Para editar grupos, contatos e mensagens:**

1. Na aba **📱 Envio de Mensagem**, clique em **⚙️ Editar Configurações**
2. O arquivo `evolution_config.json` será aberto
3. Edite conforme necessário:
   - Adicione/remova contatos
   - Crie novos grupos
   - Personalize mensagens do dia 7 e dia 15
4. Salve e feche

**Exemplo de estrutura:**
```json
{
  "grupos": {
    "grupo1": {
      "nome": "Meus Clientes VIP",
      "contatos": [
        {"phone": "5519995378302", "name": "João Silva"},
        {"phone": "5519988776655", "name": "Maria Santos"}
      ]
    }
  },
  "mensagens": {
    "dia7": {
      "grupo1": "Olá {nome}! Hoje é dia 7..."
    },
    "dia15": {
      "grupo1": "Olá {nome}! Hoje é dia 15..."
    }
  }
}
```

---

## ⏰ Agendamento Automático

**Para enviar mensagens AUTOMATICAMENTE todo dia 7 e 15:**

1. Abra o arquivo `evolution_config.json`
2. Encontre a seção `"agendamento"`
3. Altere `"enabled": false` para `"enabled": true`
4. Configure o horário (formato 24h):
   ```json
   "agendamento": {
     "enabled": true,
     "horario_envio": "09:00",
     "dias_para_enviar": [7, 15]
   }
   ```
5. Salve o arquivo

**Como funciona:**
- Todo dia às 09:00 (ou horário configurado)
- O sistema verifica se é dia 7 ou 15
- Se sim, envia automaticamente para todos os grupos
- Usa as mensagens específicas de cada dia

---

## 📝 Formato de Telefone

**Todos estes formatos funcionam:**
- ✅ `5519995378302` ← **Recomendado**
- ✅ `19995378302` (adiciona 55 automaticamente)
- ✅ `(19) 99537-8302` (remove formatação)
- ✅ `+55 19 99537-8302` (remove formatação)

---

## 🧪 Testar a Funcionalidade

### Teste Rápido

1. Abra o sistema: `bash run.sh`
2. Vá na aba **📱 Envio de Mensagem**
3. Configure a API
4. Clique em **🧪 Testar Conexão**
5. Se aparecer ✅, está tudo OK!

### Teste de Envio

1. Adicione seu próprio número no campo de contatos:
   ```
   5519995378302 - Eu Mesmo
   ```
2. Escreva uma mensagem de teste:
   ```
   Olá {nome}! Este é um teste 🚀
   ```
3. Clique em **📤 Enviar Mensagens**
4. Você deve receber a mensagem no seu WhatsApp!

---

## ❓ Problemas Comuns

### ❌ "Erro na conexão"

**Solução:**
1. Verifique se a URL está correta
2. Confirme o nome da instância
3. Valide a API Key
4. Teste primeiro no Postman

### ❌ "Mensagem não enviada"

**Solução:**
1. Verifique o formato do número
2. Certifique-se de que o número está no WhatsApp
3. Aguarde alguns segundos e tente novamente

### ❌ "evolution_config.json não encontrado"

**Solução:**
```bash
bash install.sh  # Recria o arquivo
```

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **[EVOLUTION_API_GUIDE.md](EVOLUTION_API_GUIDE.md)** - Guia completo com exemplos avançados

---

## 🎯 Resumo dos Arquivos

**Novos arquivos criados:**
```
utils/evolution_api.py              # Cliente da Evolution API
automation/message_scheduler.py     # Agendador automático  
evolution_config.json               # Configurações
EVOLUTION_API_GUIDE.md              # Guia completo
QUICKSTART_MESSAGES.md              # Este arquivo
```

**Arquivos modificados:**
```
ui/modern_automation_gui.py         # Nova aba adicionada
requirements.txt                    # Adicionado 'schedule'
install.sh                          # Cria evolution_config.json
update.sh                           # Cria evolution_config.json
```

---

## 🎉 Pronto para Usar!

Tudo está configurado e pronto para usar!

**Próximos passos:**
1. Execute: `bash run.sh`
2. Configure sua Evolution API
3. Teste com seu próprio número
4. Configure seus grupos de clientes
5. Comece a enviar mensagens! 🚀

---

## 📞 Suas Informações

**Com base no que você me passou:**
- **URL:** `https://zap.tekvosoft.com`
- **Instância:** `david-tekvo`
- **API Key:** `634A7E882CE5-4314-8C5B-BC79C0A9EBBA`
- **Endpoint:** `POST /message/sendText/david-tekvo`
- **Formato:**
  ```json
  {
    "number": "5519995378302@c.us",
    "text": "Mensagem aqui"
  }
  ```

**Tudo isso já está implementado e funcionando!** 🎊

---

Desenvolvido com ❤️ para automação de mensagens WhatsApp
