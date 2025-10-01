# 🤖 Sistema de Automação Servopa + Todoist - CICLO COMPLETO

Sistema completo de automação com ciclo inteligente entre Servopa e Todoist para processamento automático de lances de consórcios.

## ✨ Funcionalidades Principais

### 🔄 **CICLO COMPLETO IMPLEMENTADO**
Agora o sistema faz o ciclo completo:
1. **Extrai TODAS as colunas e linhas** do board do Todoist
2. **Processa coluna por coluna, linha por linha**
3. **Alterna entre Servopa e Todoist** automaticamente
4. **Marca checkboxes** como concluído após cada lance
5. **Mantém ambas as abas abertas** durante todo o processo

## 🎯 Fluxo de Automação

```
┌─────────────────────────────────────────────────────────────┐
│                    INÍCIO DA AUTOMAÇÃO                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 1: Login no Servopa (Aba 1)                          │
│  → URL: https://www.consorcioservopa.com.br/vendas/login    │
│  → Credenciais configuradas na interface                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 2: Abre Nova Aba + Login no Todoist (Aba 2)         │
│  → URL: https://app.todoist.com/auth/login                  │
│  → Navega para projeto "Lances Servopa Outubro Dia 8"      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 3: Extração Completa do Board                        │
│  → Identifica TODAS as colunas (grupos)                     │
│  → Extrai TODAS as linhas (cotas + nomes)                   │
│  → Mapeia checkboxes para marcar depois                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 4: CICLO COMPLETO (Para cada coluna e linha)        │
│                                                              │
│  PARA CADA COLUNA (Grupo):                                  │
│    ┌──────────────────────────────────────────┐            │
│    │ PARA CADA LINHA (Cota):                  │            │
│    │                                           │            │
│    │ 1️⃣ Muda para aba SERVOPA                 │            │
│    │    → Clica em "Alterar Consórcio"        │            │
│    │    → Busca o GRUPO da coluna             │            │
│    │    → Seleciona a COTA da linha           │            │
│    │    → Navega para "Lances"                │            │
│    │    → Copia tx_lanfix → tx_lanfix_emb     │            │
│    │    → Clica "Simular Lance"               │            │
│    │    → Clica "Registrar"                   │            │
│    │                                           │            │
│    │ 2️⃣ Muda para aba TODOIST                 │            │
│    │    → Marca CHECKBOX como concluído ✅    │            │
│    │                                           │            │
│    │ 3️⃣ Volta para aba SERVOPA                │            │
│    │    → Pronto para próxima linha           │            │
│    │                                           │            │
│    └──────────────────────────────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  🎉 AUTOMAÇÃO CONCLUÍDA                                     │
│  → Relatório de estatísticas                                │
│  → Navegador mantido aberto para verificação               │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Estrutura do Board do Todoist

```
Projeto: "Lances Servopa Outubro Dia 8"

┌──────────────┬──────────────┬──────────────┐
│  Coluna 1    │  Coluna 2    │  Coluna 3    │
│  1550-dia 8  │  1620-dia 8  │  1730-dia 8  │
├──────────────┼──────────────┼──────────────┤
│ □ 1874       │ □ 2145       │ □ 3001       │
│   Gil Zanobia│   João Silva │   Maria Lima │
├──────────────┼──────────────┼──────────────┤
│ □ 1123       │ □ 2067       │ □ 3045       │
│   Josué      │   Ana Costa  │   Pedro Alves│
├──────────────┼──────────────┼──────────────┤
│ □ 1065       │ □ 2189       │ □ 3112       │
│   Gil Zanobia│   Lucas Pena │   Carla Dias │
└──────────────┴──────────────┴──────────────┘

