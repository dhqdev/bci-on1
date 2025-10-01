# automation/cycle_orchestrator.py
# Orquestrador do ciclo completo: Todoist → Servopa → Todoist (checkbox) → repetir

import time
from selenium.webdriver.common.by import By

def switch_to_window_with_url(driver, url_part, progress_callback=None):
    """
    Muda para a janela/aba que contém a URL especificada
    
    Args:
        driver: Instância do WebDriver
        url_part: Parte da URL para identificar a janela (ex: "todoist", "servopa")
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        bool: True se encontrou e mudou com sucesso
    """
    try:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if url_part in driver.current_url:
                if progress_callback:
                    progress_callback(f"🔄 Mudado para aba: {url_part}")
                return True
        
        if progress_callback:
            progress_callback(f"❌ Aba com '{url_part}' não encontrada")
        return False
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro ao mudar de aba: {e}")
        return False


def executar_ciclo_completo(driver, board_data, progress_callback=None, history_callback=None, should_continue=None):
    """
    Executa o ciclo completo coluna por coluna, linha por linha
    
    Fluxo:
    1. Para cada coluna (seção/grupo) no board:
       2. Para cada linha (tarefa/cota) naquela coluna:
          a. Muda para aba do Servopa
          b. Busca grupo
          c. Seleciona cota
          d. Navega para lances
          e. Executa lance (com verificação de popup)
          f. Muda para aba do Todoist
          g. Marca checkbox como concluído (individual)
          h. Volta para aba do Servopa
          i. Registra no histórico
       3. Ao terminar a coluna: marca TODOS os checkboxes da coluna
       4. Próxima coluna
    
    Args:
        driver: Instância do WebDriver com ambas as abas abertas
        board_data: Dados extraídos do board (retorno de extract_complete_board)
        progress_callback: Função para atualizar progresso na UI
        history_callback: Função para adicionar entrada ao histórico (grupo, cota, nome, valor, status, obs)
        should_continue: Função que retorna True se deve continuar, False se deve parar
        
    Returns:
        dict: Estatísticas da execução
    """
    from automation.servopa_lances import processar_lance_completo
    from utils.todoist_board_extractor import mark_task_completed, mark_all_section_tasks_completed
    
    stats = {
        'total_sections': len(board_data['sections']),
        'total_tasks': sum(len(s['tasks']) for s in board_data['sections']),
        'completed': 0,
        'failed': 0,
        'skipped': 0,
        'results': []
    }
    
    if progress_callback:
        progress_callback("=" * 60)
        progress_callback(f"🚀 INICIANDO CICLO COMPLETO")
        progress_callback(f"📊 {stats['total_sections']} colunas, {stats['total_tasks']} tarefas")
        progress_callback("=" * 60)
    
    # Percorre cada coluna (seção)
    for section_index, section in enumerate(board_data['sections'], 1):
        # Verifica se deve continuar
        if should_continue and not should_continue():
            if progress_callback:
                progress_callback("⏹️ Automação interrompida pelo usuário")
            return stats
        
        grupo = section['grupo']
        section_title = section['title']
        total_tasks_in_section = len(section['tasks'])
        
        if progress_callback:
            progress_callback("")
            progress_callback("┌" + "─" * 58 + "┐")
            progress_callback(f"│ COLUNA {section_index}/{stats['total_sections']}: {section_title:<48}│")
            progress_callback(f"│ Grupo: {grupo:<51}│")
            progress_callback(f"│ Tarefas: {total_tasks_in_section:<49}│")
            progress_callback("└" + "─" * 58 + "┘")
        
        # Percorre cada linha (tarefa) nesta coluna
        for task_index, task in enumerate(section['tasks'], 1):
            # Verifica se deve continuar
            if should_continue and not should_continue():
                if progress_callback:
                    progress_callback("⏹️ Automação interrompida pelo usuário")
                return stats
            
            cota = task['cota']
            nome = task['nome']
            checkbox = task['checkbox_element']
            
            if progress_callback:
                progress_callback("")
                progress_callback(f"┌─ Tarefa {task_index}/{total_tasks_in_section} " + "─" * 40)
                progress_callback(f"│  📝 Cota: {cota}")
                progress_callback(f"│  👤 Nome: {nome}")
                progress_callback(f"└" + "─" * 50)
            
            result = {
                'section': section_title,
                'grupo': grupo,
                'cota': cota,
                'nome': nome,
                'success': False,
                'error': None
            }
            
            try:
                # ========== VERIFICAÇÃO: CONTINUAR? ==========
                if should_continue and not should_continue():
                    # Automação foi parada pelo usuário DURANTE o processamento deste item
                    if history_callback:
                        try:
                            history_callback(grupo, cota, nome, "N/A", "⏹️ Parado", "Automação interrompida pelo usuário")
                        except:
                            pass
                    if progress_callback:
                        progress_callback("⏹️ Automação interrompida pelo usuário durante processamento")
                    return stats
                
                # ========== PARTE 1: SERVOPA ==========
                if progress_callback:
                    progress_callback("🌐 [SERVOPA] Mudando para aba do Servopa...")
                
                if not switch_to_window_with_url(driver, "servopa", progress_callback):
                    raise Exception("Não foi possível mudar para aba do Servopa")
                
                time.sleep(1)
                
                # ========== VERIFICAÇÃO: CONTINUAR? ==========
                if should_continue and not should_continue():
                    if history_callback:
                        try:
                            history_callback(grupo, cota, nome, "N/A", "⏹️ Parado", "Automação interrompida pelo usuário")
                        except:
                            pass
                    if progress_callback:
                        progress_callback("⏹️ Automação interrompida pelo usuário durante processamento")
                    return stats
                
                # Processa lance completo no Servopa
                if progress_callback:
                    progress_callback(f"🎯 [SERVOPA] Processando lance: Grupo {grupo} - Cota {cota}")
                
                lance_result = processar_lance_completo(driver, grupo, cota, progress_callback)
                
                if not lance_result['success']:
                    raise Exception(f"Falha no processamento do lance: {lance_result.get('error', 'Desconhecido')}")
                
                # Verifica se lance já existia
                if lance_result.get('already_exists', False):
                    if progress_callback:
                        progress_callback(f"✅ [SERVOPA] {lance_result.get('lance_message', 'Lance já registrado')}")
                else:
                    if progress_callback:
                        progress_callback(f"✅ [SERVOPA] Lance registrado com sucesso!")
                
                # ========== VERIFICAÇÃO: CONTINUAR? ==========
                if should_continue and not should_continue():
                    if history_callback:
                        try:
                            history_callback(grupo, cota, nome, "N/A", "⏹️ Parado", "Automação interrompida pelo usuário")
                        except:
                            pass
                    if progress_callback:
                        progress_callback("⏹️ Automação interrompida pelo usuário durante processamento")
                    return stats
                
                # ========== PARTE 2: TODOIST ==========
                if progress_callback:
                    progress_callback("📋 [TODOIST] Mudando para aba do Todoist...")
                
                if not switch_to_window_with_url(driver, "todoist", progress_callback):
                    raise Exception("Não foi possível mudar para aba do Todoist")
                
                time.sleep(1)
                
                # Marca tarefa como concluída
                if progress_callback:
                    progress_callback(f"✅ [TODOIST] Marcando tarefa como concluída...")
                
                if mark_task_completed(driver, checkbox, progress_callback):
                    if progress_callback:
                        progress_callback(f"✅ [TODOIST] Tarefa marcada com sucesso!")
                    
                    result['success'] = True
                    stats['completed'] += 1
                    
                    # ========== REGISTRA NO HISTÓRICO (SUCESSO) ==========
                    if history_callback:
                        try:
                            valor_lance = lance_result.get('valor_lance', 'N/A')
                            if lance_result.get('already_exists', False):
                                observacao = "Lance já existia (protocolo anterior detectado)"
                                status = "✅ Sucesso (já existia)"
                            else:
                                observacao = "Lance registrado com sucesso"
                                status = "✅ Sucesso"
                            
                            history_callback(grupo, cota, nome, f"{valor_lance}%", status, observacao)
                        except Exception as hist_error:
                            if progress_callback:
                                progress_callback(f"⚠️ Aviso: Não foi possível registrar no histórico: {hist_error}")
                else:
                    raise Exception("Falha ao marcar checkbox no Todoist")
                
                # ========== RETORNA PARA SERVOPA ==========
                if progress_callback:
                    progress_callback("🔄 Retornando para aba do Servopa para próxima tarefa...")
                
                switch_to_window_with_url(driver, "servopa", progress_callback)
                time.sleep(1)
                
                if progress_callback:
                    progress_callback(f"🎉 Tarefa {task_index}/{total_tasks_in_section} concluída com sucesso!")
                    progress_callback(f"📊 Progresso: {stats['completed']}/{stats['total_tasks']} tarefas")
                
            except Exception as e:
                stats['failed'] += 1
                result['error'] = str(e)
                
                # ========== REGISTRA NO HISTÓRICO (ERRO) ==========
                if history_callback:
                    try:
                        history_callback(grupo, cota, nome, "N/A", "❌ Erro", str(e)[:200])
                    except Exception as hist_error:
                        if progress_callback:
                            progress_callback(f"⚠️ Aviso: Não foi possível registrar erro no histórico: {hist_error}")
                
                if progress_callback:
                    progress_callback(f"❌ Erro na tarefa {task_index}: {e}")
                    progress_callback(f"⚠️ Tentando continuar com próxima tarefa...")
                
                # Tenta voltar para Servopa mesmo após erro
                try:
                    switch_to_window_with_url(driver, "servopa", progress_callback)
                except:
                    pass
            
            stats['results'].append(result)
        
        # ========== FIM DA COLUNA: MARCA TODOS OS CHECKBOXES ==========
        if progress_callback:
            progress_callback("")
            progress_callback("=" * 60)
            progress_callback(f"📋 FINALIZANDO COLUNA: {section_title}")
            progress_callback("=" * 60)
        
        # Muda para Todoist para marcar todos os checkboxes
        try:
            if switch_to_window_with_url(driver, "todoist", progress_callback):
                time.sleep(2)
                
                # Marca todos os checkboxes da coluna
                marked_count = mark_all_section_tasks_completed(driver, section_title, progress_callback)
                
                if progress_callback:
                    progress_callback(f"✅ {marked_count} checkboxes garantidos na coluna '{section_title}'")
            
            # Volta para Servopa para próxima coluna
            switch_to_window_with_url(driver, "servopa", progress_callback)
            time.sleep(1)
            
        except Exception as final_mark_error:
            if progress_callback:
                progress_callback(f"⚠️ Erro ao marcar checkboxes finais: {final_mark_error}")
        
        # Fim da coluna
        if progress_callback:
            progress_callback("")
            progress_callback(f"✅ Coluna '{section_title}' TOTALMENTE concluída!")
            progress_callback(f"📊 Total: {stats['completed']} sucesso, {stats['failed']} falhas")
    
    # ========== RELATÓRIO FINAL ==========
    if progress_callback:
        progress_callback("")
        progress_callback("=" * 60)
        progress_callback("🎉 CICLO COMPLETO FINALIZADO!")
        progress_callback("=" * 60)
        if stats['skipped'] > 0:
            progress_callback(f"⏭️ Tarefas puladas (continuação): {stats['skipped']}")
        progress_callback(f"✅ Tarefas concluídas: {stats['completed']}/{stats['total_tasks']}")
        progress_callback(f"❌ Tarefas com falha: {stats['failed']}/{stats['total_tasks']}")
        if stats['completed'] + stats['failed'] > 0:
            progress_callback(f"📊 Taxa de sucesso: {(stats['completed']/(stats['completed']+stats['failed'])*100):.1f}%")
        progress_callback("=" * 60)
    
    return stats


