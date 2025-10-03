# test_protocol_extraction.py
# Teste de extração de protocolo do link DocParser

import base64
import json
from utils.protocol_extractor import _decode_docparser_payload

# Link de exemplo que você forneceu
docparser_url = "eyJ1cmwiOiJodHRwczovL3d3dy5jb25zb3JjaW9zZXJ2b3BhLmNvbS5ici9kb2NnZW4vbGFuY2UvaW5kZXgucGhwIiwiZGF0YSI6eyJudW1fcHJvdG9jb2xvX2FudCI6IjE3NDI0NSIsImRpZ2l0byI6IjciLCJncnVwbyI6IjE1NTQiLCJwbGFubyI6IjA5NzIiLCJubUNsaWVudGUiOiJBTkRSRSBMVUlTIFNBTlRPUyBIRU5SSVFVRVMiLCJuckFzc2VtYiI6IjI1IiwiZHRFZGl0YWRhIjoiMTYvMTAvMjAyNSIsImhyRWRpdGFkYSI6IjE2OjAwIiwibG9jYWwiOiJTRVJWT1BBIFNBIENPTUVSQ0lPIEUgSU5EVVNUUklBIiwiYmVtX3JlZmVyZW5jaWEiOiJDUkVESVRPIFAvSU1PVkVMIDYiLCJ0eExhbmZpeCI6IjMwIiwidmxMYW5maXgiOiI0MC45NDUsNTIiLCJxdExhbmZpZCI6IiIsInR4TGFuZmlkIjoiIiwidmxMYW5maWQiOiIiLCJ0eExhbmxpdiI6IiIsInZsTGFubGl2IjoiUiQgMCwwMCIsImRhdGEiOiIwMy8xMC8yMDI1IiwiaG9yYSI6IjAwOjE3Iiwic3RfZXZlbnRvIjoiRiIsImRzRGVzY3IxNSI6IiJ9fQ"

print("=" * 80)
print("🔍 TESTE DE EXTRAÇÃO DE PROTOCOLO")
print("=" * 80)

try:
    # Decodifica o payload
    payload = _decode_docparser_payload(docparser_url)
    
    print("\n✅ Payload decodificado com sucesso!")
    print("\n📄 Conteúdo completo do JSON:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # Extrai o protocolo
    data_block = payload.get("data", {})
    protocolo = data_block.get("num_protocolo_ant")
    
    print("\n" + "=" * 80)
    print(f"📑 PROTOCOLO EXTRAÍDO: {protocolo}")
    print("=" * 80)
    
    # Mostra outros dados importantes
    print(f"\n📊 Outros dados capturados:")
    print(f"   • Grupo: {data_block.get('grupo')}")
    print(f"   • Plano: {data_block.get('plano')}")
    print(f"   • Cliente: {data_block.get('nmCliente')}")
    print(f"   • Assembleia: {data_block.get('nrAssemb')}")
    print(f"   • Data: {data_block.get('dtEditada')}")
    print(f"   • Hora: {data_block.get('hrEditada')}")
    print(f"   • Tx Lance Fixo: {data_block.get('txLanfix')}%")
    print(f"   • Valor Lance: R$ {data_block.get('vlLanfix')}")
    
    print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("   O sistema está capturando o protocolo corretamente!")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
