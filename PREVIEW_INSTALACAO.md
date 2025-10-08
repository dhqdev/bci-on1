# Como Executar a Preview da Arquitetura Web

## Passo 1: Instalar Dependências

```bash
pip install flask flask-socketio flask-cors supabase python-socketio
```

Se você estiver usando `pip3`:
```bash
pip3 install flask flask-socketio flask-cors supabase python-socketio
```

## Passo 2: Executar o Servidor

### Linux/Mac:
```bash
cd web
chmod +x run_preview.sh
./run_preview.sh
```

### Windows:
```cmd
cd web
run_preview.bat
```

### Manualmente:
```bash
cd web
python3 app_preview.py
```

## Passo 3: Acessar a Interface

Abra seu navegador em:

**http://localhost:5001**

---

## O que você verá:

1. **Dashboard Moderno**
   - Cards estatísticos animados
   - Dados em tempo real
   - Design responsivo

2. **Controles de Automação**
   - Botões para iniciar/parar automações
   - Simulação de processamento
   - Atualizações instantâneas

3. **Histórico em Tempo Real**
   - Tabela atualizada automaticamente
   - Feed de atividades ao vivo
   - Eventos via WebSocket

---

## Teste Rápido

1. Abra http://localhost:5001
2. Clique em "Iniciar Dia 08"
3. Observe o feed de atividades atualizando em tempo real
4. Veja os cards estatísticos mudando automaticamente
5. Confira o histórico sendo populado

**Tudo sem dar refresh na página!**

---

## Arquivos Criados

```
web/
├── app_preview.py                    # Backend Flask + API + WebSocket
├── templates/
│   └── preview_dashboard.html        # Frontend moderno
├── run_preview.sh                    # Script para Linux/Mac
├── run_preview.bat                   # Script para Windows
└── README_PREVIEW.md                 # Documentação completa
```

**Banco de Dados:**
- 4 tabelas criadas no Supabase
- Dados persistidos automaticamente
- RLS (Row Level Security) configurado

---

## Endpoints da API

- `GET /api/boletos` - Lista todos os boletos
- `GET /api/cotas` - Lista todas as cotas
- `GET /api/historico` - Histórico de execuções
- `GET /api/automation/status` - Status das automações
- `POST /api/automation/start` - Inicia automação
- `POST /api/automation/stop` - Para automação

---

## WebSocket Events

Frontend recebe eventos em tempo real:

- `connected` - Conexão estabelecida
- `automation_progress` - Progresso da automação
- `task_completed` - Tarefa concluída
- `automation_complete` - Automação finalizada
- `automation_stopped` - Automação parada

---

## Estrutura da Arquitetura

```
┌─────────────────┐
│   NAVEGADOR     │  ← Interface web moderna
│  localhost:5001 │
└────────┬────────┘
         │ HTTP REST + WebSocket
         ↓
┌─────────────────┐
│  FLASK BACKEND  │  ← Python mantém automações
│   app_preview   │
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│    SUPABASE     │  ← PostgreSQL database
│   (PostgreSQL)  │
└─────────────────┘
```

---

## Próximo Passo

Após testar a preview e gostar do resultado, você pode:

1. Integrar com suas automações reais do Selenium
2. Adicionar autenticação de usuários
3. Fazer deploy em produção
4. Adicionar mais funcionalidades

Esta preview mantém **100% do seu código Python** e adiciona apenas a interface web moderna!
