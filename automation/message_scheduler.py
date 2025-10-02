# automation/message_scheduler.py
# Módulo de agendamento automático de envio de mensagens WhatsApp

import time
import json
import os
import threading
import schedule
from datetime import datetime, date
from typing import Optional, Callable

class MessageScheduler:
    """Agendador de mensagens WhatsApp automáticas"""
    
    def __init__(self, config_file='evolution_config.json', progress_callback: Optional[Callable] = None):
        """
        Inicializa o agendador
        
        Args:
            config_file: Caminho para arquivo de configuração
            progress_callback: Função para callback de progresso
        """
        self.config_file = config_file
        self.progress_callback = progress_callback
        self.running = False
        self.scheduler_thread = None
        self.config = None
        
    def log(self, message):
        """Log de mensagem"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        try:
            if not os.path.exists(self.config_file):
                self.log(f"❌ Arquivo {self.config_file} não encontrado")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.log("✅ Configurações carregadas")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao carregar configurações: {e}")
            return False
    
    def check_if_should_send_today(self):
        """
        Verifica se deve enviar mensagens hoje
        
        Returns:
            str: 'dia7', 'dia15' ou None
        """
        today = date.today().day
        
        if not self.config:
            return None
        
        dias_para_enviar = self.config.get('agendamento', {}).get('dias_para_enviar', [7, 15])
        
        if today in dias_para_enviar:
            if today == 7:
                return 'dia7'
            elif today == 15:
                return 'dia15'
        
        return None
    
    def send_scheduled_messages(self):
        """Envia mensagens agendadas"""
        try:
            self.log("=" * 60)
            self.log("📅 Verificando agendamento de mensagens...")
            self.log("=" * 60)
            
            # Verifica se deve enviar hoje
            dia = self.check_if_should_send_today()
            
            if not dia:
                self.log(f"ℹ️ Hoje não é dia de envio (hoje: {date.today().day})")
                return
            
            self.log(f"✅ Hoje é {dia}! Iniciando envio de mensagens...")
            
            # Carrega config atualizado
            if not self.load_config():
                return
            
            from utils.evolution_api import EvolutionAPI
            
            # Cria cliente API
            api_config = self.config.get('api', {})
            api = EvolutionAPI(
                api_config.get('base_url', ''),
                api_config.get('instance_name', ''),
                api_config.get('api_key', '')
            )
            
            # Valida API
            valid, message = api.validate_config()
            if not valid:
                self.log(f"❌ API inválida: {message}")
                return
            
            self.log("✅ API validada com sucesso")
            
            # Pega grupos e mensagens
            grupos = self.config.get('grupos', {})
            mensagens = self.config.get('mensagens', {}).get(dia, {})
            
            if not grupos or not mensagens:
                self.log("❌ Nenhum grupo ou mensagem configurada")
                return
            
            # Delay entre mensagens
            delay = self.config.get('configuracoes', {}).get('delay_entre_mensagens', 2.0)
            
            total_sent = 0
            total_failed = 0
            
            # Envia para cada grupo
            for grupo_id, grupo_data in grupos.items():
                self.log("")
                self.log(f"📊 Processando {grupo_data.get('nome', grupo_id)}...")
                
                # Verifica se há mensagem configurada para este grupo
                if grupo_id not in mensagens:
                    self.log(f"⚠️ Nenhuma mensagem configurada para {grupo_id} no {dia}")
                    continue
                
                message = mensagens[grupo_id]
                contacts = grupo_data.get('contatos', [])
                
                if not contacts:
                    self.log(f"⚠️ Nenhum contato no grupo {grupo_id}")
                    continue
                
                self.log(f"📤 Enviando para {len(contacts)} contato(s)...")
                
                # Envia mensagens
                results = api.send_bulk_messages(
                    contacts,
                    message,
                    delay_between_messages=delay,
                    progress_callback=self.log
                )
                
                total_sent += results['success']
                total_failed += results['failed']
            
            # Resumo final
            self.log("")
            self.log("=" * 60)
            self.log(f"📊 RESUMO DO ENVIO AUTOMÁTICO - {dia.upper()}")
            self.log("=" * 60)
            self.log(f"✅ Total enviadas: {total_sent}")
            self.log(f"❌ Total falhas: {total_failed}")
            self.log(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            self.log("=" * 60)
            
        except Exception as e:
            self.log(f"❌ Erro ao enviar mensagens agendadas: {e}")
    
    def schedule_daily_check(self):
        """Agenda verificação diária"""
        if not self.config:
            if not self.load_config():
                return False
        
        agendamento = self.config.get('agendamento', {})
        
        if not agendamento.get('enabled', False):
            self.log("⚠️ Agendamento automático está desabilitado")
            return False
        
        horario_envio = agendamento.get('horario_envio', '09:00')
        dias_para_enviar = agendamento.get('dias_para_enviar', [7, 15])
        
        # Agenda tarefa
        schedule.every().day.at(horario_envio).do(self.send_scheduled_messages)
        
        self.log(f"✅ Agendamento configurado para {horario_envio}")
        self.log(f"📅 Dias de envio: {', '.join(map(str, dias_para_enviar))}")
        
        return True
    
    def run_scheduler(self):
        """Executa o loop do agendador"""
        self.running = True
        
        self.log("=" * 60)
        self.log("🕐 AGENDADOR DE MENSAGENS INICIADO")
        self.log("=" * 60)
        
        # Carrega configurações e agenda
        if not self.schedule_daily_check():
            self.log("❌ Falha ao configurar agendamento")
            self.running = False
            return
        
        self.log("🔄 Agendador em execução... (pressione Ctrl+C para parar)")
        
        # Loop principal
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
        
        self.log("⏹️ Agendador parado")
    
    def start(self):
        """Inicia agendador em thread separada"""
        if self.running:
            self.log("⚠️ Agendador já está em execução")
            return False
        
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        return True
    
    def stop(self):
        """Para o agendador"""
        if not self.running:
            self.log("⚠️ Agendador não está em execução")
            return False
        
        self.log("⏹️ Parando agendador...")
        self.running = False
        
        # Aguarda thread terminar
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        # Limpa agenda
        schedule.clear()
        
        self.log("✅ Agendador parado com sucesso")
        return True
    
    def test_send_now(self):
        """Testa envio imediato (independente do dia)"""
        self.log("=" * 60)
        self.log("🧪 TESTE DE ENVIO IMEDIATO")
        self.log("=" * 60)
        
        # Força envio
        self.send_scheduled_messages()


# Teste do módulo
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DO AGENDADOR DE MENSAGENS")
    print("=" * 60)
    print()
    
    # Cria agendador
    scheduler = MessageScheduler(progress_callback=print)
    
    # Teste 1: Carregar configurações
    print("📋 Teste 1: Carregando configurações...")
    if scheduler.load_config():
        print("✅ Configurações carregadas")
    else:
        print("❌ Falha ao carregar configurações")
        exit(1)
    print()
    
    # Teste 2: Verificar se deve enviar hoje
    print("📅 Teste 2: Verificando dia de envio...")
    dia = scheduler.check_if_should_send_today()
    if dia:
        print(f"✅ Hoje é {dia} - deve enviar mensagens")
    else:
        print(f"ℹ️ Hoje não é dia de envio (hoje: {date.today().day})")
    print()
    
    # Teste 3: Teste de envio (comentado para não enviar de verdade)
    print("🧪 Teste 3: Envio de teste")
    print("   (descomente a linha abaixo para testar envio real)")
    # scheduler.test_send_now()
    print()
    
    # Teste 4: Configurar agendamento
    print("⏰ Teste 4: Configurando agendamento...")
    if scheduler.schedule_daily_check():
        print("✅ Agendamento configurado")
        print(f"   Próxima execução: {schedule.next_run()}")
    else:
        print("⚠️ Agendamento não está habilitado")
    print()
    
    print("=" * 60)
    print("✅ Testes concluídos!")
    print("=" * 60)
    print()
    print("Para iniciar o agendador em modo daemon:")
    print("  scheduler = MessageScheduler()")
    print("  scheduler.start()")
    print()
    print("Para parar:")
    print("  scheduler.stop()")
