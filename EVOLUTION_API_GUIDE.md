# 📱 Funcionalidade de Envio de Mensagens WhatsApp

## 📋 Visão Geral

Sistema integrado de envio de mensagens WhatsApp via Evolution API, com suporte para:
- Envio manual de mensagens
- Envio por grupos configurados
- Agendamento automático para dias 7 e 15
- Personalização de mensagens por contato
- Gerenciamento de múltiplos grupos

---

## 🚀 Como Usar

### 1. Configurar Evolution API

Na aba **"📱 Envio de Mensagem"**, configure:

**URL da API:**
```
https://zap.tekvosoft.com
```

**Nome da Instância:**
```
david-tekvo
```
*Troque pelo nome da sua instância*

**API Key:**
```
634A7E882CE5-4314-8C5B-BC79C0A9EBBA
```
*Troque pela sua API Key*

Clique em **🧪 Testar Conexão** para validar.

---

### 2. Envio Manual de Mensagens

**📝 Como funciona:**

1. **Adicionar Contatos** (coluna esquerda):
   ```
   5519995378302 - João Silva
   5519988776655 - Maria Santos
   19977665544 - Ana Costa
   ```
   - Formato: `TELEFONE - NOME`
   - Um contato por linha
   - O código do país (55) é adicionado automaticamente se não existir

2. **Escrever Mensagem** (coluna direita):
   ```
   Olá {nome}! 🎉
   
   Esta é uma mensagem personalizada para você!
   ```
   - Use `{nome}` para personalizar com o nome do contato
   - Suporta emojis e quebras de linha

3. Clique em **📤 Enviar Mensagens**

4. Acompanhe o progresso no **Log de Envio**

---

### 3. Envio por Grupo Configurado

**📊 Como funciona:**

1. Selecione o **Grupo** (Grupo 1 ou Grupo 2)
2. Selecione o **Dia** (Dia 7 ou Dia 15)
3. Clique em **📤 Enviar para Grupo Selecionado**

As mensagens configuradas para aquele grupo e dia serão enviadas automaticamente.

**⚙️ Para editar configurações:**
- Clique em **⚙️ Editar Configurações**
- Edite o arquivo `evolution_config.json`
- Salve e feche

---

## 📝 Arquivo de Configuração

### Estrutura do `evolution_config.json`

```json
{
  "api": {
    "base_url": "https://zap.tekvosoft.com",
    "instance_name": "sua-instancia",
    "api_key": "SUA-API-KEY"
  },
  
  "grupos": {
    "grupo1": {
      "nome": "Grupo 1 - Clientes Principal",
      "contatos": [
        {
          "phone": "5519995378302",
          "name": "João Silva"
        },
        {
          "phone": "5519988776655",
          "name": "Maria Santos"
        }
      ]
    },
    "grupo2": {
      "nome": "Grupo 2 - Clientes Secundário",
      "contatos": [
        {
          "phone": "5519977665544",
          "name": "Ana Costa"
        }
      ]
    }
  },
  
  "mensagens": {
    "dia7": {
      "grupo1": "Olá {nome}! 🎉\n\nMensagem do dia 7 para grupo 1",
      "grupo2": "Oi {nome}! 📢\n\nMensagem do dia 7 para grupo 2"
    },
    "dia15": {
      "grupo1": "Olá {nome}! 🎯\n\nMensagem do dia 15 para grupo 1",
      "grupo2": "Oi {nome}! ⏰\n\nMensagem do dia 15 para grupo 2"
    }
  },
  
  "agendamento": {
    "enabled": false,
    "horario_envio": "09:00",
    "dias_para_enviar": [7, 15]
  },
  
  "configuracoes": {
    "delay_entre_mensagens": 2.0,
    "tentar_reenviar_falhas": true,
    "max_tentativas": 3
  }
}
```

---

## ⏰ Agendamento Automático

### Como Ativar

1. Abra `evolution_config.json`
2. Altere `"enabled": false` para `"enabled": true` na seção `agendamento`
3. Configure o horário desejado (formato 24h):
   ```json
   "horario_envio": "09:00"
   ```
4. Salve o arquivo

### Como Funciona

- O sistema verifica automaticamente todo dia às 09:00 (ou horário configurado)
- Se for dia 7 ou 15, envia as mensagens automaticamente
- Envia para todos os grupos configurados
- Usa as mensagens específicas de cada dia

### Para Usar o Agendador

**Opção 1: Via Python**
```python
from automation.message_scheduler import MessageScheduler

# Criar agendador
scheduler = MessageScheduler()

# Iniciar (roda em background)
scheduler.start()

# Para parar
scheduler.stop()
```

**Opção 2: Script Standalone**
```bash
python -m automation.message_scheduler
```

---

## 🔧 Configurações Avançadas

### Delay entre Mensagens

Para evitar bloqueios do WhatsApp, há um delay entre cada mensagem:

```json
"configuracoes": {
  "delay_entre_mensagens": 2.0
}
```

**Valores recomendados:**
- Poucos contatos (< 10): 1.0 segundo
- Médio volume (10-50): 2.0 segundos
- Alto volume (> 50): 3.0 segundos

### Tentativas de Reenvio

```json
"configuracoes": {
  "tentar_reenviar_falhas": true,
  "max_tentativas": 3
}
```

---

## 📞 Formato de Telefone

