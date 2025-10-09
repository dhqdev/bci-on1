#!/usr/bin/env python3
"""
Script para sincronizar dados de lance_registrado entre dia08/dia16 e grupos
"""

import json
import os

def fix_cotas_data():
    """Sincroniza lance_registrado de dia08/dia16 para grupos"""
    filepath = os.path.join(os.path.dirname(__file__), 'cotas_data.json')
    
    if not os.path.exists(filepath):
        print("❌ Arquivo cotas_data.json não encontrado")
        return
    
    print("📂 Carregando cotas_data.json...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Cria mapa de lances registrados por grupo+cota
    lances_map = {}
    
    # Coleta lances de dia08 e dia16
    for dia_key in ['dia08', 'dia16']:
        if dia_key not in data:
            continue
        
        for grupo_obj in data[dia_key]:
            grupo_num = str(grupo_obj.get('numero', ''))
            
            for cota_obj in grupo_obj.get('cotas', []):
                cota_num = str(cota_obj.get('cota', ''))
                
                if 'lance_registrado' in cota_obj:
                    key = f"{grupo_num}_{cota_num}"
                    lances_map[key] = cota_obj['lance_registrado']
                    print(f"✅ Lance encontrado em {dia_key}: Grupo {grupo_num}, Cota {cota_num} - {cota_obj['lance_registrado']['modalidade']} {cota_obj['lance_registrado']['valor']}%")
    
    print(f"\n📊 Total de lances encontrados: {len(lances_map)}")
    
    # Aplica lances ao array 'grupos'
    if 'grupos' not in data:
        print("⚠️ Array 'grupos' não encontrado")
        return
    
    updated_count = 0
    for grupo_obj in data['grupos']:
        grupo_num = str(grupo_obj.get('numero', ''))
        
        for cota_obj in grupo_obj.get('cotas', []):
            cota_num = str(cota_obj.get('cota', ''))
            key = f"{grupo_num}_{cota_num}"
            
            if key in lances_map:
                cota_obj['lance_registrado'] = lances_map[key]
                updated_count += 1
                print(f"🔄 Atualizado em 'grupos': Grupo {grupo_num}, Cota {cota_num}")
    
    print(f"\n💾 Salvando alterações...")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Arquivo atualizado! {updated_count} cotas sincronizadas.")

if __name__ == '__main__':
    fix_cotas_data()
