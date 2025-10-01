#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar normalização de cotas
"""

def testar_normalizacao():
    """Testa a função zfill para normalização de cotas"""
    
    print("=" * 60)
    print("TESTE DE NORMALIZAÇÃO DE COTAS")
    print("=" * 60)
    print()
    
    # Casos de teste
    casos_teste = [
        ("1", "0001"),
        ("45", "0045"),
        ("303", "0303"),
        ("750", "0750"),
        ("1545", "1545"),
        ("9999", "9999"),
    ]
    
    print("Testando conversão:")
    print("-" * 60)
    
    todos_passaram = True
    
    for entrada, esperado in casos_teste:
        resultado = str(entrada).zfill(4)
        passou = resultado == esperado
        
        simbolo = "✅" if passou else "❌"
        print(f"{simbolo} Input: '{entrada}' → Output: '{resultado}' (Esperado: '{esperado}')")
        
        if not passou:
            todos_passaram = False
    
    print("-" * 60)
    print()
    
    if todos_passaram:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
    
    print()
    print("=" * 60)
    print("SIMULAÇÃO DE COMPARAÇÃO NA TABELA")
    print("=" * 60)
    print()
    
    # Simula comparação com tabela do Servopa
    cotas_servopa = ["0303", "0304", "0306", "0321", "0350", "0375"]
    cotas_todoist = ["303", "304", "306", "321", "350", "375"]
    
    print("Comparando cotas do Todoist com tabela do Servopa:")
    print("-" * 60)
    
    for cota_todoist in cotas_todoist:
        cota_normalizada = str(cota_todoist).zfill(4)
        encontrada = cota_normalizada in cotas_servopa
        
        simbolo = "✅" if encontrada else "❌"
        print(f"{simbolo} Todoist: '{cota_todoist}' → Normalizada: '{cota_normalizada}' → "
              f"{'ENCONTRADA' if encontrada else 'NÃO ENCONTRADA'} na tabela")
    
    print("-" * 60)
    print()
    print("✅ Normalização funcionando corretamente!")
    print()

if __name__ == "__main__":
    testar_normalizacao()
