import json
import os

# Testa leitura do arquivo de boletos
filepath = 'boletos_data.json'

print("=" * 60)
print("TESTE DE LEITURA DO ARQUIVO BOLETOS")
print("=" * 60)

# Lê o arquivo
with open(filepath, 'rb') as f:
    raw_bytes = f.read()
    print(f"\n📊 Primeiros 50 bytes (raw): {raw_bytes[:50]}")
    bom_utf8 = b'\xef\xbb\xbf'
    has_bom = raw_bytes.startswith(bom_utf8)
    print(f"📊 Tem BOM UTF-8? {has_bom}")

# Lê como texto
with open(filepath, 'r', encoding='utf-8-sig') as f:
    content = f.read()
    print(f"\n📝 Conteúdo (primeiros 200 chars):\n{content[:200]}")

# Tenta parse JSON
try:
    data = json.loads(content)
    print(f"\n✅ JSON válido!")
    print(f"📊 Estrutura: {list(data.keys())}")
    print(f"📊 Dia 08: {len(data.get('dia08', []))} boletos")
    print(f"📊 Dia 16: {len(data.get('dia16', []))} boletos")
except json.JSONDecodeError as e:
    print(f"\n❌ Erro ao fazer parse JSON: {e}")

print("\n" + "=" * 60)