Cada COLUNA = Um GRUPO de consórcio
Cada LINHA = Uma COTA + Nome do cliente
```

## 🚀 Como Usar

### 1️⃣ Instalação (Primeira vez)

**Windows:**
```bash
# Execute como administrador
install.bat
```

**Linux/Mac:**
```bash
bash install.sh
```

### 2️⃣ Configurar Credenciais

1. Execute o sistema:
   ```bash
   python main_gui.py
   ```

2. Vá para a aba **"🔐 Credenciais"**

3. Configure suas credenciais:

   **Servopa:**
   - Usuário: `26.350.659/0001-61`
   - Senha: `43418`

   **Todoist:**
   - Usuário: `oscarifn6@gmail.com`
   - Senha: `spfctri12`

4. Clique em **"💾 Salvar"**

### 3️⃣ Executar Automação

1. Vá para a aba **"🚀 Automação"**

2. Clique em **"🚀 Iniciar"**

3. Acompanhe o progresso:
   - **Status Cards**: Status de cada componente
   - **Barra de Progresso**: Progresso geral
   - **Log Detalhado**: Cada ação executada

4. Aguarde a conclusão:
   - O navegador **permanecerá aberto** ao final
   - Você pode **verificar manualmente** cada lance
   - **Feche o navegador** quando terminar

## 📁 Estrutura do Projeto

```
auto-oxbci/
├── 🔐 auth/
│   ├── servopa_auth.py        # Login Servopa
│   ├── todoist_auth.py        # Login Todoist
│   └── __init__.py
│
├── 🤖 automation/
│   ├── servopa_automation.py  # Automação básica (legado)
│   ├── servopa_lances.py      # 🆕 Automação completa de lances
│   ├── cycle_orchestrator.py  # 🆕 Orquestrador do ciclo
│   └── __init__.py
│
├── 🖥️ ui/
│   ├── automation_gui.py      # Interface antiga (legado)
│   ├── modern_automation_gui.py # Interface moderna
│   └── __init__.py
│
├── ⚙️ utils/
│   ├── config.py              # Configurações
│   ├── todoist_board_extractor.py # 🆕 Extrator completo do board
│   └── __init__.py
│
├── 📄 main_gui.py             # Executável principal
├── 📄 main.py                 # CLI (linha de comando)
├── 📄 requirements.txt        # Dependências
├── 📄 credentials.json        # Credenciais salvas
└── 📖 README.md               # Esta documentação
```

## 🆕 Módulos do Sistema

### `utils/todoist_board_extractor.py`
- ✅ Extrai **TODAS** as colunas (seções) do board
- ✅ Extrai **TODAS** as tarefas (linhas) de cada coluna
- ✅ Mapeia checkboxes para marcar depois
- ✅ Retorna estrutura completa: grupos, cotas, nomes

### `automation/servopa_lances.py`
- ✅ Função `alterar_consorcio()` - Volta para busca
- ✅ Função `buscar_grupo()` - Busca grupo específico
- ✅ Função `selecionar_cota()` - Encontra e seleciona cota
- ✅ Função `navegar_para_lances()` - Vai para página de lances
- ✅ Função `executar_lance()` - Executa lance completo
- ✅ Função `processar_lance_completo()` - Orquestra tudo

### `automation/cycle_orchestrator.py`
- ✅ Função `switch_to_window_with_url()` - Alterna entre abas
- ✅ Função `executar_ciclo_completo()` - Loop principal
- ✅ Função `executar_automacao_completa()` - Ponto de entrada

## 📊 Interface Visual

### Status Cards
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   Servopa    │   Todoist    │   Cliente    │    Lances    │
│  ✅ Conectado│  ✅ Extraído │ ⏳ Processando│ ⏳ Processando│
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### Log Colorido
```
[10:30:15] 🚀 Iniciando sistema de automação completo...
[10:30:20] ✅ Login Servopa concluído!
[10:30:35] ✅ Login Todoist concluído!
[10:30:45] 📊 Board extraído: 3 colunas, 9 tarefas
[10:30:50] ┌────────────────────────────────────────┐
[10:30:50] │ COLUNA 1/3: 1550 - dia 8              │
[10:30:50] │ Grupo: 1550                            │
[10:30:50] │ Tarefas: 3                             │
[10:30:50] └────────────────────────────────────────┘
[10:30:55] ┌─ Tarefa 1/3 ─────────────────────────
[10:30:55] │  📝 Cota: 1874
[10:30:55] │  👤 Nome: Gil Zanobia
[10:30:55] └──────────────────────────────────────
[10:31:00] 🌐 [SERVOPA] Mudando para aba do Servopa...
[10:31:05] 🎯 [SERVOPA] Processando lance: Grupo 1550 - Cota 1874
[10:31:20] ✅ [SERVOPA] Lance registrado com sucesso!
[10:31:22] 📋 [TODOIST] Mudando para aba do Todoist...
[10:31:25] ✅ [TODOIST] Tarefa marcada como concluída!
[10:31:27] 🎉 Tarefa 1/3 concluída com sucesso!
[10:31:27] 📊 Progresso: 1/9 tarefas
```

## ⚙️ Configurações

### Credenciais
- Salvas em `credentials.json`
- Formato:
  ```json
  {
    "servopa": {
      "usuario": "26.350.659/0001-61",
      "senha": "43418"
    },
    "todoist": {
      "usuario": "oscarifn6@gmail.com",
      "senha": "spfctri12"
    }
  }
  ```

### Timeouts
- Timeout padrão: **20 segundos**
- Aguarda login Todoist: **10 segundos**
- Delays entre ações: **1-3 segundos**
- Digitação natural: **0.1s por caractere**

## 🛠️ Requisitos

- ✅ Python 3.8+
- ✅ Google Chrome
- ✅ Conexão com internet
- ✅ Credenciais válidas Servopa e Todoist

## 📦 Dependências

```txt
selenium>=4.15.0
webdriver-manager>=4.0.1
tkinter (incluído no Python)
```

## 🔧 Desenvolvimento

### Testar Módulos Individualmente

**Testar extrator do Todoist:**
```python
from utils.todoist_board_extractor import extract_complete_board
# Executar após login...
```

**Testar automação de lances:**
```python
from automation.servopa_lances import processar_lance_completo
result = processar_lance_completo(driver, "1550", "1123")
```

**Testar ciclo completo:**
```python
from automation.cycle_orchestrator import executar_automacao_completa
stats = executar_automacao_completa(driver)
```

## ⚠️ Tratamento de Erros

- ✅ Timeouts configuráveis
- ✅ Logs detalhados com timestamps
- ✅ Navegador mantido aberto para debug
- ✅ Continua próxima tarefa após erro
- ✅ Relatório final com estatísticas

## 📈 Estatísticas

Ao final da execução, você verá:
```
═══════════════════════════════════════════════════════════
🎉 CICLO COMPLETO FINALIZADO!
═══════════════════════════════════════════════════════════
✅ Tarefas concluídas: 8/9
❌ Tarefas com falha: 1/9
📊 Taxa de sucesso: 88.9%
═══════════════════════════════════════════════════════════
```

## 🎨 Cores da Interface

- 🔵 **Azul** - Informações e processos em andamento
- 🟢 **Verde** - Sucessos e confirmações
- 🟡 **Amarelo** - Avisos e atenção
- 🔴 **Vermelho** - Erros e falhas
- ⚫ **Cinza** - Timestamps e dados secundários

## 🚦 Estados dos Cards

| Ícone | Significado |
|-------|-------------|
| ⏳ | Em processamento |
| ✅ | Concluído com sucesso |
| ❌ | Erro ou falha |
| 🔄 | Aguardando ou recarregando |

## 💡 Dicas

1. **Primeira execução**: Verifique se as credenciais estão corretas
2. **Erros de timeout**: Aumente o valor em `TIMEOUT` nos módulos
3. **Debug**: O navegador fica aberto ao final para verificação manual
4. **Performance**: Recomenda-se executar em horários de menor tráfego
5. **Backup**: As credenciais ficam salvas localmente

## 📞 Suporte

Se encontrar problemas:
1. Verifique o log detalhado na interface
2. Confirme que as credenciais estão corretas
3. Teste conexão com internet
4. Verifique se o Chrome está atualizado

---

**Versão:** 4.0 - Sistema de Ciclo Completo  
**Data:** Setembro 2025  
**Status:** ✅ Produção
