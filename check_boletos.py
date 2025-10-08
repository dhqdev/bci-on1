#!/usr/bin/env python3
"""
Script para verificar e exibir estrutura de boletos
"""

import json

def check_boletos():
    filepath = 'boletos_data.json'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        dia08 = data.get('dia08', [])
        dia16 = data.get('dia16', [])
        
        print(f"📊 Total de boletos:")
        print(f"   - Dia 08: {len(dia08)}")
        print(f"   - Dia 16: {len(dia16)}")
        
        if dia08:
            print(f"\n📋 Boletos Dia 08:")
            for idx, boleto in enumerate(dia08, 1):
                print(f"   {idx}. {boleto.get('nome')} - Cotas: {boleto.get('cotas')}")
        
        if dia16:
            print(f"\n📋 Boletos Dia 16:")
            for idx, boleto in enumerate(dia16, 1):
                print(f"   {idx}. {boleto.get('nome')} - Cotas: {boleto.get('cotas')}")
    
    except FileNotFoundError:
        print("❌ Arquivo boletos_data.json não encontrado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    check_boletos()
