# test_protocol_flow_complete.py
# Teste completo do fluxo de captura de protocolo

import json
from utils.protocol_extractor import extract_protocol_from_docparser

print("=" * 80)
print("🧪 TESTE COMPLETO - FLUXO DE CAPTURA DE PROTOCOLO")
print("=" * 80)
print()

# Simula diferentes formatos de URL que podem aparecer

test_cases = [
    {
        "name": "Formato 1: URL completa com /view/",
        "url": "https://www.consorcioservopa.com.br/docparser/view/eyJ1cmwiOiJodHRwczovL3d3dy5jb25zb3JjaW9zZXJ2b3BhLmNvbS5ici9kb2NnZW4vbGFuY2UvaW5kZXgucGhwIiwiZGF0YSI6eyJudW1fcHJvdG9jb2xvX2FudCI6IjE3NDI0NSIsImRpZ2l0byI6IjciLCJncnVwbyI6IjE1NTQiLCJwbGFubyI6IjA5NzIiLCJubUNsaWVudGUiOiJBTkRSRSBMVUlTIFNBTlRPUyBIRU5SSVFVRVMiLCJuckFzc2VtYiI6IjI1IiwiZHRFZGl0YWRhIjoiMTYvMTAvMjAyNSIsImhyRWRpdGFkYSI6IjE2OjAwIiwibG9jYWwiOiJTRVJWT1BBIFNBIENPTUVSQ0lPIEUgSU5EVVNUUklBIiwiYmVtX3JlZmVyZW5jaWEiOiJDUkVESVRPIFAvSU1PVkVMIDYiLCJ0eExhbmZpeCI6IjMwIiwidmxMYW5maXgiOiI0MC45NDUsNTIiLCJxdExhbmZpZCI6IiIsInR4TGFuZmlkIjoiIiwidmxMYW5maWQiOiIiLCJ0eExhbmxpdiI6IiIsInZsTGFubGl2IjoiUiQgMCwwMCIsImRhdGEiOiIwMy8xMC8yMDI1IiwiaG9yYSI6IjAwOjE3Iiwic3RfZXZlbnRvIjoiRiIsImRzRGVzY3IxNSI6IiJ9fQ",
        "should_work": True
    },
    {
        "name": "Formato 2: Somente Base64 (sem /view/)",
        "url": "eyJ1cmwiOiJodHRwczovL3d3dy5jb25zb3JjaW9zZXJ2b3BhLmNvbS5ici9kb2NnZW4vbGFuY2UvaW5kZXgucGhwIiwiZGF0YSI6eyJudW1fcHJvdG9jb2xvX2FudCI6IjE3NDI0NSIsImRpZ2l0byI6IjciLCJncnVwbyI6IjE1NTQiLCJwbGFubyI6IjA5NzIiLCJubUNsaWVudGUiOiJBTkRSRSBMVUlTIFNBTlRPUyBIRU5SSVFVRVMiLCJuckFzc2VtYiI6IjI1IiwiZHRFZGl0YWRhIjoiMTYvMTAvMjAyNSIsImhyRWRpdGFkYSI6IjE2OjAwIiwibG9jYWwiOiJTRVJWT1BBIFNBIENPTUVSQ0lPIEUgSU5EVVNUUklBIiwiYmVtX3JlZmVyZW5jaWEiOiJDUkVESVRPIFAvSU1PVkVMIDYiLCJ0eExhbmZpeCI6IjMwIiwidmxMYW5maXgiOiI0MC45NDUsNTIiLCJxdExhbmZpZCI6IiIsInR4TGFuZmlkIjoiIiwidmxMYW5maWQiOiIiLCJ0eExhbmxpdiI6IiIsInZsTGFubGl2IjoiUiQgMCwwMCIsImRhdGEiOiIwMy8xMC8yMDI1IiwiaG9yYSI6IjAwOjE3Iiwic3RfZXZlbnRvIjoiRiIsImRzRGVzY3IxNSI6IiJ9fQ",
        "should_work": True
    },
    {
        "name": "Formato 3: URL com /docgen/lance/",
        "url": "https://www.consorcioservopa.com.br/docgen/lance/index.php?data=eyJ1cmwiOiJodHRwczovL3d3dy5jb25zb3JjaW9zZXJ2b3BhLmNvbS5ici9kb2NnZW4vbGFuY2UvaW5kZXgucGhwIiwiZGF0YSI6eyJudW1fcHJvdG9jb2xvX2FudCI6IjE3NDI0NSIsImRpZ2l0byI6IjciLCJncnVwbyI6IjE1NTQiLCJwbGFubyI6IjA5NzIiLCJubUNsaWVudGUiOiJBTkRSRSBMVUlTIFNBTlRPUyBIRU5SSVFVRVMiLCJuckFzc2VtYiI6IjI1IiwiZHRFZGl0YWRhIjoiMTYvMTAvMjAyNSIsImhyRWRpdGFkYSI6IjE2OjAwIiwibG9jYWwiOiJTRVJWT1BBIFNBIENPTUVSQ0lPIEUgSU5EVVNUUklBIiwiYmVtX3JlZmVyZW5jaWEiOiJDUkVESVRPIFAvSU1PVkVMIDYiLCJ0eExhbmZpeCI6IjMwIiwidmxMYW5maXgiOiI0MC45NDUsNTIiLCJxdExhbmZpZCI6IiIsInR4TGFuZmlkIjoiIiwidmxMYW5maWQiOiIiLCJ0eExhbmxpdiI6IiIsInZsTGFubGl2IjoiUiQgMCwwMCIsImRhdGEiOiIwMy8xMC8yMDI1IiwiaG9yYSI6IjAwOjE3Iiwic3RfZXZlbnRvIjoiRiIsImRzRGVzY3IxNSI6IiJ9fQ",
        "should_work": False  # Não vai funcionar porque o Base64 está no parâmetro ?data=
    }
]

