#!/usr/bin/env python3
"""
🤖 Script de Teste do Agente de IA OXCASH

Este script testa as funcionalidades principais do agente de IA.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.ai_agent import OXCASHAgent
import json


def print_header(title):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response):
    """Imprime a resposta do agente de forma formatada"""
    print(f"\n🤖 Resposta: {response['message']}")
    
    if response.get('actions'):
        print("\n📋 Ações executadas:")
        for action in response['actions']:
            print(f"   • {action['function']}")
            print(f"     Argumentos: {action['arguments']}")
            print(f"     Resultado: {json.dumps(action['result'], indent=6, ensure_ascii=False)[:200]}...")


def test_agent():
    """Testa o agente de IA"""
    
    # Carrega configuração
    config_file = 'ai_config.json'
    if not os.path.exists(config_file):
        print("❌ Arquivo ai_config.json não encontrado!")
        print("   Copie ai_config.json.example para ai_config.json e configure sua chave da OpenAI")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    api_key = config.get('openai_api_key')
    
    if not api_key or api_key == 'SUA-CHAVE-API-AQUI':
        print("❌ Chave da API OpenAI não configurada!")
        print("   Edite ai_config.json e adicione sua chave da OpenAI")
        return False
    
    print_header("🚀 Iniciando Testes do Agente de IA")
    
    # Cria agente
    print("\n📦 Criando instância do agente...")
    agent = OXCASHAgent(api_key)
    print("✅ Agente criado com sucesso!")
    
    # Teste 1: Status do sistema
    print_header("📊 TESTE 1: Status Geral do Sistema")
    response = agent.chat("Qual é o status geral do sistema?")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 1 falhou!")
        return False
    print("\n✅ Teste 1 passou!")
    
    # Teste 2: Estatísticas de boletos
    print_header("📄 TESTE 2: Estatísticas de Boletos")
    response = agent.chat("Quantos boletos foram emitidos? Me dê os números do dia 08 e do dia 16.")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 2 falhou!")
        return False
    print("\n✅ Teste 2 passou!")
    
    # Teste 3: Estatísticas de lances
    print_header("🎯 TESTE 3: Estatísticas de Lances")
    response = agent.chat("Quantos lances ainda estão pendentes?")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 3 falhou!")
        return False
    print("\n✅ Teste 3 passou!")
    
    # Teste 4: Histórico
    print_header("📋 TESTE 4: Histórico de Execuções")
    response = agent.chat("Mostre as últimas 3 execuções do histórico")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 4 falhou!")
        return False
    print("\n✅ Teste 4 passou!")
    
    # Teste 5: Busca
    print_header("🔍 TESTE 5: Busca de Cliente")
    response = agent.chat("Procure informações sobre clientes que tenham 'Silva' no nome")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 5 falhou!")
        return False
    print("\n✅ Teste 5 passou!")
    
    # Teste 6: Simulação de lance (sem executar)
    print_header("🎲 TESTE 6: Simulação de Lance")
    response = agent.chat("Simule a execução de um lance para o grupo 1550, cota 303")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 6 falhou!")
        return False
    print("\n✅ Teste 6 passou!")
    
    # Teste 7: Pergunta sobre o sistema
    print_header("💬 TESTE 7: Conversação Natural")
    response = agent.chat("Como funciona o sistema de automação de lances?")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 7 falhou!")
        return False
    print("\n✅ Teste 7 passou!")
    
    # Teste 8: Múltiplas consultas
    print_header("🔄 TESTE 8: Consulta Complexa")
    response = agent.chat("Me dê um resumo: total de boletos, total de lances, e última execução")
    print_response(response)
    
    if not response['success']:
        print("\n❌ Teste 8 falhou!")
        return False
    print("\n✅ Teste 8 passou!")
    
    # Relatório final
    print_header("✅ TODOS OS TESTES PASSARAM!")
    print(f"\n📊 Resumo:")
    print(f"   • Total de testes: 8")
    print(f"   • Sucessos: 8")
    print(f"   • Falhas: 0")
    print(f"   • Histórico de conversa: {len(agent.conversation_history)} mensagens")
    print(f"   • Ferramentas disponíveis: {len(agent.tools)} funções")
    
    return True


if __name__ == "__main__":
    try:
        success = test_agent()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
