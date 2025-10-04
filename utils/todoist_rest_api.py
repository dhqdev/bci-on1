"""
Módulo para interação com Todoist REST API
Documentação: https://developer.todoist.com/rest/v2
"""

import requests
from typing import Dict, List, Optional

class TodoistRestAPI:
    """Cliente para Todoist REST API"""
    
    BASE_URL = "https://api.todoist.com/rest/v2"
    
    def __init__(self, token: str):
        """
        Inicializa o cliente da API
        
        Args:
            token: Token de autenticação do Todoist
        """
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_projects(self) -> List[Dict]:
        """
        Obtém todos os projetos
        
        Returns:
            Lista de projetos
        """
        url = f"{self.BASE_URL}/projects"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_project_by_name(self, name: str) -> Optional[Dict]:
        """
        Busca um projeto pelo nome
        
        Args:
            name: Nome do projeto
            
        Returns:
            Dados do projeto ou None se não encontrado
        """
        projects = self.get_projects()
        for project in projects:
            if project.get('name') == name:
                return project
        return None
    
    def get_sections(self, project_id: str) -> List[Dict]:
        """
        Obtém todas as seções de um projeto
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Lista de seções
        """
        url = f"{self.BASE_URL}/sections"
        params = {"project_id": project_id}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_tasks(self, project_id: Optional[str] = None, section_id: Optional[str] = None) -> List[Dict]:
        """
        Obtém tarefas de um projeto ou seção
        
        Args:
            project_id: ID do projeto (opcional)
            section_id: ID da seção (opcional)
            
        Returns:
            Lista de tarefas
        """
        url = f"{self.BASE_URL}/tasks"
        params = {}
        
        if project_id:
            params['project_id'] = project_id
        if section_id:
            params['section_id'] = section_id
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict:
        """
        Obtém uma tarefa específica
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Dados da tarefa
        """
        url = f"{self.BASE_URL}/tasks/{task_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def close_task(self, task_id: str) -> bool:
        """
        Marca uma tarefa como concluída
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            True se sucesso
        """
        url = f"{self.BASE_URL}/tasks/{task_id}/close"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        # close_task retorna 204 No Content em sucesso
        return response.status_code == 204
    
    def reopen_task(self, task_id: str) -> bool:
        """
        Reabre uma tarefa concluída
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            True se sucesso (retorna 204 No Content)
        """
        url = f"{self.BASE_URL}/tasks/{task_id}/reopen"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        # reopen_task retorna 204 No Content em sucesso
        return response.status_code == 204
    
    def extract_boletos_board(self, project_name: str = "Boletos Servopa Outubro", 
                            section_dia08: str = "Vencimento dia 08",
                            section_dia16: str = "Vencimento dia 16",
                            progress_callback=None) -> Dict:
        """
        Extrai dados do board de boletos via API REST
        
        Args:
            project_name: Nome do projeto
            section_dia08: Nome da seção dia 08
            section_dia16: Nome da seção dia 16
            progress_callback: Função para reportar progresso
            
        Returns:
            Dict com estrutura: {'dia08': [...], 'dia16': [...]}
        """
        try:
            if progress_callback:
                progress_callback("🔍 Buscando projeto no Todoist...")
            
            # Busca projeto
            project = self.get_project_by_name(project_name)
            if not project:
                raise Exception(f"Projeto '{project_name}' não encontrado")
            
            project_id = project['id']
            
            if progress_callback:
                progress_callback(f"✅ Projeto encontrado: {project_name}")
                progress_callback("📂 Buscando seções...")
            
            # Busca seções
            sections = self.get_sections(project_id)
            
            section_dia08_id = None
            section_dia16_id = None
            
            for section in sections:
                if section['name'] == section_dia08:
                    section_dia08_id = section['id']
                elif section['name'] == section_dia16:
                    section_dia16_id = section['id']
            
            if not section_dia08_id:
                raise Exception(f"Seção '{section_dia08}' não encontrada")
            if not section_dia16_id:
                raise Exception(f"Seção '{section_dia16}' não encontrada")
            
            if progress_callback:
                progress_callback("✅ Seções encontradas")
                progress_callback("📋 Extraindo tarefas...")
            
            # Extrai tarefas de cada seção
            tasks_dia08 = self.get_tasks(project_id=project_id, section_id=section_dia08_id)
            tasks_dia16 = self.get_tasks(project_id=project_id, section_id=section_dia16_id)
            
            # Formata dados
            boletos_dia08 = []
            for task in tasks_dia08:
                boletos_dia08.append({
                    'nome': task['content'],
                    'cotas': task.get('description', ''),
                    'task_id': task['id'],
                    'is_completed': task.get('is_completed', False)
                })
            
            boletos_dia16 = []
            for task in tasks_dia16:
                boletos_dia16.append({
                    'nome': task['content'],
                    'cotas': task.get('description', ''),
                    'task_id': task['id'],
                    'is_completed': task.get('is_completed', False)
                })
            
            if progress_callback:
                progress_callback(f"✅ Extraídos {len(boletos_dia08)} boletos (dia 08) e {len(boletos_dia16)} boletos (dia 16)")
            
            return {
                'dia08': boletos_dia08,
                'dia16': boletos_dia16
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erro HTTP na API do Todoist: {e}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Erro ao extrair boletos: {e}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def extract_lances_board(self, project_dia8: str = "Lances Servopa Outubro Dia 8",
                            project_dia16: str = "Lances Servopa Outubro Dia 16",
                            progress_callback=None) -> Dict:
        """
        Extrai dados dos boards de lances do Servopa via API REST.
        Organiza por grupos (colunas/seções) e cotas (tarefas).
        
        Args:
            project_dia8: Nome do projeto do dia 8
            project_dia16: Nome do projeto do dia 16
            progress_callback: Função para reportar progresso
            
        Returns:
            Dict com estrutura: {
                'dia08': [
                    {
                        'grupo': '1550',
                        'title': '1550 - dia 8',
                        'tasks': [
                            {
                                'cota': '1874',
                                'nome': 'Gil Zanobia',
                                'task_id': 'xxx',
                                'is_completed': False
                            },
                            ...
                        ]
                    },
                    ...
                ],
                'dia16': [...]
            }
        """
        try:
            result = {'dia08': [], 'dia16': []}
            
            # Processa dia 8
            if progress_callback:
                progress_callback(f"🔍 Buscando projeto '{project_dia8}'...")
            
            project_8 = self.get_project_by_name(project_dia8)
            if project_8:
                if progress_callback:
                    progress_callback(f"✅ Projeto encontrado: {project_dia8}")
                    progress_callback("📂 Buscando seções (grupos)...")
                
                sections_8 = self.get_sections(project_8['id'])
                
                for section in sections_8:
                    section_title = section['name']
                    
                    # Extrai número do grupo (primeiro número do título)
                    import re
                    grupo_match = re.match(r'(\d+)', section_title)
                    grupo_number = grupo_match.group(1) if grupo_match else section_title
                    
                    if progress_callback:
                        progress_callback(f"📂 Processando grupo: {section_title}")
                    
                    # Busca tarefas da seção
                    tasks = self.get_tasks(project_id=project_8['id'], section_id=section['id'])
                    
                    tasks_list = []
                    for task in tasks:
                        # Extrai cota (content) e nome (description)
                        cota = task['content']
                        nome = task.get('description', 'Sem nome')
                        
                        tasks_list.append({
                            'cota': cota,
                            'nome': nome,
                            'task_id': task['id'],
                            'is_completed': task.get('is_completed', False)
                        })
                    
                    result['dia08'].append({
                        'grupo': grupo_number,
                        'title': section_title,
                        'tasks': tasks_list
                    })
                    
                    if progress_callback:
                        progress_callback(f"   └─ {len(tasks_list)} cotas encontradas")
            else:
                if progress_callback:
                    progress_callback(f"⚠️ Projeto '{project_dia8}' não encontrado")
            
            # Processa dia 16
            if progress_callback:
                progress_callback(f"🔍 Buscando projeto '{project_dia16}'...")
            
            project_16 = self.get_project_by_name(project_dia16)
            if project_16:
                if progress_callback:
                    progress_callback(f"✅ Projeto encontrado: {project_dia16}")
                    progress_callback("📂 Buscando seções (grupos)...")
                
                sections_16 = self.get_sections(project_16['id'])
                
                for section in sections_16:
                    section_title = section['name']
                    
                    # Extrai número do grupo
                    import re
                    grupo_match = re.match(r'(\d+)', section_title)
                    grupo_number = grupo_match.group(1) if grupo_match else section_title
                    
                    if progress_callback:
                        progress_callback(f"📂 Processando grupo: {section_title}")
                    
                    # Busca tarefas da seção
                    tasks = self.get_tasks(project_id=project_16['id'], section_id=section['id'])
                    
                    tasks_list = []
                    for task in tasks:
                        cota = task['content']
                        nome = task.get('description', 'Sem nome')
                        
                        tasks_list.append({
                            'cota': cota,
                            'nome': nome,
                            'task_id': task['id'],
                            'is_completed': task.get('is_completed', False)
                        })
                    
                    result['dia16'].append({
                        'grupo': grupo_number,
                        'title': section_title,
                        'tasks': tasks_list
                    })
                    
                    if progress_callback:
                        progress_callback(f"   └─ {len(tasks_list)} cotas encontradas")
            else:
                if progress_callback:
                    progress_callback(f"⚠️ Projeto '{project_dia16}' não encontrado")
            
            # Resumo
            total_grupos_8 = len(result['dia08'])
            total_cotas_8 = sum(len(g['tasks']) for g in result['dia08'])
            total_grupos_16 = len(result['dia16'])
            total_cotas_16 = sum(len(g['tasks']) for g in result['dia16'])
            
            if progress_callback:
                progress_callback(f"✅ Dia 08: {total_grupos_8} grupos, {total_cotas_8} cotas")
                progress_callback(f"✅ Dia 16: {total_grupos_16} grupos, {total_cotas_16} cotas")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erro HTTP na API do Todoist: {e}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Erro ao extrair lances: {e}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            raise Exception(error_msg)