results = {
    "passed": 0,
    "failed": 0,
    "total": len(test_cases)
}

for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"TESTE {i}/{len(test_cases)}: {test['name']}")
    print(f"{'=' * 80}")
    print(f"URL: {test['url'][:100]}...")
    print()
    
    messages = []
    
    def mock_callback(msg):
        messages.append(msg)
        print(f"  {msg}")
    
    try:
        # Simula extração sem driver (vai falhar no download do PDF mas isso é ok)
        result = extract_protocol_from_docparser(
            driver=None,  # Sem driver, só testa extração do JSON
            docparser_url=test['url'],
            progress_callback=mock_callback
        )
        
        print()
        if result.protocol:
            print(f"✅ SUCESSO: Protocolo extraído = {result.protocol}")
            print(f"   Fonte: {result.source}")
            
            if test['should_work']:
                results['passed'] += 1
                print(f"   ✅ Resultado esperado!")
            else:
                results['failed'] += 1
                print(f"   ⚠️  Funcionou mas não era esperado!")
        else:
            print(f"❌ FALHA: Protocolo NÃO foi extraído")
            
            if test['should_work']:
                results['failed'] += 1
                print(f"   ❌ Deveria ter funcionado!")
            else:
                results['passed'] += 1
                print(f"   ✅ Falha esperada (formato não suportado)")
                
    except Exception as e:
        print(f"❌ ERRO: {e}")
        if test['should_work']:
            results['failed'] += 1
            print(f"   ❌ Erro inesperado!")
        else:
            results['passed'] += 1
            print(f"   ✅ Erro esperado (formato não suportado)")

# Resumo final
print()
print("=" * 80)
print("📊 RESUMO DOS TESTES")
print("=" * 80)
print(f"Total de testes: {results['total']}")
print(f"✅ Aprovados: {results['passed']}")
print(f"❌ Reprovados: {results['failed']}")
print()

if results['failed'] == 0:
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("   O sistema está pronto para capturar protocolos")
else:
    print("⚠️  ALGUNS TESTES FALHARAM")
    print("   Verifique os formatos de URL que não funcionaram")

print()
print("=" * 80)
print("📝 NOTA:")
print("   - Formato 1 e 2 devem SEMPRE funcionar")
print("   - Formato 3 precisa de ajuste no código se aparecer")
print("   - Se TODOS falharem, há problema na instalação do pdfplumber")
print("=" * 80)