def executar_automacao_completa(driver, progress_callback=None):
    """
    Executa a automação completa do início ao fim
    
    Requisitos:
    - Driver deve ter 2 abas abertas: Servopa e Todoist
    - Ambas devem estar logadas
    - Todoist deve estar no projeto do board
    
    Args:
        driver: Instância do WebDriver
        progress_callback: Função para atualizar progresso na UI
        
    Returns:
        dict: Estatísticas da execução
    """
    from utils.todoist_board_extractor import extract_complete_board
    
    try:
        # Verifica se há 2 abas abertas
        if len(driver.window_handles) < 2:
            if progress_callback:
                progress_callback("❌ Erro: São necessárias 2 abas abertas (Servopa e Todoist)")
            return None
        
        if progress_callback:
            progress_callback("✅ Verificado: 2 abas abertas")
        
        # Muda para aba do Todoist para extrair board
        if progress_callback:
            progress_callback("📋 Mudando para aba do Todoist para extrair dados...")
        
        if not switch_to_window_with_url(driver, "todoist", progress_callback):
            raise Exception("Não foi possível encontrar aba do Todoist")
        
        time.sleep(2)
        
        # Extrai estrutura completa do board
        board_data = extract_complete_board(driver, progress_callback)
        
        if not board_data or not board_data['sections']:
            raise Exception("Falha ao extrair dados do board ou board vazio")
        
        # Executa ciclo completo
        stats = executar_ciclo_completo(driver, board_data, progress_callback)
        
        return stats
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro na automação completa: {e}")
        return None


if __name__ == "__main__":
    # Teste do módulo
    print("Este módulo deve ser importado e usado com uma instância do WebDriver")
    print("Exemplo:")
    print("  from auth.servopa_auth import create_driver, login_servopa")
    print("  from auth.todoist_auth import login_todoist_and_extract")
    print("  from automation.cycle_orchestrator import executar_automacao_completa")
    print("  ")
    print("  driver = create_driver()")
    print("  login_servopa(driver)")
    print("  # Abrir Todoist em nova aba e fazer login...")
    print("  stats = executar_automacao_completa(driver)")