**Formatos Aceitos:**
- ✅ `5519995378302` (recomendado)
- ✅ `19995378302` (adiciona 55 automaticamente)
- ✅ `(19) 99537-8302` (remove formatação)
- ✅ `+55 19 99537-8302` (remove formatação)

**Formato Final:** `5519995378302@c.us`

---

## 🧪 Testando a Funcionalidade

### Teste 1: Conexão com API

```bash
cd /home/david/Área\ de\ trabalho/localbci1/auto-oxbci
source venv/bin/activate
python utils/evolution_api.py
```

### Teste 2: Parse de Contatos

```python
from utils.evolution_api import parse_contacts_from_text

text = """
5519995378302 - João Silva
19988776655 - Maria Santos
"""

contacts = parse_contacts_from_text(text)
print(contacts)
```

### Teste 3: Envio Manual

Use a interface GUI:
1. Abra a aba **📱 Envio de Mensagem**
2. Configure a API
3. Adicione um contato de teste
4. Escreva uma mensagem simples
5. Clique em **📤 Enviar Mensagens**

### Teste 4: Agendamento

```python
from automation.message_scheduler import MessageScheduler

scheduler = MessageScheduler()
scheduler.load_config()

# Testar se é dia de envio
dia = scheduler.check_if_should_send_today()
print(f"Dia de envio: {dia}")

# Teste de envio imediato (não espera agendamento)
# scheduler.test_send_now()
```

---

## ❓ Solução de Problemas

### Erro: "Conexão falhou"

**Possíveis causas:**
1. URL da API incorreta
2. Nome da instância incorreto
3. API Key inválida
4. Instância offline no servidor Evolution

**Solução:**
- Verifique as credenciais no Postman primeiro
- Certifique-se de que a instância está conectada
- Teste com: `https://sua-url/message/sendText/sua-instancia`

### Erro: "Mensagem não enviada"

**Possíveis causas:**
1. Número de telefone inválido
2. Número não está no WhatsApp
3. Bloqueio temporário do WhatsApp

**Solução:**
- Verifique o formato do número
- Teste com um número que você sabe que funciona
- Aumente o delay entre mensagens

### Erro: "evolution_config.json não encontrado"

**Solução:**
```bash
bash install.sh  # Recria o arquivo
# ou
bash update.sh   # Atualiza e cria se não existir
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Envio Simples

```python
from utils.evolution_api import EvolutionAPI

api = EvolutionAPI(
    "https://zap.tekvosoft.com",
    "david-tekvo",
    "634A7E882CE5-4314-8C5B-BC79C0A9EBBA"
)

success, response = api.send_text_message(
    "5519995378302",
    "Olá! Esta é uma mensagem de teste 🚀"
)

print(f"Sucesso: {success}")
print(f"Resposta: {response}")
```

### Exemplo 2: Envio em Massa

```python
from utils.evolution_api import EvolutionAPI

api = EvolutionAPI(
    "https://zap.tekvosoft.com",
    "david-tekvo",
    "634A7E882CE5-4314-8C5B-BC79C0A9EBBA"
)

contacts = [
    {"phone": "5519995378302", "name": "João"},
    {"phone": "5519988776655", "name": "Maria"}
]

message = "Olá {nome}! Tudo bem? 😊"

results = api.send_bulk_messages(
    contacts,
    message,
    delay_between_messages=2.0
)

print(f"Enviadas: {results['success']}")
print(f"Falhas: {results['failed']}")
```

### Exemplo 3: Agendamento

```python
from automation.message_scheduler import MessageScheduler

def my_callback(message):
    print(f"[LOG] {message}")

scheduler = MessageScheduler(
    config_file='evolution_config.json',
    progress_callback=my_callback
)

# Iniciar em background
scheduler.start()

# Manter rodando
import time
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    scheduler.stop()
```

---

## 🔐 Segurança

⚠️ **IMPORTANTE:**

1. **NÃO compartilhe** seu arquivo `evolution_config.json`
2. **NÃO faça commit** da API Key no GitHub
3. Adicione ao `.gitignore`:
   ```
   evolution_config.json
   ```

4. Mantenha backups das configurações em local seguro

---

## 📚 Arquivos Criados

```
auto-oxbci/
├── utils/
│   └── evolution_api.py          # Cliente da Evolution API
├── automation/
│   └── message_scheduler.py      # Agendador automático
├── evolution_config.json          # Configurações
├── requirements.txt               # Atualizado com 'schedule'
├── install.sh                     # Atualizado
├── update.sh                      # Atualizado
└── ui/
    └── modern_automation_gui.py   # Nova aba adicionada
```

---

## 🎯 Funcionalidades Implementadas

✅ Envio manual de mensagens  
✅ Envio para múltiplos contatos  
✅ Personalização com {nome}  
✅ Grupos configuráveis  
✅ Mensagens diferentes por dia (7 e 15)  
✅ Agendamento automático  
✅ Teste de conexão  
✅ Log detalhado de envios  
✅ Interface gráfica integrada  
✅ Formatação automática de números  
✅ Delay configurável entre mensagens  

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique o **Log de Envio** na interface
2. Teste primeiro no **Postman** para validar a API
3. Consulte esta documentação
4. Verifique os logs do servidor Evolution API

---

**Desenvolvido para integração com Evolution API WhatsApp** 🚀
