# Arquitetura Web Moderna - Sistema OXCASH

## Visão Geral

O sistema mantém o **Python como backend** para todas as automações (Selenium, Servopa, Todoist) e adiciona uma **interface web moderna** com atualizações em tempo real.

---

## Stack Tecnológica

### Backend (Atual + Melhorado)
- **Python/Flask** - API REST + WebSockets
- **Selenium** - Automações de navegador
- **Supabase** - Banco de dados PostgreSQL
- **SocketIO** - Comunicação em tempo real

### Frontend (Novo)
- **HTML5/CSS3/JavaScript** - Interface moderna
- **Socket.IO Client** - Atualizações em tempo real
- **Fetch API** - Comunicação com backend
- **Responsive Design** - Mobile-first

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         NAVEGADOR                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  INTERFACE WEB (HTML/CSS/JS)                               │ │
│  │  - Dashboard com cards animados                            │ │
│  │  - Controles de automação                                  │ │
│  │  - Visualização de dados em tempo real                     │ │
│  │  - Histórico de execuções                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↕ HTTP REST + WebSocket            │
└─────────────────────────────────────────────────────────────────┘
                                 ↕
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND PYTHON (Flask)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  API REST (/api/*)                                         │ │
│  │  - GET /api/boletos    → Lista boletos                     │ │
│  │  - GET /api/cotas      → Lista cotas                       │ │
│  │  - POST /api/automation/start → Inicia automação           │ │
│  │  - POST /api/automation/stop  → Para automação             │ │
│  │  - GET /api/history    → Histórico de execuções            │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  WebSocket (SocketIO)                                      │ │
│  │  - Envia atualizações em tempo real para frontend          │ │
│  │  - Emite eventos: 'progress', 'status_change', 'complete'  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  AUTOMAÇÕES (Threads separadas)                            │ │
│  │  - Selenium WebDriver                                      │ │
│  │  - Servopa Automation                                      │ │
│  │  - Todoist Integration                                     │ │
│  │  - Lances Processing                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↕                                  │
└─────────────────────────────────────────────────────────────────┘
                                 ↕
┌─────────────────────────────────────────────────────────────────┐
│                     BANCO DE DADOS                               │
│                        (Supabase)                                │
│  - Boletos                                                       │
│  - Cotas                                                         │
│  - Clientes                                                      │
│  - Histórico de Execuções                                        │
│  - Status de Automações                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fluxo de Funcionamento

### 1. Usuário inicia automação

```javascript
// Frontend envia requisição
fetch('/api/automation/start', {
  method: 'POST',
  body: JSON.stringify({ dia: '08' })
})
```

### 2. Backend processa em background

```python
# Backend cria thread e retorna imediatamente
@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    dia = request.json.get('dia')

    # Inicia automação em thread separada
    thread = threading.Thread(
        target=run_automation_with_progress,
        args=(dia, socketio)
    )
    thread.start()

    return jsonify({'success': True, 'message': 'Automação iniciada'})
```

### 3. Atualizações em tempo real

```python
# Durante a execução, envia atualizações via WebSocket
def run_automation_with_progress(dia, socketio):
    for cota in cotas:
        # Processa cota
        result = processar_lance(cota)

        # Envia atualização para frontend
        socketio.emit('progress', {
            'cota': cota,
            'status': 'completed',
            'message': 'Lance registrado com sucesso'
        })
```

### 4. Frontend recebe e atualiza interface

```javascript
// Frontend escuta eventos e atualiza UI dinamicamente
socket.on('progress', (data) => {
    updateProgressBar(data);
    addHistoryEntry(data);
    showNotification(data.message);
});
```

---

## Vantagens desta Arquitetura

### ✅ Mantém as Automações
- Todo código Python/Selenium continua funcionando
- Nenhuma lógica de automação precisa ser reescrita

### ✅ Interface Moderna
- Design responsivo (funciona em mobile)
- Atualizações em tempo real sem refresh
- Animações suaves e feedback visual

### ✅ Escalável
- Backend pode processar múltiplas automações
- Frontend leve (apenas HTML/CSS/JS)
- Banco de dados robusto (Supabase)

### ✅ Separação de Responsabilidades
- **Backend**: Lógica de negócio e automações
- **Frontend**: Apresentação e interação
- **Database**: Persistência de dados

---

## Exemplo de Código

### Backend API Endpoint
```python
@app.route('/api/boletos', methods=['GET'])
def get_boletos():
    dia = request.args.get('dia')  # '08' ou '16'

    # Busca no banco de dados
    boletos = supabase.table('boletos')\
        .select('*')\
        .eq('dia', dia)\
        .execute()

    return jsonify({
        'success': True,
        'data': boletos.data
    })
```

### Frontend Requisição
```javascript
async function loadBoletos(dia) {
    const response = await fetch(`/api/boletos?dia=${dia}`);
    const data = await response.json();

    if (data.success) {
        renderBoletosTable(data.data);
    }
}
```

### WebSocket em Tempo Real
```python
# Backend emite evento
socketio.emit('boleto_updated', {
    'boleto_id': 123,
    'status': 'completed',
    'protocolo': 'ABC-123-456'
})
```

```javascript
// Frontend escuta e atualiza
socket.on('boleto_updated', (data) => {
    const row = document.querySelector(`#boleto-${data.boleto_id}`);
    row.classList.add('completed');
    row.querySelector('.status').textContent = 'Concluído';
});
```

---

## Comparação: Antes vs Depois

### ANTES (Desktop GUI)
- Aplicação PyQt/Tkinter
- Executa localmente
- Uma instância por máquina
- Interface desktop tradicional

### DEPOIS (Web App)
- Aplicação web moderna
- Acessa de qualquer lugar
- Múltiplos usuários simultâneos
- Interface responsiva e moderna
- Atualizações em tempo real
- Acesso mobile

---

## Próximos Passos

1. **Migrar dados para Supabase**
   - Criar tabelas (boletos, cotas, clientes, etc)
   - Implementar Row Level Security (RLS)

2. **Criar endpoints REST**
   - CRUD de boletos
   - CRUD de cotas
   - Controle de automações

3. **Implementar WebSocket**
   - Eventos de progresso
   - Status de automações
   - Notificações

4. **Melhorar interface**
   - Dashboard com gráficos
   - Tabelas interativas
   - Filtros e busca

---

## Exemplo Prático: Controle de Automação

```html
<!-- Botão de controle -->
<button id="startAutomation" class="btn-primary">
    <i class="fas fa-play"></i> Iniciar Automação Dia 08
</button>

<div id="progressContainer" style="display: none;">
    <div class="progress-bar">
        <div id="progressFill" style="width: 0%"></div>
    </div>
    <div id="currentTask">Aguardando...</div>
</div>
```

```javascript
// Controla automação
document.getElementById('startAutomation').onclick = async () => {
    // Envia comando para backend
    const response = await fetch('/api/automation/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dia: '08' })
    });

    if (response.ok) {
        document.getElementById('progressContainer').style.display = 'block';
    }
};

// Recebe atualizações em tempo real
socket.on('progress', (data) => {
    const percent = (data.completed / data.total) * 100;
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('currentTask').textContent =
        `Processando: ${data.current_cota} (${data.completed}/${data.total})`;
});

socket.on('automation_complete', (data) => {
    showNotification('Automação concluída!', 'success');
    document.getElementById('progressContainer').style.display = 'none';
});
```

---

## Conclusão

Esta arquitetura mantém **100% das automações Python** funcionando enquanto adiciona uma **interface web moderna** com:

- ✅ Acesso remoto
- ✅ Atualizações em tempo real
- ✅ Design responsivo
- ✅ Múltiplos usuários
- ✅ Escalabilidade
- ✅ Melhor experiência de usuário

O backend Python continua fazendo todo o trabalho pesado (Selenium, automações), e a web serve apenas como interface visual moderna.
