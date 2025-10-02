# 🌐 Interface Web Moderna - OXCASH

## 🎨 Visão Geral

Interface web moderna e profissional para o sistema de automação OXCASH, com dashboards interativos, gráficos em tempo real e controle completo via navegador.

## ✨ Funcionalidades

### 📊 **Dashboard Principal**
- Cards com estatísticas em tempo real
- Gráficos de pizza (sucesso/falha/parado)
- Status das automações Dia 8 e Dia 16
- Ações rápidas para todas as páginas

### 🤖 **Automação Dia 8 e Dia 16**
- Controles de start/stop
- Logs em tempo real via WebSocket
- Barra de progresso visual
- Status de cada componente (Servopa, Todoist, Cliente, Lances)

### 📱 **WhatsApp**
- Interface lado-a-lado para Dia 8 e Dia 16
- Configuração da Evolution API (URL bloqueada)
- Disparo em massa personalizado
- Logs de envio compartilhados

### 📈 **Histórico**
- Visualização de todos os lances processados
- Tabs separadas para Dia 8 e Dia 16
- Tabelas com protocolos e status
- Atualização automática

### 🔐 **Credenciais**
- Gerenciamento seguro de acessos
- Servopa e Todoist
- Validação e salvamento

## 🚀 Como Usar

### **Linux/Mac:**
```bash
./run_web.sh
```

### **Windows:**
```bat
run_web.bat
```

O servidor será iniciado em: **http://localhost:5000**

## 🛠️ Tecnologias

- **Backend:** Flask + Flask-SocketIO
- **Frontend:** Bootstrap 5 + Chart.js
- **Comunicação:** WebSocket (tempo real)
- **Design:** CSS3 + Animações
- **Ícones:** Font Awesome

## 📁 Estrutura

```
web/
├── app.py                 # Servidor Flask principal
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Dashboard
│   ├── automation_dia8.html
│   ├── automation_dia16.html
│   ├── whatsapp.html
│   ├── history.html
│   └── credentials.html
└── static/               # Arquivos estáticos
    ├── css/
    │   └── style.css     # Estilos customizados
    └── js/
        └── (futuros scripts)
```

## 🎯 Características

### ✅ **Design Moderno**
- Interface limpa e profissional
- Animações suaves
- Responsivo (funciona em mobile)
- Tema com cores da marca

### ⚡ **Tempo Real**
- Logs instantâneos via WebSocket
- Progresso ao vivo
- Status atualizado automaticamente
- Sem necessidade de refresh

### 📊 **Visualizações**
- Gráficos de pizza interativos
- Cards com métricas importantes
- Progress bars animadas
- Badges de status

### 🔒 **Segurança**
- URL da API bloqueada
- Credenciais mascaradas
- Validações no backend
- CORS configurado

## 🔄 Compatibilidade

- **Navegadores:** Chrome, Firefox, Edge, Safari
- **Sistema:** Linux, Mac, Windows
- **Python:** 3.8+
- **Rede:** Funciona em localhost (127.0.0.1 ou localhost:5000)

## 📝 Notas

1. **Mantém Tudo:** A interface web NÃO substitui a interface desktop (Tkinter), ambas funcionam
2. **Zero Mudanças:** Nenhuma funcionalidade foi alterada, apenas adicionada nova interface
3. **Opcional:** Você pode usar a interface desktop normal (`./run.sh`) ou a web (`./run_web.sh`)

## 🆘 Troubleshooting

**Erro: Porta 5000 em uso**
```bash
# Linux/Mac
sudo lsof -i :5000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Dependências não instaladas:**
```bash
pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio
```

## 🎉 Próximas Melhorias

- [ ] Tema escuro/claro toggle
- [ ] Notificações push
- [ ] Exportação de relatórios
- [ ] Filtros avançados no histórico
- [ ] Dashboard de performance
- [ ] Multi-idioma

---

**Desenvolvido para OXCASH** 🏆
*Interface moderna, funcionalidade completa*
