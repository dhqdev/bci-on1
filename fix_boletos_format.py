#!/usr/bin/env python3
"""
Script para corrigir formato de cotas nos boletos
Boletos devem mostrar "2 cotas", "3 cotas", etc. quando há múltiplas
"""

import json

def fix_boletos_format():
    clientes_filepath = 'clientes_data.json'
    boletos_filepath = 'boletos_data.json'
    
    # Carrega clientes para saber quantas cotas cada um tem
    with open(clientes_filepath, 'r', encoding='utf-8') as f:
        clientes_data = json.load(f)
    
    # Carrega boletos
    with open(boletos_filepath, 'r', encoding='utf-8') as f:
        boletos_data = json.load(f)
    
    total_fixed = 0
    
    for dia_key in ['dia08', 'dia16']:
        print(f"\n📋 Processando {dia_key}...")
        
        # Cria mapa de clientes por nome
        clientes_map = {}
        for cliente in clientes_data.get(dia_key, []):
            nome = cliente.get('nome', '').strip().lower()
            clientes_map[nome] = cliente
        
        # Atualiza boletos
        for boleto in boletos_data.get(dia_key, []):
            nome = boleto.get('nome', '').strip().lower()
            
            if nome in clientes_map:
                cliente = clientes_map[nome]
                cotas = cliente.get('cotas', [])
                grupos = cliente.get('grupos', [])
                
                # Calcula formato correto para boleto
                if len(cotas) == 1 and len(grupos) == 1:
                    novo_formato = f"{cotas[0]} - {grupos[0]}"
                elif len(cotas) > 1:
                    novo_formato = f"{len(cotas)} cotas"
                else:
                    continue
                
                # Atualiza se for diferente
                formato_atual = boleto.get('cotas', '')
                if formato_atual != novo_formato:
                    print(f"  ✏️  {cliente.get('nome')}: '{formato_atual}' → '{novo_formato}'")
                    boleto['cotas'] = novo_formato
                    total_fixed += 1
    
    # Salva boletos corrigidos
    with open(boletos_filepath, 'w', encoding='utf-8') as f:
        json.dump(boletos_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Correção concluída! {total_fixed} boletos atualizados")

if __name__ == '__main__':
    fix_boletos_format()
