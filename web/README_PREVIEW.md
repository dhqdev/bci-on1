# Preview - Arquitetura Web Moderna OXCASH

Este é um exemplo funcional da arquitetura web proposta para o sistema OXCASH.

## O que foi implementado

### Backend (Python/Flask)
- ✅ API REST completa com endpoints para boletos, cotas, histórico
- ✅ WebSocket (Socket.IO) para atualizações em tempo real
- ✅ Integração com Supabase (banco de dados PostgreSQL)
- ✅ Simulação de automação rodando em background
- ✅ Sistema de eventos para comunicação em tempo real

### Frontend (HTML/CSS/JS)
- ✅ Dashboard moderno e responsivo
- ✅ Cards estatísticos animados
- ✅ Tabela de histórico em tempo real
- ✅ Feed de atividades ao vivo
- ✅ Controles de automação (iniciar/parar)
- ✅ Atualizações automáticas via WebSocket

### Banco de Dados (Supabase)
- ✅ Tabela `boletos`
- ✅ Tabela `cotas`
- ✅ Tabela `historico_execucoes`
- ✅ Tabela `automacao_status`
- ✅ Row Level Security (RLS) configurado
- ✅ Índices para performance

---

## Como executar

### Opção 1: Linux/Mac
```bash
cd web
./run_preview.sh
```

### Opção 2: Windows
```bash
cd web
run_preview.bat
```

### Opção 3: Manual
```bash
# Instalar dependências
pip install flask flask-socketio flask-cors supabase python-socketio[client]

# Executar
cd web
python app_preview.py
```

---

## Acessar a prévia

Após iniciar o servidor, acesse:

- **Dashboard**: http://localhost:5001
- **API Boletos**: http://localhost:5001/api/boletos
- **API Cotas**: http://localhost:5001/api/cotas
- **API Histórico**: http://localhost:5001/api/historico
- **API Status**: http://localhost:5001/api/automation/status

---

## Funcionalidades Demonstradas

### 1. Dashboard em Tempo Real
- Cards estatísticos com dados do banco
- Gráficos e métricas atualizadas
- Design moderno e animado

### 2. Controle de Automações
- Botões para iniciar automação Dia 08 ou 16
- Simulação de processamento de tarefas
- Atualizações em tempo real do progresso

### 3. WebSocket em Ação
- Eventos enviados do backend para frontend
- Feed de atividades atualizado instantaneamente
- Notificações de tarefas concluídas

### 4. API REST
- Endpoints para todas as operações
- Dados armazenados em Supabase
- Respostas em JSON

---

## Como funciona

### 1. Iniciar Automação
```
Usuário clica "Iniciar Dia 08"
    ↓
Frontend envia POST /api/automation/start
    ↓
Backend cria thread Python em background
    ↓
Thread simula processamento de 10 tarefas
    ↓
Para cada tarefa:
    - Envia evento WebSocket 'automation_progress'
    - Frontend recebe e atualiza interface
    - Salva no banco de dados
    - Envia evento 'task_completed'
    ↓
Ao final:
    - Envia evento 'automation_complete'
    - Atualiza status no banco
```

### 2. Atualizações em Tempo Real
```
Backend Python (Thread)
    ↓
Emite evento via Socket.IO
    ↓
Todos os clientes conectados recebem
    ↓
JavaScript atualiza interface
    ↓
Usuário vê mudança instantaneamente
```

---

## Estrutura de Arquivos

```
web/
├── app_preview.py                  # Backend Flask + API + WebSocket
├── templates/
│   └── preview_dashboard.html      # Frontend moderno
├── run_preview.sh                  # Script Linux/Mac
├── run_preview.bat                 # Script Windows
└── README_PREVIEW.md               # Este arquivo
```

---

## Próximos Passos (Produção)

Para integrar com o sistema real:

1. **Substituir simulação por automação real**
   ```python
   # No app_preview.py, linha ~240
   # Trocar simulate_automation() por:
   from automation.cycle_orchestrator import executar_ciclo_completo

   def run_real_automation(dia, driver):
       # Usar suas funções reais
       board_data = extract_complete_board(driver)
       stats = executar_ciclo_completo(driver, board_data, progress_callback)
   ```

2. **Adicionar autenticação**
   - Login com senha
   - Sessões de usuário
   - Proteção de rotas

3. **Melhorar RLS no Supabase**
   - Políticas por usuário
   - Controle de acesso por empresa

4. **Deploy em produção**
   - Usar servidor WSGI (Gunicorn)
   - Configurar HTTPS
   - Deploy em cloud (Heroku, Railway, etc)

---

## Vantagens desta Arquitetura

✅ **Mantém 100% do código Python**
- Todas as automações continuam funcionando
- Selenium rodando normalmente
- Nenhuma reescrita necessária

✅ **Interface Moderna**
- Acesso de qualquer lugar
- Mobile-friendly
- Atualizações em tempo real

✅ **Escalável**
- Múltiplos usuários simultâneos
- Backend robusto
- Banco de dados profissional

✅ **Fácil Manutenção**
- Código organizado
- Separação frontend/backend
- API bem documentada

---

## Testando a Preview

1. Inicie o servidor
2. Abra http://localhost:5001
3. Clique em "Iniciar Dia 08"
4. Observe:
   - Feed de atividades atualizando em tempo real
   - Cards estatísticos mudando
   - Histórico sendo populado
   - Nenhum refresh necessário!

---

## Tecnologias Utilizadas

- **Python 3.x** - Linguagem base
- **Flask** - Framework web
- **Flask-SocketIO** - WebSocket
- **Supabase** - Banco de dados PostgreSQL
- **Socket.IO** - Comunicação em tempo real
- **HTML5/CSS3/JavaScript** - Frontend moderno
- **Font Awesome** - Ícones

---

## Dúvidas?

Este é um exemplo completo e funcional da arquitetura proposta.
Todo o código está comentado e pode ser adaptado para suas necessidades.

O sistema mantém suas automações Python e adiciona uma interface web moderna! 🚀
