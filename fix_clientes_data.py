#!/usr/bin/env python3
"""
Script para limpar e normalizar dados de clientes
- Remove campos duplicados 'grupo' e 'cota' (mantém apenas arrays 'grupos' e 'cotas')
- Garante que todos os clientes têm mes_relatorio definido
"""

import json
from datetime import datetime

def fix_clientes_data():
    filepath = 'clientes_data.json'
    
    # Carrega dados
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hoje = datetime.now()
    mes_atual = f"{hoje.year}-{str(hoje.month).zfill(2)}"
    
    total_fixed = 0
    total_cleaned = 0
    
    for dia_key in ['dia08', 'dia16']:
        if dia_key not in data:
            continue
            
        for cliente in data[dia_key]:
            # Remove campos antigos duplicados
            if 'grupo' in cliente:
                del cliente['grupo']
                total_cleaned += 1
            if 'cota' in cliente:
                del cliente['cota']
                total_cleaned += 1
            
            # Garante mes_relatorio
            if not cliente.get('mes_relatorio') or not cliente['mes_relatorio'].startswith('2025-'):
                cliente['mes_relatorio'] = mes_atual
                total_fixed += 1
    
    # Salva dados limpos
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Limpeza concluída!")
    print(f"   - {total_cleaned} campos duplicados removidos")
    print(f"   - {total_fixed} mes_relatorio corrigidos para {mes_atual}")
    
    # Mostra estatísticas
    dia08_count = len(data.get('dia08', []))
    dia16_count = len(data.get('dia16', []))
    print(f"\n📊 Total de clientes:")
    print(f"   - Dia 08: {dia08_count}")
    print(f"   - Dia 16: {dia16_count}")

if __name__ == '__main__':
    fix_clientes_data()
