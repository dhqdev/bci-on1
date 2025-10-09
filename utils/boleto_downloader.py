"""
Utilitário para baixar PDFs de boletos do Servopa e salvar em cache

Este módulo permite:
- Baixar PDFs de boletos do Servopa
- Salvar em cache local para reutilização
- Verificar se boleto já está em cache

Uso:
    from utils.boleto_downloader import download_boleto_pdf, get_cached_boleto
    
    # Baixar boleto
    sucesso, pdf_path, erro = download_boleto_pdf(boleto_url, task_id="12345")
    
    # Verificar cache
    pdf_path = get_cached_boleto("12345")
"""

import os
import requests
from datetime import datetime
from typing import Optional, Tuple

def download_boleto_pdf(boleto_url: str, task_id: str = None, cache_dir: str = None) -> Tuple[bool, str, Optional[str]]:
    """
    Baixa PDF do boleto do Servopa e salva em cache
    
    Args:
        boleto_url: URL do boleto no Servopa
        task_id: ID da task do Todoist (para nome do arquivo)
        cache_dir: Diretório de cache (padrão: data/boletos_pdf)
        
    Returns:
        Tuple[bool, str, Optional[str]]: (sucesso, caminho_arquivo, mensagem_erro)
        
    Examples:
        >>> sucesso, path, erro = download_boleto_pdf("https://...", "12345")
        >>> if sucesso:
        ...     print(f"PDF salvo em: {path}")
        ... else:
        ...     print(f"Erro: {erro}")
    """
    try:
        # Define diretório de cache
        if not cache_dir:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = os.path.join(project_root, 'data', 'boletos_pdf')
        
        os.makedirs(cache_dir, exist_ok=True)
        
        # Define nome do arquivo
        if task_id:
            filename = f"boleto_{task_id}.pdf"
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"boleto_{timestamp}.pdf"
        
        file_path = os.path.join(cache_dir, filename)
        
        # Se já existe em cache, retorna direto
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ Boleto já em cache: {filename} ({file_size} bytes)")
            return True, file_path, None
        
        # Download do PDF
        print(f"📥 Baixando boleto de {boleto_url}")
        
        # Headers para evitar bloqueio
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.consorcioservopa.com.br/',
            'Connection': 'keep-alive',
        }
        
        # Faz download com timeout e redirects
        response = requests.get(
            boleto_url,
            headers=headers,
            timeout=30,
            allow_redirects=True,
            stream=True  # Stream para arquivos grandes
        )
        
        if response.status_code != 200:
            return False, "", f"Erro HTTP {response.status_code}"
        
        # Verifica se é PDF válido
        content_type = response.headers.get('Content-Type', '').lower()
        
        # Lê primeiros bytes para verificar
        content = response.content
        
        if 'pdf' not in content_type and not content.startswith(b'%PDF'):
            # Tenta detectar se é HTML de erro
            if content.startswith(b'<!DOCTYPE') or content.startswith(b'<html'):
                return False, "", "Servopa retornou página HTML ao invés de PDF (possível sessão expirada)"
            return False, "", f"Resposta não é um PDF válido (Content-Type: {content_type})"
        
        # Salva arquivo
        with open(file_path, 'wb') as f:
            f.write(content)
        
        file_size = len(content)
        print(f"✅ Boleto salvo: {filename} ({file_size:,} bytes)")
        
        return True, file_path, None
        
    except requests.exceptions.Timeout:
        return False, "", "Timeout ao baixar PDF (mais de 30 segundos)"
    except requests.exceptions.ConnectionError as e:
        return False, "", f"Erro de conexão: {str(e)}"
    except requests.RequestException as e:
        return False, "", f"Erro ao baixar: {str(e)}"
    except IOError as e:
        return False, "", f"Erro ao salvar arquivo: {str(e)}"
    except Exception as e:
        return False, "", f"Erro inesperado: {str(e)}"


