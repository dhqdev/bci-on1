# utils/todoist_board_extractor.py
# Extrator completo de boards do Todoist (todas as colunas e linhas)

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

TIMEOUT = 20

def extract_complete_board(driver, progress_callback=None):
    """
    Extrai TODAS as colunas (seções) e TODAS as tarefas (linhas) do board do Todoist
    
    Estrutura retornada:
    {
        'sections': [
            {
                'grupo': '1550',  # Número do grupo (extraído do título da seção)
                'title': '1550 - dia 8',  # Título completo
                'tasks': [
                    {
                        'cota': '1874',  # Número da cota
                        'nome': 'Gil Zanobia',  # Nome do cliente
                        'task_id': 'task-6cwXP9X7FfPJJwr4',  # ID único da tarefa
                        'checkbox_element': <WebElement>  # Elemento do checkbox para marcar depois
                    },
                    ...
                ]
            },
            ...
        ]
    }
    
    Args:
        driver: Instância do WebDriver já na página do board
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: Estrutura completa do board ou None se falhar
    """
    try:
        if progress_callback:
            progress_callback("📊 Extraindo estrutura completa do board...")
        
        wait = WebDriverWait(driver, TIMEOUT)
        
        # Aguarda carregamento completo do board
        time.sleep(3)
        
        # Localiza todas as seções (colunas)
        if progress_callback:
            progress_callback("🔍 Localizando todas as colunas (seções)...")
        
        sections = driver.find_elements(By.CSS_SELECTOR, "section.board_section")
        
        if not sections:
            if progress_callback:
                progress_callback("❌ Nenhuma seção encontrada no board")
            return None
        
        if progress_callback:
            progress_callback(f"📋 Encontradas {len(sections)} colunas no board")
        
        board_data = {'sections': []}
        
        # Processa cada seção (coluna)
        for section_index, section in enumerate(sections, 1):
            try:
                # Extrai título da seção
                header = section.find_element(By.CSS_SELECTOR, "header.board_section__header")
                title_element = header.find_element(By.CSS_SELECTOR, "h3.board_section__title span.simple_content")
                section_title = title_element.text.strip()
                
                if progress_callback:
                    progress_callback(f"📂 Coluna {section_index}: '{section_title}'")
                
                # Extrai número do grupo (primeiro número do título)
                grupo_match = re.match(r'(\d+)', section_title)
                grupo_number = grupo_match.group(1) if grupo_match else None
                
                if not grupo_number:
                    if progress_callback:
                        progress_callback(f"⚠️ Coluna '{section_title}' não contém número de grupo, pulando...")
                    continue
                
                # Extrai todas as tarefas (linhas) desta seção
                task_list = section.find_element(By.CSS_SELECTOR, "div.board_section__task_list")
                tasks = task_list.find_elements(By.CSS_SELECTOR, "div.board_task")
                
                if progress_callback:
                    progress_callback(f"   └─ {len(tasks)} tarefas encontradas")
                
                section_data = {
                    'grupo': grupo_number,
                    'title': section_title,
                    'tasks': []
                }
                
                # Processa cada tarefa (linha)
                for task_index, task in enumerate(tasks, 1):
                    try:
                        # ID da tarefa
                        task_id = task.get_attribute('id')
                        
                        # Extrai número da cota (task_content)
                        cota_element = task.find_element(By.CSS_SELECTOR, "div.task_content")
                        cota = cota_element.text.strip()
                        
                        # Extrai nome do cliente (task_description)
                        try:
                            nome_element = task.find_element(By.CSS_SELECTOR, "div.task_description p")
                            nome = nome_element.text.strip()
                        except NoSuchElementException:
                            nome = "Sem nome"
                        
                        # Localiza checkbox para marcar depois
                        checkbox = task.find_element(By.CSS_SELECTOR, "button.task_checkbox")
                        
                        task_data = {
                            'cota': cota,
                            'nome': nome,
                            'task_id': task_id,
                            'checkbox_element': checkbox
                        }
                        
                        section_data['tasks'].append(task_data)
                        
                        if progress_callback:
                            progress_callback(f"      └─ Tarefa {task_index}: Cota {cota} - {nome}")
                        
                    except Exception as task_error:
                        if progress_callback:
                            progress_callback(f"⚠️ Erro ao processar tarefa {task_index}: {task_error}")
                        continue
                
                # Adiciona seção ao board data
                if section_data['tasks']:
                    board_data['sections'].append(section_data)
                
            except Exception as section_error:
                if progress_callback:
                    progress_callback(f"⚠️ Erro ao processar coluna {section_index}: {section_error}")
                continue
        
        # Resumo final
        total_tasks = sum(len(section['tasks']) for section in board_data['sections'])
        if progress_callback:
            progress_callback(f"✅ Extração completa: {len(board_data['sections'])} colunas, {total_tasks} tarefas")
        
        return board_data
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro na extração do board: {e}")
        return None


