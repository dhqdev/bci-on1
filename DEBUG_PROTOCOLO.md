# 🔍 DEBUG - PROTOCOLO NÃO APARECENDO NA COLUNA

## ❌ PROBLEMA
Após instalar o `pdfplumber`, o protocolo ainda não aparece na coluna do histórico.

## 🎯 DIAGNÓSTICO

### PASSO 1: Execute o debug manual
```powershell
python debug_protocol_urls.py
```

Siga as instruções na tela:
1. O Chrome vai abrir
2. Faça login no Servopa
3. Navegue até a página de lances
4. Clique em "Registrar"
5. O script vai mostrar TODAS as URLs

**O que procurar:**
- A URL que aparece deve conter `/view/` ou `docgen/lance`
- Anote a URL completa que aparece

---

### PASSO 2: Execute a automação com DEBUG ativado

Agora o código tem MUITO mais mensagens de debug. Execute a automação normalmente e veja as mensagens no log:

```
🔍 DEBUG: Iniciando captura de protocolo...
🔍 DEBUG: Janelas antes: 1
🔍 DEBUG: 1 nova(s) janela(s) detectada(s)
🔍 DEBUG: URL ou nova janela detectada!
🔍 DEBUG: Janelas depois: 2
🔍 DEBUG: Novas janelas: 1
🔍 DEBUG: Verificando janela 1/2
🔍 DEBUG: URL = https://www.consorcioservopa.com.br/docparser/view/...
✅ DEBUG: URL de protocolo encontrada!
📄 Documento de protocolo detectado, extraindo dados...
🔍 DEBUG: URL recebida para extração: https://...
🔍 DEBUG: Base64 extraído da URL (/view/): eyJ1cmw...
✅ DEBUG: Payload decodificado com sucesso!
🔍 DEBUG: Procurando protocolo em 3 campos...
✅ DEBUG: Protocolo encontrado no campo 'num_protocolo_ant': 174245
📑 Protocolo capturado: 174245
✅ DEBUG: Protocolo extraído: 174245
🔍 DEBUG: Protocolo final: 174245
```

**Se você NÃO ver essas mensagens:**
- Copie TODAS as mensagens que aparecem
- Envie para análise

---

### PASSO 3: Verifique o histórico JSON

Abra o arquivo:
```
history_dia8.json
```

Procure pela última entrada e veja se tem o campo `protocolo`:

```json
{
  "hora": "16:00:00",
  "data": "2025-10-03",
  "grupo": "1554",
  "cota": "0972",
  "nome": "ANDRE LUIS SANTOS HENRIQUES",
  "valor_lance": "30%",
  "status": "✅ Sucesso",
  "observacao": "Lance registrado com sucesso",
  "protocolo": "174245",    <--- DEVE TER AQUI
  "documento_url": "https://..."
}
```

**Se NÃO tiver o campo `protocolo`:**
- O problema está na captura
- As mensagens de debug vão mostrar onde falhou

---

## 🔧 POSSÍVEIS CAUSAS E SOLUÇÕES

### Causa 1: URL diferente do esperado
**Sintoma:** Nas mensagens de debug aparece:
```
⚠️ DEBUG: Formato de URL não reconhecido!
```

**Solução:** Me envie a URL completa que aparece, vou ajustar o código.

---

### Causa 2: Aba abre e fecha muito rápido
**Sintoma:** Nas mensagens de debug aparece:
```
🔍 DEBUG: Novas janelas: 0
```

**Solução:** Aumentar tempo de espera ou capturar de forma diferente.

---

### Causa 3: Popup de "protocolo anterior obrigatório"
**Sintoma:** O lance já existe e o popup impede a abertura do documento.

**Solução:** Neste caso não tem protocolo mesmo, é esperado.

---

### Causa 4: Documento não abre em nova aba
**Sintoma:** Nas mensagens de debug aparece:
```
🔍 DEBUG: Novas janelas: 0
🔍 DEBUG: URL não contém protocolo, pulando...
```

**Solução:** Verificar se o documento abre na mesma aba ou em popup.

---

## 📊 CHECKLIST DE VERIFICAÇÃO

Execute estes comandos e me envie os resultados:

```powershell
# 1. Verifica se pdfplumber está instalado
python -c "import pdfplumber; print('✅ pdfplumber instalado:', pdfplumber.__version__)"

# 2. Testa extração de protocolo do exemplo
python test_protocol_extraction.py

# 3. Verifica se o arquivo de histórico existe
dir history_dia8.json

# 4. Verifica última linha do histórico
python -c "import json; data=json.load(open('history_dia8.json')); print('Última entrada:', data[-1] if data else 'Vazio')"
```

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Execute o `debug_protocol_urls.py`
2. ✅ Execute a automação e copie TODAS as mensagens de debug
3. ✅ Verifique o `history_dia8.json`
4. ✅ Me envie os resultados

Com essas informações vou identificar exatamente onde está o problema!
