#!/usr/bin/env python3
"""
Script de teste para validar a integração com Todoist REST API
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.todoist_rest_api import TodoistRestAPI

def test_todoist_api():
    """Testa a API do Todoist"""
    
    print("=" * 80)
    print("🧪 TESTE DA API REST DO TODOIST")
    print("=" * 80)
    print()
    
    # Token
    TODOIST_TOKEN = "aa4b5ab41a462bd6fd5dbae643b45fe9bfaeeded"
    
    try:
        print("📡 Criando cliente da API...")
        api = TodoistRestAPI(TODOIST_TOKEN)
        print("✅ Cliente criado com sucesso")
        print()
        
        print("📂 Buscando projeto 'Boletos Servopa Outubro'...")
        project = api.get_project_by_name("Boletos Servopa Outubro")
        
        if not project:
            print("❌ Projeto não encontrado!")
            print("📋 Projetos disponíveis:")
            projects = api.get_projects()
            for p in projects:
                print(f"   - {p['name']} (ID: {p['id']})")
            return False
        
        print(f"✅ Projeto encontrado: {project['name']} (ID: {project['id']})")
        print()
        
        print("📂 Buscando seções do projeto...")
        sections = api.get_sections(project['id'])
        print(f"✅ Encontradas {len(sections)} seções:")
        for section in sections:
            print(f"   - {section['name']} (ID: {section['id']})")
        print()
        
        print("📋 Extraindo dados do board...")
        
        def progress_callback(msg):
            print(f"   {msg}")
        
        boletos_data = api.extract_boletos_board(
            project_name="Boletos Servopa Outubro",
            section_dia08="Vencimento dia 08",
            section_dia16="Vencimento dia 16",
            progress_callback=progress_callback
        )
        
        print()
        print("=" * 80)
        print("📊 RESULTADO DA EXTRAÇÃO")
        print("=" * 80)
        print()
        
        print(f"📅 Vencimento dia 08: {len(boletos_data['dia08'])} boletos")
        print("-" * 80)
        for idx, boleto in enumerate(boletos_data['dia08'], 1):
            status = "✅" if boleto['is_completed'] else "⬜"
            print(f"{idx}. {status} {boleto['nome']}")
            if boleto['cotas']:
                print(f"   📝 {boleto['cotas']}")
            print(f"   🔗 Task ID: {boleto['task_id']}")
            print()
        
        print()
        print(f"📅 Vencimento dia 16: {len(boletos_data['dia16'])} boletos")
        print("-" * 80)
        for idx, boleto in enumerate(boletos_data['dia16'], 1):
            status = "✅" if boleto['is_completed'] else "⬜"
            print(f"{idx}. {status} {boleto['nome']}")
            if boleto['cotas']:
                print(f"   📝 {boleto['cotas']}")
            print(f"   🔗 Task ID: {boleto['task_id']}")
            print()
        
        print("=" * 80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERRO NO TESTE")
        print("=" * 80)
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_todoist_api()
    sys.exit(0 if success else 1)