def mark_task_completed(driver, checkbox_element, progress_callback=None):
    """
    Marca uma tarefa como concluída clicando no checkbox
    
    Args:
        driver: Instância do WebDriver
        checkbox_element: Elemento do checkbox a ser clicado
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se marcado com sucesso
    """
    try:
        if progress_callback:
            progress_callback("✅ Marcando tarefa como concluída...")
        
        # Rola até o elemento para garantir que está visível
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_element)
        time.sleep(0.5)
        
        # Clica no checkbox
        checkbox_element.click()
        time.sleep(1)  # Aguarda animação
        
        if progress_callback:
            progress_callback("✅ Tarefa marcada como concluída no Todoist")
        
        return True
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao marcar tarefa: {e}")
        return False


def mark_all_section_tasks_completed(driver, section_title, progress_callback=None):
    """
    Marca TODAS as tarefas de uma seção (coluna) como concluídas
    
    Esta função re-localiza a seção no DOM e marca todos os checkboxes não marcados.
    Útil para garantir que todas as tarefas foram marcadas ao final de uma coluna.
    
    Args:
        driver: Instância do WebDriver
        section_title: Título da seção para localizar
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        int: Quantidade de checkboxes marcados
    """
    try:
        if progress_callback:
            progress_callback(f"🔄 Marcando TODOS os checkboxes da coluna '{section_title}'...")
        
        time.sleep(2)  # Aguarda página atualizar
        
        # Localiza todas as seções novamente
        sections = driver.find_elements(By.CSS_SELECTOR, "section.board_section")
        
        target_section = None
        for section in sections:
            try:
                header = section.find_element(By.CSS_SELECTOR, "header.board_section__header")
                title_element = header.find_element(By.CSS_SELECTOR, "h3.board_section__title span.simple_content")
                current_title = title_element.text.strip()
                
                if current_title == section_title:
                    target_section = section
                    break
            except:
                continue
        
        if not target_section:
            if progress_callback:
                progress_callback(f"⚠️ Seção '{section_title}' não encontrada")
            return 0
        
        # Localiza todas as tarefas desta seção
        task_list = target_section.find_element(By.CSS_SELECTOR, "div.board_section__task_list")
        checkboxes = task_list.find_elements(By.CSS_SELECTOR, "button.task_checkbox")
        
        marked_count = 0
        
        if progress_callback:
            progress_callback(f"📋 Encontrados {len(checkboxes)} checkboxes na coluna")
        
        # Marca cada checkbox que ainda não está marcado
        for index, checkbox in enumerate(checkboxes, 1):
            try:
                # Verifica se já está marcado
                aria_checked = checkbox.get_attribute('aria-checked')
                
                if aria_checked == 'false':
                    # Rola até o elemento
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                    time.sleep(0.3)
                    
                    # Clica no checkbox
                    checkbox.click()
                    marked_count += 1
                    time.sleep(0.5)  # Delay entre cliques
                    
                    if progress_callback:
                        progress_callback(f"   ✅ Checkbox {index}/{len(checkboxes)} marcado")
                else:
                    if progress_callback:
                        progress_callback(f"   ⏭️  Checkbox {index}/{len(checkboxes)} já estava marcado")
                        
            except Exception as checkbox_error:
                if progress_callback:
                    progress_callback(f"   ⚠️ Erro ao marcar checkbox {index}: {checkbox_error}")
                continue
        
        if progress_callback:
            progress_callback(f"✅ Total de {marked_count} checkboxes marcados na coluna '{section_title}'")
        
        return marked_count
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao marcar checkboxes da seção: {e}")
        return 0


def navigate_to_board_project(driver, progress_callback=None):
    """
    Navega para o projeto do board 'Lances Servopa Outubro Dia 8'
    
    Args:
        driver: Instância do WebDriver já logado no Todoist
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se navegou com sucesso
    """
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        
        if progress_callback:
            progress_callback("🔍 Procurando projeto 'Lances Servopa Outubro Dia 8'...")
        
        # Procura o link do projeto
        project_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Lances Servopa Outubro Dia 8')]")
        ))
        
        if progress_callback:
            progress_callback("📂 Abrindo projeto do board...")
        
        project_link.click()
        time.sleep(4)  # Aguarda carregamento completo
        
        if progress_callback:
            progress_callback("✅ Board aberto com sucesso")
        
        return True
        
    except TimeoutException:
        if progress_callback:
            progress_callback("❌ Timeout ao procurar projeto")
        return False
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao navegar para projeto: {e}")
        return False


if __name__ == "__main__":
    # Teste do módulo
    print("Este módulo deve ser importado e usado com uma instância do WebDriver")
    print("Exemplo:")
    print("  from auth.todoist_auth import login_todoist_and_extract")
    print("  from utils.todoist_board_extractor import extract_complete_board")
    print("  ")
    print("  driver = create_driver()")
    print("  # Fazer login...")
    print("  board_data = extract_complete_board(driver)")
