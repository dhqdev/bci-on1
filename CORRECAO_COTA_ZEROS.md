# Correção: Normalização de Números de Cota

## 🐛 Problema Identificado

O sistema estava falhando ao selecionar cotas porque:

1. **No Todoist**: As cotas vêm sem zeros à esquerda → `303`, `750`, `1545`
2. **No Servopa**: As cotas aparecem com 4 dígitos → `0303`, `0750`, `1545`
3. **Comparação falhava**: `"303" != "0303"` → Cota não encontrada

## ✅ Solução Implementada

### Arquivo Modificado: `automation/servopa_lances.py`

Função `selecionar_cota()` foi atualizada para:

```python
# ANTES - Comparava direto (ERRADO)
if cota_value == cota_number:  # "0303" != "303" ❌

# DEPOIS - Normaliza primeiro (CORRETO)
cota_normalizada = str(cota_number).zfill(4)  # "303" → "0303"
if cota_value == cota_normalizada:  # "0303" == "0303" ✅
```

### Mudanças Detalhadas

1. **Normalização com `zfill(4)`:**
   ```python
   cota_normalizada = str(cota_number).zfill(4)
   ```
   - `"303"` → `"0303"` ✅
   - `"750"` → `"0750"` ✅
   - `"1545"` → `"1545"` ✅ (já tem 4 dígitos)

2. **Log melhorado para debug:**
   ```python
   progress_callback(f"🔍 Procurando cota {cota_number} (normalizada: {cota_normalizada})")
   ```
   - Mostra o número original E o normalizado
   - Facilita identificar problemas

3. **Lista de cotas encontradas:**
   ```python
   cotas_encontradas = []
   for row in rows:
       cotas_encontradas.append(cota_value)
   ```
   - Se não encontrar, mostra todas as cotas disponíveis
   - Ajuda a debugar problemas

4. **Mensagem de erro detalhada:**
   ```python
   if progress_callback:
       progress_callback(f"❌ Cota {cota_normalizada} não encontrada")
       progress_callback(f"📋 Cotas disponíveis: {', '.join(cotas_encontradas[:10])}")
   ```

## 📊 Exemplo de Funcionamento

### Cenário 1: Cota com poucos dígitos
```
Todoist: "303"
↓ Normalização
Sistema: "0303"
↓ Busca na tabela
Servopa: "0303" ← ENCONTRADO ✅
↓ Clica na linha
Abre página da cota
```

### Cenário 2: Cota com 4 dígitos
```
Todoist: "1545"
↓ Normalização
Sistema: "1545" (já tem 4 dígitos)
↓ Busca na tabela
Servopa: "1545" ← ENCONTRADO ✅
↓ Clica na linha
Abre página da cota
```

## 🔍 Como Validar

### No Log do Sistema:
```
📊 18 linhas encontradas, procurando cota 0303...
✅ Cota 303 encontrada: ANTONIO PEREIRA
🖱️ Clicando na linha da cota...
```

### Se Houver Problema:
```
📊 18 linhas encontradas, procurando cota 0303...
❌ Cota 0303 não encontrada na tabela
📋 Cotas disponíveis: 0304, 0306, 0321, 0350, 0375, 0470, 0480, 0507, 0570, 0575
   ... e mais 8 cotas
```

## 🎯 Fluxo Completo Após Correção

1. **Extrai cota do Todoist:** `"303"`
2. **Normaliza para 4 dígitos:** `"0303"`
3. **Busca grupo no Servopa:** `"1545"`
4. **Carrega tabela de cotas**
5. **Procura linha com cota:** `"0303"`
6. **Encontra e clica na linha:** `<tr onclick="...">`
7. **Redireciona para página da cota**
8. **Navega para Lances**
9. **Copia valor de tx_lanfix**
10. **Cola em tx_lanfix_emb**
11. **Clica em "Simular Lance"**
12. **Clica em "Registrar"**
13. **Verifica popup de protocolo anterior**
14. **Marca checkbox no Todoist**
15. **Registra no histórico**

## 🧪 Teste Manual

Para testar a correção:

1. Execute o sistema
2. Na aba "🚀 Automação" ou "🚀 Lances Dia 16"
3. Clique em "Iniciar"
4. Observe o log:
   - ✅ Deve mostrar: `"procurando cota 0303"` (com zero)
   - ✅ Deve mostrar: `"Cota 303 encontrada: NOME_CLIENTE"`
   - ✅ Deve clicar na linha e prosseguir

## 📝 Notas Técnicas

### Método `zfill()`
- Preenche string com zeros à esquerda
- Garante tamanho mínimo especificado
- Exemplos:
  - `"1".zfill(4)` → `"0001"`
  - `"45".zfill(4)` → `"0045"`
  - `"303".zfill(4)` → `"0303"`
  - `"1545".zfill(4)` → `"1545"`

### Por que 4 dígitos?
- Servopa usa formato `XXXX` para cotas
- Permite até 9999 cotas por grupo
- Padrão do sistema de consórcios

## ✅ Status

- [x] Problema identificado
- [x] Solução implementada
- [x] Código validado (sem erros de sintaxe)
- [x] Log de debug adicionado
- [ ] Teste em produção pendente

---

**Data da Correção:** 01/10/2025  
**Arquivo Modificado:** `automation/servopa_lances.py`  
**Função:** `selecionar_cota()`