def get_cached_boleto(task_id: str, cache_dir: str = None) -> Optional[str]:
    """
    Verifica se boleto já está em cache
    
    Args:
        task_id: ID da task do Todoist
        cache_dir: Diretório de cache (padrão: data/boletos_pdf)
        
    Returns:
        Optional[str]: Caminho do arquivo se existir, None caso contrário
        
    Examples:
        >>> pdf_path = get_cached_boleto("12345")
        >>> if pdf_path:
        ...     print(f"PDF encontrado: {pdf_path}")
        ... else:
        ...     print("PDF não está em cache")
    """
    if not cache_dir:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_dir = os.path.join(project_root, 'data', 'boletos_pdf')
    
    filename = f"boleto_{task_id}.pdf"
    file_path = os.path.join(cache_dir, filename)
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"🔍 Boleto encontrado em cache: {filename} ({file_size} bytes)")
        return file_path
    else:
        print(f"🔍 Boleto não está em cache: {filename}")
        return None


def clear_old_boletos(cache_dir: str = None, days_old: int = 30) -> Tuple[int, int]:
    """
    Remove boletos antigos do cache
    
    Args:
        cache_dir: Diretório de cache (padrão: data/boletos_pdf)
        days_old: Remover arquivos com mais de X dias (padrão: 30)
        
    Returns:
        Tuple[int, int]: (arquivos_removidos, bytes_liberados)
        
    Examples:
        >>> removed, bytes_freed = clear_old_boletos(days_old=7)
        >>> print(f"Removidos {removed} arquivos ({bytes_freed:,} bytes)")
    """
    import time
    
    if not cache_dir:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_dir = os.path.join(project_root, 'data', 'boletos_pdf')
    
    if not os.path.exists(cache_dir):
        return 0, 0
    
    removed_count = 0
    bytes_freed = 0
    cutoff_time = time.time() - (days_old * 86400)  # dias em segundos
    
    for filename in os.listdir(cache_dir):
        if not filename.endswith('.pdf'):
            continue
        
        file_path = os.path.join(cache_dir, filename)
        
        try:
            # Verifica idade do arquivo
            if os.path.getmtime(file_path) < cutoff_time:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                removed_count += 1
                bytes_freed += file_size
                print(f"🗑️  Removido: {filename} ({file_size} bytes)")
        except Exception as e:
            print(f"⚠️  Erro ao remover {filename}: {e}")
    
    if removed_count > 0:
        print(f"✅ Limpeza concluída: {removed_count} arquivos removidos ({bytes_freed:,} bytes)")
    else:
        print("ℹ️  Nenhum arquivo antigo encontrado")
    
    return removed_count, bytes_freed


if __name__ == '__main__':
    """Testes básicos"""
    print("=" * 60)
    print("TESTE: Boleto Downloader")
    print("=" * 60)
    
    # Teste 1: Verificar cache inexistente
    print("\n1️⃣  Teste: Verificar cache inexistente")
    result = get_cached_boleto("teste_12345")
    print(f"   Resultado: {result}")
    assert result is None, "Deveria retornar None"
    
    # Teste 2: URL inválida
    print("\n2️⃣  Teste: URL inválida")
    sucesso, path, erro = download_boleto_pdf("https://invalid-url-teste-123.com", "teste_url_invalida")
    print(f"   Sucesso: {sucesso}")
    print(f"   Erro: {erro}")
    assert not sucesso, "Deveria falhar com URL inválida"
    
    # Teste 3: Listar cache
    print("\n3️⃣  Teste: Verificar diretório de cache")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(project_root, 'data', 'boletos_pdf')
    
    if os.path.exists(cache_dir):
        files = [f for f in os.listdir(cache_dir) if f.endswith('.pdf')]
        print(f"   📁 {len(files)} arquivos em cache")
        for f in files[:5]:  # Mostra primeiros 5
            size = os.path.getsize(os.path.join(cache_dir, f))
            print(f"      - {f} ({size:,} bytes)")
    else:
        print(f"   📁 Diretório de cache não existe ainda")
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
    print("=" * 60)
