"""
🤖 AGENTE DE IA INTELIGENTE - Sistema OXCASH

Este módulo implementa um agente de IA baseado em Google Gemini (GRATUITO!) que tem
acesso completo a todo o sistema OXCASH, podendo:

- Consultar quantidade de boletos emitidos ou pendentes
- Consultar quantidade de lances realizados
- Verificar histórico de execuções
- Executar lances automaticamente
- Gerar boletos automaticamente
- Enviar mensagens via WhatsApp
- Consultar credenciais e configurações
- Responder perguntas sobre o sistema

O agente usa Function Calling do Gemini para executar ações de forma segura.
"""

import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import google.generativeai as genai


class OXCASHAgent:
    """Agente de IA inteligente com acesso total ao sistema OXCASH"""
    
    def __init__(self, api_key: str, project_root: str = None, session_id: str = None):
        """
        Inicializa o agente de IA
        
        Args:
            api_key: Chave da API Google Gemini
            project_root: Diretório raiz do projeto (opcional)
            session_id: ID da sessão do usuário (para persistir conversas)
        """
        # Configura Google Gemini
        genai.configure(api_key=api_key)
        
        # Cria modelo Gemini 2.0 Flash (versão gratuita e rápida)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.session_id = session_id or 'default'
        self.conversation_history = []
        self.callbacks = {}  # Callbacks para execução de ações reais
        
        # Carrega histórico persistido
        self._load_conversation_history()
        
        # Definição das ferramentas/funções disponíveis para o agente (formato Gemini)
        self.tools = [
            genai.protos.Tool(
                function_declarations=[
                    genai.protos.FunctionDeclaration(
                        name="get_boletos_stats",
                        description="Retorna estatísticas sobre boletos: total, emitidos, pendentes, por dia (08 ou 16)",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "dia": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Dia específico (08, 16) ou 'all' para todos",
                                    enum=["08", "16", "all"]
                                )
                            },
                            required=["dia"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_lances_stats",
                        description="Retorna estatísticas sobre lances: total, concluídos, pendentes, por dia (08 ou 16)",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "dia": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Dia específico (08, 16) ou 'all' para todos",
                                    enum=["08", "16", "all"]
                                )
                            },
                            required=["dia"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_history",
                        description="Retorna o histórico de execuções (lances realizados)",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "dia": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Dia específico ou 'both' para ambos",
                                    enum=["dia8", "dia16", "both"]
                                ),
                                "limit": genai.protos.Schema(
                                    type=genai.protos.Type.INTEGER,
                                    description="Número máximo de registros a retornar"
                                )
                            },
                            required=["dia"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="execute_lance",
                        description="Executa um lance no Servopa para um grupo e cota específicos",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "grupo": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Número do grupo (ex: '1550')"
                                ),
                                "cota": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Número da cota (ex: '303')"
                                ),
                                "confirmar": genai.protos.Schema(
                                    type=genai.protos.Type.BOOLEAN,
                                    description="Se true, executa imediatamente. Se false, apenas simula"
                                )
                            },
                            required=["grupo", "cota"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="generate_boleto",
                        description="Gera um boleto no portal Servopa para um cliente específico",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "task_id": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="ID da tarefa do Todoist do boleto a gerar"
                                ),
                                "confirmar": genai.protos.Schema(
                                    type=genai.protos.Type.BOOLEAN,
                                    description="Se true, gera imediatamente. Se false, apenas verifica"
                                )
                            },
                            required=["task_id"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="send_whatsapp",
                        description="Envia mensagem via WhatsApp para um cliente específico do Todoist",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "task_id": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="ID da tarefa do Todoist do cliente"
                                ),
                                "confirmar": genai.protos.Schema(
                                    type=genai.protos.Type.BOOLEAN,
                                    description="Se true, envia imediatamente. Se false, apenas valida"
                                )
                            },
                            required=["task_id"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="search_boleto",
                        description="Busca um boleto específico por nome do cliente",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "nome": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Nome ou parte do nome do cliente"
                                )
                            },
                            required=["nome"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="search_lance",
                        description="Busca um lance específico por grupo, cota ou nome",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "query": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Termo de busca (grupo, cota ou nome)"
                                )
                            },
                            required=["query"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_system_status",
                        description="Retorna o status geral do sistema (automações rodando, últimas execuções, etc)",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={}
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="start_automation",
                        description="Inicia a automação completa do Dia 8 ou Dia 16 (login Servopa, extração Todoist, lances, notificações)",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "dia": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Qual automação iniciar: 'dia8' ou 'dia16'",
                                    enum=["dia8", "dia16"]
                                ),
                                "confirmar": genai.protos.Schema(
                                    type=genai.protos.Type.BOOLEAN,
                                    description="Se true, inicia imediatamente. Se false, apenas verifica status"
                                )
                            },
                            required=["dia"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="stop_automation",
                        description="Para a automação que está rodando no momento",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "dia": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Qual automação parar: 'dia8' ou 'dia16'",
                                    enum=["dia8", "dia16"]
                                )
                            },
                            required=["dia"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_automation_status",
                        description="Verifica se alguma automação está rodando no momento",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "dia": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Qual automação verificar: 'dia8', 'dia16' ou 'both'",
                                    enum=["dia8", "dia16", "both"]
                                )
                            },
                            required=["dia"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="send_whatsapp_custom",
                        description="Envia mensagem WhatsApp para qualquer número customizado (sem precisar estar no Todoist)",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "numero": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Número do WhatsApp com DDD (ex: 19995378302, 11987654321)"
                                ),
                                "mensagem": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Texto da mensagem a enviar"
                                ),
                                "confirmar": genai.protos.Schema(
                                    type=genai.protos.Type.BOOLEAN,
                                    description="Se true, envia imediatamente. Se false, apenas valida"
                                )
                            },
                            required=["numero", "mensagem"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="schedule_whatsapp",
                        description="Agenda uma mensagem WhatsApp para ser enviada em data/hora específica",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "numero": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Número do WhatsApp com DDD"
                                ),
                                "mensagem": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Texto da mensagem"
                                ),
                                "data_hora": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Data e hora no formato 'DD/MM/YYYY HH:MM' (ex: '07/10/2025 14:30')"
                                ),
                                "confirmar": genai.protos.Schema(
                                    type=genai.protos.Type.BOOLEAN,
                                    description="Se true, agenda imediatamente. Se false, apenas valida"
                                )
                            },
                            required=["numero", "mensagem", "data_hora"]
                        )
                    )
                ]
            )
        ]
        
    def _load_json_file(self, filename: str) -> Dict:
        """Carrega um arquivo JSON do projeto"""
        filepath = os.path.join(self.project_root, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_json_file(self, filename: str, data: Dict):
        """Salva dados em um arquivo JSON"""
        filepath = os.path.join(self.project_root, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_conversation_history(self):
        """Carrega histórico de conversa persistido"""
        history_file = os.path.join(self.project_root, 'data', 'ai_conversations', f'{self.session_id}.json')
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('messages', [])
            except Exception as e:
                print(f"Erro ao carregar histórico: {e}")
    
    def _save_conversation_history(self):
        """Salva histórico de conversa para persistir entre sessões"""
        history_dir = os.path.join(self.project_root, 'data', 'ai_conversations')
        os.makedirs(history_dir, exist_ok=True)
        
        history_file = os.path.join(history_dir, f'{self.session_id}.json')
        
        data = {
            'session_id': self.session_id,
            'last_updated': datetime.now().isoformat(),
            'messages': self.conversation_history
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register_callback(self, action_name: str, callback: Callable):
        """Registra um callback para executar ações reais (geração de boletos, lances, etc)"""
        self.callbacks[action_name] = callback
    
    # ========== IMPLEMENTAÇÃO DAS FERRAMENTAS ==========
    
    def get_boletos_stats(self, dia: str = "all") -> Dict[str, Any]:
        """Retorna estatísticas sobre boletos"""
        boletos_data = self._load_json_file('boletos_data.json')
        
        stats = {
            "dia": dia,
            "timestamp": datetime.now().isoformat()
        }
        
        def count_boletos(dia_key):
            boletos = boletos_data.get(dia_key, [])
            total = len(boletos)
            emitidos = sum(1 for b in boletos if b.get('png_base64') or b.get('boleto_url'))
            concluidos = sum(1 for b in boletos if b.get('is_completed'))
            return {
                "total": total,
                "emitidos": emitidos,
                "pendentes": total - emitidos,
                "concluidos": concluidos,
                "lista": [{"nome": b.get('nome'), "cotas": b.get('cotas'), "emitido": bool(b.get('png_base64') or b.get('boleto_url'))} for b in boletos[:5]]
            }
        
        if dia == "all":
            stats["dia08"] = count_boletos("dia08")
            stats["dia16"] = count_boletos("dia16")
            stats["total_geral"] = stats["dia08"]["total"] + stats["dia16"]["total"]
            stats["emitidos_geral"] = stats["dia08"]["emitidos"] + stats["dia16"]["emitidos"]
        else:
            dia_key = f"dia{dia}"
            stats["dados"] = count_boletos(dia_key)
        
        return stats
    
    def get_lances_stats(self, dia: str = "all") -> Dict[str, Any]:
        """Retorna estatísticas sobre lances"""
        lances_data = self._load_json_file('lances_data.json')
        
        stats = {
            "dia": dia,
            "timestamp": datetime.now().isoformat()
        }
        
        def count_lances(dia_key):
            grupos = lances_data.get(dia_key, [])
            total = 0
            concluidos = 0
            lances_list = []
            
            for grupo in grupos:
                tasks = grupo.get('tasks', [])
                total += len(tasks)
                concluidos += sum(1 for t in tasks if t.get('is_completed'))
                
                for task in tasks[:3]:  # Primeiros 3 de cada grupo
                    lances_list.append({
                        "grupo": grupo.get('grupo'),
                        "cota": task.get('cota'),
                        "nome": task.get('nome'),
                        "concluido": task.get('is_completed', False)
                    })
            
            return {
                "total": total,
                "concluidos": concluidos,
                "pendentes": total - concluidos,
                "grupos": len(grupos),
                "lista": lances_list[:10]
            }
        
        if dia == "all":
            stats["dia08"] = count_lances("dia08")
            stats["dia16"] = count_lances("dia16")
            stats["total_geral"] = stats["dia08"]["total"] + stats["dia16"]["total"]
            stats["concluidos_geral"] = stats["dia08"]["concluidos"] + stats["dia16"]["concluidos"]
        else:
            dia_key = f"dia{dia}"
            stats["dados"] = count_lances(dia_key)
        
        return stats
    
    def get_history(self, dia: str = "both", limit: int = 10) -> Dict[str, Any]:
        """Retorna histórico de execuções"""
        result = {
            "dia": dia,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
        if dia == "both":
            history_dia8 = self._load_json_file('history_dia8.json')
            history_dia16 = self._load_json_file('history_dia16.json')
            
            result["dia8"] = {
                "total": len(history_dia8),
                "ultimos": list(reversed(history_dia8[-limit:]))
            }
            result["dia16"] = {
                "total": len(history_dia16),
                "ultimos": list(reversed(history_dia16[-limit:]))
            }
        else:
            history = self._load_json_file(f'history_{dia}.json')
            result["dados"] = {
                "total": len(history),
                "ultimos": list(reversed(history[-limit:]))
            }
        
        return result
    
    def execute_lance(self, grupo: str, cota: str, confirmar: bool = False) -> Dict[str, Any]:
        """Executa um lance (ou simula se confirmar=False)"""
        if not confirmar:
            return {
                "success": True,
                "simulated": True,
                "message": f"Simulação: Lance seria executado para Grupo {grupo}, Cota {cota}",
                "grupo": grupo,
                "cota": cota,
                "warning": "Para executar de verdade, use confirmar=True"
            }
        
        # EXECUÇÃO REAL via callback registrado
        if 'execute_lance' in self.callbacks:
            try:
                result = self.callbacks['execute_lance'](grupo, cota)
                return {
                    "success": True,
                    "executed": True,
                    "message": f"Lance executado com sucesso! Grupo {grupo}, Cota {cota}",
                    "grupo": grupo,
                    "cota": cota,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao executar lance: {str(e)}",
                    "grupo": grupo,
                    "cota": cota
                }
        
        # Fallback se não há callback
        return {
            "success": False,
            "error": "Execução direta de lances ainda não implementada. Use a interface web para executar automações.",
            "grupo": grupo,
            "cota": cota
        }
    
    def generate_boleto(self, task_id: str, confirmar: bool = False) -> Dict[str, Any]:
        """Gera um boleto (ou verifica se confirmar=False)"""
        boletos_data = self._load_json_file('boletos_data.json')
        
        # Busca o boleto
        boleto = None
        dia = None
        
        for d in ["dia08", "dia16"]:
            for b in boletos_data.get(d, []):
                if str(b.get('task_id')) == str(task_id):
                    boleto = b
                    dia = d
                    break
            if boleto:
                break
        
        if not boleto:
            return {
                "success": False,
                "error": f"Boleto com task_id {task_id} não encontrado"
            }
        
        if not confirmar:
            return {
                "success": True,
                "simulated": True,
                "message": f"Simulação: Boleto seria gerado para {boleto.get('nome')}",
                "boleto": {
                    "nome": boleto.get('nome'),
                    "cotas": boleto.get('cotas'),
                    "dia": dia,
                    "ja_emitido": bool(boleto.get('png_base64') or boleto.get('boleto_url'))
                },
                "warning": "Para gerar de verdade, use confirmar=True"
            }
        
        # EXECUÇÃO REAL via callback registrado
        if 'generate_boleto' in self.callbacks:
            try:
                result = self.callbacks['generate_boleto'](task_id, dia)
                return {
                    "success": True,
                    "executed": True,
                    "message": f"Boleto gerado com sucesso para {boleto.get('nome')}!",
                    "boleto": {
                        "nome": boleto.get('nome'),
                        "task_id": task_id,
                        "dia": dia
                    },
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao gerar boleto: {str(e)}",
                    "boleto": {
                        "nome": boleto.get('nome'),
                        "task_id": task_id
                    }
                }
        
        # Fallback se não há callback
        return {
            "success": False,
            "error": "Geração direta de boletos ainda não implementada. Use a interface web.",
            "boleto": {
                "nome": boleto.get('nome'),
                "task_id": task_id
            }
        }
    
    def send_whatsapp(self, task_id: str, confirmar: bool = False) -> Dict[str, Any]:
        """Envia WhatsApp (ou valida se confirmar=False)"""
        boletos_data = self._load_json_file('boletos_data.json')
        
        # Busca o boleto
        boleto = None
        
        for d in ["dia08", "dia16"]:
            for b in boletos_data.get(d, []):
                if str(b.get('task_id')) == str(task_id):
                    boleto = b
                    break
            if boleto:
                break
        
        if not boleto:
            return {
                "success": False,
                "error": f"Boleto com task_id {task_id} não encontrado"
            }
        
        if not confirmar:
            return {
                "success": True,
                "simulated": True,
                "message": f"Simulação: WhatsApp seria enviado para {boleto.get('nome')}",
                "boleto": {
                    "nome": boleto.get('nome'),
                    "celular": boleto.get('celular'),
                    "tem_boleto": bool(boleto.get('png_base64') or boleto.get('boleto_url'))
                },
                "warning": "Para enviar de verdade, use confirmar=True"
            }
        
        # TODO: Implementar envio real via Evolution API
        return {
            "success": False,
            "error": "Envio direto de WhatsApp ainda não implementado. Use a interface web.",
            "boleto": {
                "nome": boleto.get('nome'),
                "task_id": task_id
            }
        }
    
    def search_boleto(self, nome: str) -> Dict[str, Any]:
        """Busca boletos por nome"""
        boletos_data = self._load_json_file('boletos_data.json')
        nome_lower = nome.lower()
        
        results = []
        
        for dia in ["dia08", "dia16"]:
            for boleto in boletos_data.get(dia, []):
                if nome_lower in boleto.get('nome', '').lower():
                    results.append({
                        "task_id": boleto.get('task_id'),
                        "nome": boleto.get('nome'),
                        "cotas": boleto.get('cotas'),
                        "celular": boleto.get('celular'),
                        "dia": dia,
                        "emitido": bool(boleto.get('png_base64') or boleto.get('boleto_url')),
                        "concluido": boleto.get('is_completed', False)
                    })
        
        return {
            "success": True,
            "query": nome,
            "total": len(results),
            "results": results
        }
    
    def search_lance(self, query: str) -> Dict[str, Any]:
        """Busca lances por grupo, cota ou nome"""
        lances_data = self._load_json_file('lances_data.json')
        query_lower = query.lower()
        
        results = []
        
        for dia in ["dia08", "dia16"]:
            for grupo in lances_data.get(dia, []):
                grupo_nome = grupo.get('grupo', '')
                
                for task in grupo.get('tasks', []):
                    cota = str(task.get('cota', ''))
                    nome = task.get('nome', '')
                    
                    if (query_lower in grupo_nome.lower() or 
                        query_lower in cota.lower() or 
                        query_lower in nome.lower()):
                        
                        results.append({
                            "task_id": task.get('task_id'),
                            "grupo": grupo_nome,
                            "cota": cota,
                            "nome": nome,
                            "dia": dia,
                            "concluido": task.get('is_completed', False)
                        })
        
        return {
            "success": True,
            "query": query,
            "total": len(results),
            "results": results[:20]  # Limita a 20 resultados
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status geral do sistema"""
        boletos_stats = self.get_boletos_stats("all")
        lances_stats = self.get_lances_stats("all")
        history_dia8 = self._load_json_file('history_dia8.json')
        history_dia16 = self._load_json_file('history_dia16.json')
        
        # Última execução
        last_execution = None
        if history_dia8:
            last_execution = history_dia8[-1]
        elif history_dia16:
            last_execution = history_dia16[-1]
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "boletos": {
                "total": boletos_stats.get("total_geral", 0),
                "emitidos": boletos_stats.get("emitidos_geral", 0),
                "pendentes": boletos_stats.get("total_geral", 0) - boletos_stats.get("emitidos_geral", 0)
            },
            "lances": {
                "total": lances_stats.get("total_geral", 0),
                "concluidos": lances_stats.get("concluidos_geral", 0),
                "pendentes": lances_stats.get("total_geral", 0) - lances_stats.get("concluidos_geral", 0)
            },
            "historico": {
                "total_execucoes_dia8": len(history_dia8),
                "total_execucoes_dia16": len(history_dia16),
                "ultima_execucao": last_execution
            }
        }
    
    def start_automation(self, dia: str, confirmar: bool = False) -> Dict[str, Any]:
        """Inicia automação do Dia 8 ou Dia 16"""
        if not confirmar:
            return {
                "success": True,
                "simulated": True,
                "message": f"Simulação: Automação {dia} seria iniciada",
                "dia": dia,
                "warning": "Para iniciar de verdade, confirme a execução"
            }
        
        # EXECUÇÃO REAL via callback registrado
        if 'start_automation' in self.callbacks:
            try:
                result = self.callbacks['start_automation'](dia)
                return {
                    "success": True,
                    "executed": True,
                    "message": f"Automação {dia} iniciada com sucesso!",
                    "dia": dia,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao iniciar automação: {str(e)}",
                    "dia": dia
                }
        
        # Fallback se não há callback
        return {
            "success": False,
            "error": "Iniciar automação via IA ainda não está implementado. Use a interface web.",
            "dia": dia
        }
    
    def stop_automation(self, dia: str) -> Dict[str, Any]:
        """Para automação rodando"""
        # EXECUÇÃO REAL via callback registrado
        if 'stop_automation' in self.callbacks:
            try:
                result = self.callbacks['stop_automation'](dia)
                return {
                    "success": True,
                    "executed": True,
                    "message": f"Automação {dia} parada com sucesso!",
                    "dia": dia,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao parar automação: {str(e)}",
                    "dia": dia
                }
        
        # Fallback se não há callback
        return {
            "success": False,
            "error": "Parar automação via IA ainda não está implementado. Use a interface web.",
            "dia": dia
        }
    
    def get_automation_status(self, dia: str = "both") -> Dict[str, Any]:
        """Verifica status das automações"""
        # EXECUÇÃO REAL via callback registrado
        if 'get_automation_status' in self.callbacks:
            try:
                result = self.callbacks['get_automation_status'](dia)
                return {
                    "success": True,
                    "dia": dia,
                    "status": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao verificar status: {str(e)}",
                    "dia": dia
                }
        
        # Fallback se não há callback
        return {
            "success": True,
            "dia": dia,
            "status": {
                "dia8_running": False,
                "dia16_running": False,
                "message": "Status não disponível via IA"
            }
        }
    
    def send_whatsapp_custom(self, numero: str, mensagem: str, confirmar: bool = False) -> Dict[str, Any]:
        """Envia WhatsApp para qualquer número (sem precisar estar no Todoist)"""
        # Se não confirmar, só valida
        if not confirmar:
            return {
                "success": True,
                "executed": False,
                "numero": numero,
                "mensagem": mensagem[:100] + "..." if len(mensagem) > 100 else mensagem,
                "message": f"📱 Pronto para enviar WhatsApp para {numero}. Confirme para enviar."
            }
        
        # EXECUÇÃO REAL via callback registrado
        if 'send_whatsapp_custom' in self.callbacks:
            try:
                result = self.callbacks['send_whatsapp_custom'](numero, mensagem)
                return {
                    "success": True,
                    "executed": True,
                    "message": f"✅ WhatsApp enviado para {numero}!",
                    "numero": numero,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao enviar WhatsApp: {str(e)}",
                    "numero": numero
                }
        
        # Fallback se não há callback
        return {
            "success": False,
            "error": "Envio de WhatsApp customizado não está configurado",
            "numero": numero
        }
    
    def schedule_whatsapp(self, numero: str, mensagem: str, data_hora: str, confirmar: bool = False) -> Dict[str, Any]:
        """Agenda mensagem WhatsApp para data/hora específica"""
        # Se não confirmar, só valida
        if not confirmar:
            return {
                "success": True,
                "executed": False,
                "numero": numero,
                "mensagem": mensagem[:100] + "..." if len(mensagem) > 100 else mensagem,
                "data_hora": data_hora,
                "message": f"📅 Pronto para agendar WhatsApp para {numero} em {data_hora}. Confirme para agendar."
            }
        
        # EXECUÇÃO REAL via callback registrado
        if 'schedule_whatsapp' in self.callbacks:
            try:
                result = self.callbacks['schedule_whatsapp'](numero, mensagem, data_hora)
                return {
                    "success": True,
                    "executed": True,
                    "message": f"✅ WhatsApp agendado para {numero} em {data_hora}!",
                    "numero": numero,
                    "data_hora": data_hora,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro ao agendar WhatsApp: {str(e)}",
                    "numero": numero,
                    "data_hora": data_hora
                }
        
        # Fallback se não há callback
        return {
            "success": False,
            "error": "Agendamento de WhatsApp não está configurado",
            "numero": numero,
            "data_hora": data_hora
        }
    
    def _execute_function(self, function_name: str, arguments: Dict) -> Dict[str, Any]:
        """Executa uma função do agente"""
        function_map = {
            "get_boletos_stats": self.get_boletos_stats,
            "get_lances_stats": self.get_lances_stats,
            "get_history": self.get_history,
            "execute_lance": self.execute_lance,
            "generate_boleto": self.generate_boleto,
            "send_whatsapp": self.send_whatsapp,
            "search_boleto": self.search_boleto,
            "search_lance": self.search_lance,
            "get_system_status": self.get_system_status,
            "start_automation": self.start_automation,
            "stop_automation": self.stop_automation,
            "get_automation_status": self.get_automation_status,
            "send_whatsapp_custom": self.send_whatsapp_custom,
            "schedule_whatsapp": self.schedule_whatsapp
        }
        
        if function_name not in function_map:
            return {"error": f"Função {function_name} não encontrada"}
        
        try:
            return function_map[function_name](**arguments)
        except Exception as e:
            return {"error": f"Erro ao executar {function_name}: {str(e)}"}
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Envia uma mensagem para o agente e recebe resposta
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            Dict com resposta do agente e ações executadas
        """
        # System prompt com contexto do sistema
        system_prompt = """Você é o OXCASH AI Assistant, um assistente inteligente especializado em automação de consórcios.

🎯 VOCÊ DEVE EXECUTAR AÇÕES AUTOMATICAMENTE QUANDO O USUÁRIO PEDIR:

📊 QUANDO O USUÁRIO PERGUNTAR SOBRE DADOS, CHAME AS FUNÇÕES:
- "quantos boletos" → CHAME get_boletos_stats(dia="all")
- "quantos lances" → CHAME get_lances_stats(dia="all")
- "status do sistema" → CHAME get_system_status()
- "histórico" → CHAME get_history(dia="both", limit=10)

🔍 QUANDO O USUÁRIO BUSCAR ALGUÉM, CHAME AS FUNÇÕES:
- "procure João" → CHAME search_boleto(nome="João")
- "buscar grupo 1550" → CHAME search_lance(query="1550")

📱 QUANDO O USUÁRIO PEDIR PRA ENVIAR WHATSAPP:
- "envie whatsapp para 19995378302" → PERGUNTE qual mensagem
- "envie whatsapp para 19995378302 dizendo oi" → CHAME send_whatsapp_custom(numero="19995378302", mensagem="oi", confirmar=False) PRIMEIRO
- Se usuário CONFIRMAR com "sim", "confirma", "pode enviar" → CHAME send_whatsapp_custom(numero="19995378302", mensagem="oi", confirmar=True)

🚀 QUANDO O USUÁRIO PEDIR PRA INICIAR AUTOMAÇÃO:
- "inicie a automação do dia 8" → CHAME start_automation(dia="dia8", confirmar=False) PRIMEIRO
- Se usuário CONFIRMAR com "sim", "confirma", "pode iniciar" → CHAME start_automation(dia="dia8", confirmar=True)
- "pare a automação" → CHAME stop_automation(dia="dia8" ou "dia16")

⚡ REGRAS CRÍTICAS DE EXECUÇÃO:

1. SEMPRE CHAME AS FUNÇÕES quando o usuário pedir uma ação
2. Para ações DESTRUTIVAS (enviar WhatsApp, iniciar automação), primeiro chame com confirmar=False
3. Quando usuário responder "sim", "confirma", "pode", OLHE NO HISTÓRICO qual foi a última ação aguardando confirmação e chame ela com confirmar=True
4. NÃO peça informações que você já tem nos argumentos da função
5. NÃO fique fazendo perguntas em loop, EXECUTE as funções
6. Se usuário disser "envie whatsapp para 19995378302 dizendo oi", você JÁ TEM numero E mensagem, chame a função!
7. IMPORTANTE: Quando usuário disser apenas "sim", "confirma" ou "pode", você DEVE olhar o histórico da conversa e chamar a MESMA função que pediu confirmação, mas agora com confirmar=True

EXEMPLOS DE COMO AGIR:

Usuário: "quantos boletos foram emitidos?"
Você: [CHAMA get_boletos_stats(dia="all")] → "Foram emitidos 25 boletos no total! 📊"

Usuário: "procure Marcus Correa"
Você: [CHAMA search_boleto(nome="Marcus Correa")] → "Encontrei 2 boletos para Marcus Correa! 🔍"

Usuário: "envie whatsapp para 19995378302 dizendo oi"
Você: [CHAMA send_whatsapp_custom(numero="19995378302", mensagem="oi", confirmar=False)] → "📱 Pronto para enviar 'oi' para 19995378302. Confirma?"

Usuário: "sim"
Você: [OLHA O HISTÓRICO, vê que a última função foi send_whatsapp_custom] → [CHAMA send_whatsapp_custom(numero="19995378302", mensagem="oi", confirmar=True)] → "✅ WhatsApp enviado com sucesso!"

Usuário: "inicie a automação do dia 8"
Você: [CHAMA start_automation(dia="dia8", confirmar=False)] → "🚀 Pronto para iniciar automação do dia 8. Confirma?"

Usuário: "sim"
Você: [OLHA O HISTÓRICO, vê que a última função foi start_automation] → [CHAMA start_automation(dia="dia8", confirmar=True)] → "✅ Automação do dia 8 iniciada!"

SEJA PROATIVO E EXECUTE AS FUNÇÕES! Não fique pedindo informações desnecessárias."""

        try:
            # Converte histórico para formato do Gemini
            gemini_history = []
            
            # Adiciona system prompt como primeira mensagem do usuário + resposta do modelo
            if not self.conversation_history:
                gemini_history.append({
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                })
                gemini_history.append({
                    "role": "model",
                    "parts": [{"text": "Entendido! Estou pronto para ajudar. Posso consultar boletos, lances, executar automações e enviar WhatsApp. O que você precisa?"}]
                })
            
            # Adiciona histórico das últimas mensagens
            for msg in self.conversation_history[-10:]:  # Últimas 10 mensagens para contexto
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # Cria chat session COM histórico para manter contexto
            chat = self.model.start_chat(history=gemini_history)
            
            # Envia mensagem com ferramentas disponíveis
            response = chat.send_message(
                user_message,
                tools=self.tools
            )
            
            # Verifica se há function calls
            actions_executed = []
            
            while response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                # Se tem function call, executa
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    # Executa a função
                    function_response = self._execute_function(function_name, function_args)
                    
                    actions_executed.append({
                        "function": function_name,
                        "arguments": function_args,
                        "result": function_response
                    })
                    
                    # Envia resultado de volta para o modelo
                    response = chat.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={'result': function_response}
                            )
                        )
                    )
                else:
                    # Tem resposta de texto
                    break
            
            # Pega resposta final
            final_message = response.text
            
            # Salva no histórico
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": final_message
            })
            
            # Salva histórico
            self._save_conversation_history()
            
            return {
                "success": True,
                "message": final_message,
                "actions": actions_executed
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro no chat Gemini: {error_details}")
            return {
                "success": False,
                "error": f"Erro ao processar mensagem: {str(e)}",
                "message": "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
            }
    
    def reset_conversation(self):
        """Limpa o histórico da conversa"""
        self.conversation_history = []
        self._save_conversation_history()


# ========== TESTE DO MÓDULO ==========

if __name__ == "__main__":
    import sys
    
    # Token do Google Gemini (gratuito!)
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = "AIzaSyCbXLz7HBma76AsPYBr9S-bNmM3LvnlM7k"
    
    agent = OXCASHAgent(api_key)
    
    print("=" * 60)
    print("🤖 OXCASH AI Assistant - Teste (Google Gemini)")
    print("=" * 60)
    print()
    
    # Teste 1: Status do sistema
    print("📊 Teste 1: Status do sistema")
    response = agent.chat("Qual o status geral do sistema?")
    print(f"Resposta: {response['message']}")
    print()
    
    # Teste 2: Estatísticas de boletos
    print("📄 Teste 2: Boletos emitidos")
    response = agent.chat("Quantos boletos foram emitidos hoje?")
    print(f"Resposta: {response['message']}")
    print()
    
    # Teste 3: Busca
    print("🔍 Teste 3: Buscar cliente")
    response = agent.chat("Procure informações sobre o cliente 'João'")
    print(f"Resposta: {response['message']}")
    print()
    
    print("=" * 60)
    print("✅ Testes concluídos")
    print("=" * 60)
    response = agent.chat("Quantos boletos foram emitidos hoje?")
    print(f"Resposta: {response['message']}")
    print()
    
    # Teste 3: Busca
    print("🔍 Teste 3: Buscar cliente")
    response = agent.chat("Procure informações sobre o cliente 'João'")
    print(f"Resposta: {response['message']}")
    print()
    
    print("=" * 60)
    print("✅ Testes concluídos")
    print("=" * 60)
