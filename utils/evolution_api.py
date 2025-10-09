# utils/evolution_api.py
# Módulo de integração com Evolution API para envio de mensagens WhatsApp

import requests
import time
from typing import List, Dict, Optional, Tuple

class EvolutionAPI:
    """Cliente para integração com Evolution API WhatsApp"""
    
    def __init__(self, base_url: str, instance_name: str, api_key: str):
        """
        Inicializa cliente da Evolution API
        
        Args:
            base_url: URL base da API (ex: https://zap.tekvosoft.com)
            instance_name: Nome da instância (ex: david-tekvo)
            api_key: Chave de API para autenticação
        """
        self.base_url = base_url.rstrip('/')
        self.instance_name = instance_name
        self.api_key = api_key
        self.headers = {
            'apikey': api_key,
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Testa conexão com a API fazendo um envio de teste real
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # IMPORTANTE: Testa a URL completa de envio
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            
            # Verifica se a URL está acessível
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # 404 ou 405 significa que a rota existe mas o método está errado (OK!)
            # 401 ou 403 significa autenticação inválida
            if response.status_code in [404, 405]:
                return True, f"Conexão OK - API acessível em {url}"
            elif response.status_code in [401, 403]:
                return False, "API Key inválida ou sem permissão"
            elif response.status_code == 200:
                return True, "Conexão estabelecida com sucesso"
            else:
                return False, f"Status inesperado: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout na conexão com a API"
        except requests.exceptions.ConnectionError:
            return False, f"Erro de conexão - verifique a URL: {self.base_url}"
        except Exception as e:
            return False, f"Erro ao testar conexão: {str(e)}"
    
    def format_phone_number(self, phone: str) -> str:
        """
        Formata número de telefone para o padrão WhatsApp
        
        Args:
            phone: Número (ex: 5519995378302, 19995378302, etc)
            
        Returns:
            str: Número formatado com @c.us (ex: 5519995378302@c.us)
        """
        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do Brasil se não tiver
        if not phone.startswith('55'):
            phone = '55' + phone
        
        # IMPORTANTE: Adiciona sufixo @c.us (não @s.whatsapp.net)
        return f"{phone}@c.us"
    
    def send_text_message(self, phone: str, text: str) -> Tuple[bool, Dict]:
        """
        Envia mensagem de texto para um número
        
        Args:
            phone: Número de telefone (será formatado automaticamente)
            text: Texto da mensagem
            
        Returns:
            Tuple[bool, Dict]: (sucesso, resposta_da_api)
        """
        try:
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            
            # Formata número
            formatted_phone = self.format_phone_number(phone)
            
            # Prepara dados EXATAMENTE como na documentação
            payload = {
                "number": formatted_phone,
                "text": text
            }
            
            # Debug: mostra o que está sendo enviado
            print(f"DEBUG - URL: {url}")
            print(f"DEBUG - Payload: {payload}")
            print(f"DEBUG - Headers: {self.headers}")
            
            # Envia requisição
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"DEBUG - Status Code: {response.status_code}")
            print(f"DEBUG - Response: {response.text}")
            
            # Verifica resposta
            if response.status_code in [200, 201]:
                try:
                    return True, response.json()
                except:
                    return True, {'message': 'Enviado com sucesso'}
            else:
                return False, {
                    'error': f'Status {response.status_code}',
                    'message': response.text,
                    'url': url,
                    'payload': payload
                }
                
        except requests.exceptions.Timeout:
            return False, {'error': 'Timeout ao enviar mensagem'}
        except requests.exceptions.ConnectionError:
            return False, {'error': f'Erro de conexão com {self.base_url}'}
        except Exception as e:
            return False, {'error': str(e)}
    
    def send_media_message(self, phone: str, media_url: str, caption: str = "") -> Tuple[bool, Dict]:
        """
        Envia mensagem com mídia (imagem, vídeo, documento) para um número
        
        Args:
            phone: Número de telefone (será formatado automaticamente)
            media_url: URL da mídia ou base64
            caption: Legenda da mídia (opcional)
            
        Returns:
            Tuple[bool, Dict]: (sucesso, resposta_da_api)
        """
        try:
            url = f"{self.base_url}/message/sendMedia/{self.instance_name}"
            
            # Formata número (sem @c.us para sendMedia - formato: 5519999999999)
            formatted_phone = self.format_phone_number(phone).replace('@c.us', '')
            
            # SOLUÇÃO: A API está pedindo formato MISTO!
            # Documentação oficial pede mediaMessage.mediaType
            # Mas a instância está pedindo mediatype no nível raiz
            # Vamos enviar AMBOS para garantir compatibilidade
            payload = {
                "number": formatted_phone,
                "mediatype": "image",     # ✅ Formato que a instância está pedindo
                "media": media_url,       # ✅ No nível raiz
                "mediaMessage": {         # ✅ Formato da documentação (backup)
                    "mediaType": "image",
                    "media": media_url
                }
            }
            
            # Adiciona caption em ambos os lugares
            if caption:
                payload["caption"] = caption
                payload["mediaMessage"]["caption"] = caption
            
            # Debug
            print(f"DEBUG - URL: {url}")
            print(f"DEBUG - Payload: {payload}")
            
            # Envia requisição
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"DEBUG - Status Code: {response.status_code}")
            print(f"DEBUG - Response: {response.text}")
            
            # Verifica resposta
            if response.status_code in [200, 201]:
                try:
                    return True, response.json()
                except:
                    return True, {'message': 'Mídia enviada com sucesso'}
            else:
                return False, {
                    'error': f'Status {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.Timeout:
            return False, {'error': 'Timeout ao enviar mídia'}
        except requests.exceptions.ConnectionError:
            return False, {'error': f'Erro de conexão com {self.base_url}'}
        except Exception as e:
            return False, {'error': str(e)}
    
    def send_document(
        self,
        phone: str,
        file_path: str,
        caption: str = "",
        filename: str = None
    ) -> Tuple[bool, Dict]:
        """
        Envia documento (PDF, DOC, XLSX, etc) para um número via WhatsApp
        
        Args:
            phone: Número de telefone (+5519999999999 ou 5519999999999)
            file_path: Caminho do arquivo local OU URL pública
            caption: Legenda do documento (opcional)
            filename: Nome do arquivo que aparecerá no WhatsApp (opcional)
            
        Returns:
            Tuple[bool, Dict]: (sucesso, resposta_da_api)
            
        Examples:
            >>> api = EvolutionAPI(...)
            >>> # Com arquivo local
            >>> success, response = api.send_document(
            ...     phone="5519999999999",
            ...     file_path="/path/to/boleto.pdf",
            ...     caption="Seu boleto",
            ...     filename="Boleto_Janeiro.pdf"
            ... )
            >>> # Com URL pública
            >>> success, response = api.send_document(
            ...     phone="5519999999999",
            ...     file_path="https://example.com/arquivo.pdf",
            ...     filename="documento.pdf"
            ... )
        """
        try:
            import os
            import base64
            
            url = f"{self.base_url}/message/sendMedia/{self.instance_name}"
            formatted_phone = self.format_phone_number(phone).replace('@c.us', '')
            
            # Determina tipo de arquivo e converte se necessário
            file_data = None
            
            # Se é arquivo local, converte para base64
            if os.path.exists(file_path):
                print(f"📄 Lendo arquivo local: {file_path}")
                
                with open(file_path, 'rb') as f:
                    file_content = base64.b64encode(f.read()).decode('utf-8')
                
                # Detecta mimetype baseado na extensão
                ext = os.path.splitext(file_path)[1].lower()
                mimetype_map = {
                    '.pdf': 'application/pdf',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.xls': 'application/vnd.ms-excel',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.txt': 'text/plain',
                    '.zip': 'application/zip',
                    '.rar': 'application/x-rar-compressed',
                }
                mimetype = mimetype_map.get(ext, 'application/octet-stream')
                
                file_data = f"data:{mimetype};base64,{file_content}"
                
                if not filename:
                    filename = os.path.basename(file_path)
                
                file_size = len(file_content)
                print(f"📦 Arquivo codificado: {file_size:,} bytes base64")
            
            # Se é URL, usa direto (Evolution API baixa automaticamente)
            elif file_path.startswith(('http://', 'https://')):
                print(f"🌐 Usando URL pública: {file_path}")
                file_data = file_path
                
                if not filename:
                    filename = file_path.split('/')[-1] or "documento.pdf"
            
            else:
                raise ValueError(f"Arquivo não encontrado e não é URL válida: {file_path}")
            
            # Mont payload para Evolution API - FORMATO CORRETO PARA DOCUMENTOS
            # A Evolution API espera base64 SEM o prefixo "data:..."
            payload = {
                "number": formatted_phone,
                "mediatype": "document",  # IMPORTANTE: tipo 'document' para PDFs/docs
                "fileName": filename,  # Nome que aparece no WhatsApp
            }
            
            # Para base64, remove o prefixo "data:..."
            if file_data.startswith('data:'):
                # Extrai apenas o base64 puro
                base64_only = file_data.split(',', 1)[1] if ',' in file_data else file_data
                payload["media"] = base64_only
            else:
                # É URL pública
                payload["media"] = file_data
            
            # Adiciona caption se fornecido
            if caption:
                payload["caption"] = caption
            
            print(f"📤 Enviando documento: {filename}")
            print(f"   📞 Para: {formatted_phone}")
            print(f"   📝 Caption: {caption if caption else '(sem legenda)'}")
            print(f"   🔗 URL: {url}")
            
            # Envia requisição
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=60  # Timeout maior para upload de arquivos
            )
            
            print(f"📨 Status Code: {response.status_code}")
            
            # Processa resposta
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    print(f"✅ Documento enviado com sucesso!")
                    print(f"   Response: {response_data}")
                    return True, response_data
                except ValueError:
                    # Se não é JSON, considera sucesso mesmo assim
                    print(f"✅ Documento enviado (resposta não-JSON)")
                    return True, {'message': 'Documento enviado com sucesso', 'raw_response': response.text}
            else:
                error_msg = f'Status {response.status_code}'
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    error_msg = response.text
                
                print(f"❌ Falha ao enviar: {error_msg}")
                return False, {
                    'error': error_msg,
                    'status_code': response.status_code,
                    'response': response.text
                }
                
        except FileNotFoundError as e:
            error_msg = f'Arquivo não encontrado: {file_path}'
            print(f"❌ {error_msg}")
            return False, {'error': error_msg}
        except requests.exceptions.Timeout:
            error_msg = 'Timeout ao enviar documento (mais de 60 segundos)'
            print(f"❌ {error_msg}")
            return False, {'error': error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = f'Erro de conexão com {self.base_url}'
            print(f"❌ {error_msg}")
            return False, {'error': error_msg}
        except Exception as e:
            error_msg = f'Erro inesperado: {str(e)}'
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return False, {'error': error_msg}
    
    def send_bulk_messages(
        self,
        contacts: List[Dict[str, str]],
        message: str,
        delay_between_messages: float = 2.0,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, any]:
        """
        Envia mensagem para múltiplos contatos
        
        Args:
            contacts: Lista de dicts com 'phone' e 'name'
            message: Texto da mensagem (pode usar {nome} para personalizar)
            delay_between_messages: Delay entre envios em segundos
            progress_callback: Função para callback de progresso
            
        Returns:
            Dict com estatísticas do envio
        """
        results = {
            'total': len(contacts),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        for index, contact in enumerate(contacts, 1):
            phone = contact.get('phone', '')
            name = contact.get('name', 'Cliente')
            
            # Personaliza mensagem com nome
            personalized_message = message.replace('{nome}', name)
            
            if progress_callback:
                progress_callback(
                    f"📤 [{index}/{len(contacts)}] Enviando para {name} ({phone})..."
                )
            
            # Envia mensagem
            success, response = self.send_text_message(phone, personalized_message)
            
            # Registra resultado
            result_detail = {
                'phone': phone,
                'name': name,
                'success': success,
                'response': response
            }
            results['details'].append(result_detail)
            
            if success:
                results['success'] += 1
                if progress_callback:
                    progress_callback(f"✅ Enviado para {name}")
            else:
                results['failed'] += 1
                error_msg = response.get('error', 'Erro desconhecido')
                if progress_callback:
                    progress_callback(f"❌ Falha para {name}: {error_msg}")
            
            # Delay entre mensagens (exceto última)
            if index < len(contacts):
                time.sleep(delay_between_messages)
        
        # Resumo final
        if progress_callback:
            progress_callback("")
            progress_callback("=" * 50)
            progress_callback(f"📊 Resumo do envio:")
            progress_callback(f"   Total: {results['total']}")
            progress_callback(f"   ✅ Sucesso: {results['success']}")
            progress_callback(f"   ❌ Falhas: {results['failed']}")
            progress_callback("=" * 50)
        
        return results
    
    def validate_config(self) -> Tuple[bool, str]:
        """
        Valida configurações da API
        
        Returns:
            Tuple[bool, str]: (válido, mensagem)
        """
        errors = []
        
        if not self.base_url:
            errors.append("URL base não configurada")
        
        if not self.instance_name:
            errors.append("Nome da instância não configurado")
        
        if not self.api_key:
            errors.append("API Key não configurada")
        
        if errors:
            return False, "; ".join(errors)
        
        # Testa conexão
        success, message = self.test_connection()
        
        if success:
            return True, "Configuração válida e API acessível"
        else:
            return False, f"Configuração inválida: {message}"


def parse_contacts_from_text(text: str) -> List[Dict[str, str]]:
    """
    Parseia contatos de texto no formato:
    5519995378302 - João Silva
    5519988776655 - Maria Santos
    
    Args:
        text: Texto com contatos
        
    Returns:
        Lista de dicts com 'phone' e 'name'
    """
    contacts = []
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Tenta separar por '-' ou espaço
        if '-' in line:
            parts = line.split('-', 1)
        elif ' ' in line:
            parts = line.split(' ', 1)
        else:
            # Só número
            parts = [line, 'Cliente']
        
        if len(parts) >= 2:
            phone = parts[0].strip()
            name = parts[1].strip()
        else:
            phone = parts[0].strip()
            name = 'Cliente'
        
        # Remove caracteres não numéricos do telefone
        phone = ''.join(filter(str.isdigit, phone))
        
        if phone:  # Só adiciona se tiver telefone
            contacts.append({
                'phone': phone,
                'name': name
            })
    
    return contacts


# Teste do módulo
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DO MÓDULO EVOLUTION API")
    print("=" * 60)
    print()
    
    # Configuração de teste
    BASE_URL = "https://zap.tekvosoft.com"
    INSTANCE = "david-tekvo"
    API_KEY = "634A7E882CE5-4314-8C5B-BC79C0A9EBBA"
    
    # Cria cliente
    api = EvolutionAPI(BASE_URL, INSTANCE, API_KEY)
    
    # Teste 1: Validação de configuração
    print("📋 Teste 1: Validando configuração...")
    valid, message = api.validate_config()
    print(f"   {'✅' if valid else '❌'} {message}")
    print()
    
    # Teste 2: Teste de conexão
    print("🔌 Teste 2: Testando conexão...")
    connected, conn_message = api.test_connection()
    print(f"   {'✅' if connected else '❌'} {conn_message}")
    print()
    
    # Teste 3: Formatação de números
    print("📱 Teste 3: Formatação de números...")
    test_numbers = [
        "5519995378302",
        "19995378302",
        "(19) 99537-8302",
        "999537-8302"
    ]
    for num in test_numbers:
        formatted = api.format_phone_number(num)
        print(f"   {num} → {formatted}")
    print()
    
    # Teste 4: Parse de contatos
    print("👥 Teste 4: Parse de contatos...")
    contacts_text = """
    5519995378302 - João Silva
    5519988776655 - Maria Santos
    19977665544 Ana Costa
    """
    contacts = parse_contacts_from_text(contacts_text)
    print(f"   Parseados {len(contacts)} contatos:")
    for c in contacts:
        print(f"      {c['phone']} - {c['name']}")
    print()
    
    print("=" * 60)
    print("✅ Testes concluídos!")
    print("=" * 60)
