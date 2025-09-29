#!/usr/bin/env python3
# test_credentials.py
# Teste para verificar se as credenciais estão sendo lidas corretamente

import json
import os

def test_credentials():
    credentials_file = 'credentials.json'
    
    print("🔍 Testando sistema de credenciais...\n")
    
    # Verifica se arquivo existe
    if not os.path.exists(credentials_file):
        print(f"❌ Arquivo {credentials_file} não encontrado!")
        print("💡 Execute a interface e salve as credenciais primeiro.")
        return
    
    # Carrega e exibe credenciais
    try:
        with open(credentials_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ Arquivo de credenciais encontrado!")
        print(f"📄 Conteúdo do arquivo {credentials_file}:\n")
        
        # Mostra estrutura
        for service, creds in data.items():
            print(f"🔐 {service.upper()}:")
            print(f"   Usuario: {creds.get('usuario', 'NÃO ENCONTRADO')}")
            print(f"   Senha: {'*' * len(creds.get('senha', '')) if creds.get('senha') else 'NÃO ENCONTRADA'}")
            print()
        
        # Testa se estrutura está correta
        required_services = ['servopa', 'todoist']
        required_fields = ['usuario', 'senha']
        
        all_ok = True
        for service in required_services:
            if service not in data:
                print(f"❌ Serviço '{service}' não encontrado!")
                all_ok = False
                continue
                
            for field in required_fields:
                if field not in data[service] or not data[service][field]:
                    print(f"❌ Campo '{field}' vazio ou não encontrado em '{service}'!")
                    all_ok = False
        
        if all_ok:
            print("🎉 Todas as credenciais estão corretas!")
        else:
            print("⚠️ Há problemas com as credenciais.")
            
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_credentials()