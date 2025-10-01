# 📘 Documentação Técnica - Sistema de Automação

## Arquitetura do Sistema

### Visão Geral

O sistema foi projetado com arquitetura modular, separando responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE INTERFACE                       │
│                  (ui/modern_automation_gui.py)               │
│                                                              │
│  - Interface gráfica com Tkinter                            │
│  - Sistema de abas (Automação / Credenciais)                │
│  - Logs em tempo real                                        │
│  - Gerenciamento de threads                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                 CAMADA DE ORQUESTRAÇÃO                       │
│             (automation/cycle_orchestrator.py)               │
│                                                              │
│  - Controla o fluxo principal                               │
│  - Alterna entre abas (Servopa ↔ Todoist)                  │
│  - Loop principal (coluna por coluna, linha por linha)      │
│  - Geração de estatísticas                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ↓                   ↓
┌──────────────────┐  ┌──────────────────┐
│  CAMADA SERVOPA  │  │  CAMADA TODOIST  │
├──────────────────┤  ├──────────────────┤
│ servopa_auth.py  │  │ todoist_auth.py  │
│ - Login          │  │ - Login          │
│ - Criar driver   │  │ - Nova aba       │
│                  │  │                  │
│servopa_lances.py │  │todoist_board_    │
│ - Alterar cons.  │  │  extractor.py    │
│ - Buscar grupo   │  │ - Extrai board   │
│ - Selec. cota    │  │ - Marca checkbox │
│ - Nav. lances    │  │ - Lista tarefas  │
│ - Exec. lance    │  │                  │
└──────────────────┘  └──────────────────┘
```

## Fluxo de Dados

### 1. Extração do Board (Todoist)

```python
# Estrutura retornada por extract_complete_board()
{
    'sections': [
        {
            'grupo': '1550',           # Número do grupo
            'title': '1550 - dia 8',   # Título da coluna
            'tasks': [
                {
                    'cota': '1874',                    # Número da cota
                    'nome': 'Gil Zanobia',             # Nome do cliente
                    'task_id': 'task-6cwXP9X7FfPJJwr4', # ID único
                    'checkbox_element': <WebElement>    # Referência ao checkbox
                },
                ...
            ]
        },
        ...
    ]
}
```

### 2. Processamento de Lance (Servopa)

```python
# Resultado de processar_lance_completo()
{
    'success': True/False,
    'grupo': '1550',
    'cota': '1874',
    'steps_completed': [
        'alterar_consorcio',
        'buscar_grupo',
        'selecionar_cota',
        'navegar_lances',
        'executar_lance'
    ],
    'cota_data': {
        'cota': '1874',
        'nome': 'Gil Zanobia',
        'valor': 'R$ 332.586,00',
        'grupo': '1550',
        'digito': '4',
        'contrato': '47037I07'
    }
}
```

### 3. Estatísticas Finais

```python
# Resultado de executar_ciclo_completo()
{
    'total_sections': 3,      # Total de colunas
    'total_tasks': 9,         # Total de tarefas
    'completed': 8,           # Tarefas concluídas
    'failed': 1,              # Tarefas falhadas
    'results': [              # Detalhes de cada tarefa
        {
            'section': '1550 - dia 8',
            'grupo': '1550',
            'cota': '1874',
            'nome': 'Gil Zanobia',
            'success': True,
            'error': None
        },
        ...
    ]
}
```

## Componentes Principais

### 1. `auth/servopa_auth.py`

**Responsabilidade:** Autenticação no sistema Servopa

**Funções principais:**
- `create_driver(headless=False)` - Cria instância do Chrome com configurações anti-detecção
- `login_servopa(driver, progress_callback, credentials)` - Realiza login

**Configurações:**
```python
SERVOPA_LOGIN_URL = "https://www.consorcioservopa.com.br/vendas/login"
DEFAULT_SERVOPA_LOGIN = "26.350.659/0001-61"
DEFAULT_SERVOPA_SENHA = "43418"
TIMEOUT = 20
```

**Estratégias anti-detecção:**
- Remove flags de automação
- Digitação com delay natural (0.1s por caractere)
- User-agent real
- Pauses entre ações

### 2. `auth/todoist_auth.py`

**Responsabilidade:** Autenticação no Todoist

**Funções principais:**
- `login_todoist_and_extract(driver, progress_callback, credentials)` - Login em nova aba

**IMPORTANTE:** 
- Abre nova aba usando `window.open('')`
- **NÃO fecha a aba** após extração
- Retorna à aba original do Servopa
- Mantém ambas abertas para o ciclo

### 3. `utils/todoist_board_extractor.py`

**Responsabilidade:** Extração completa do board do Todoist

**Funções principais:**

#### `extract_complete_board(driver, progress_callback)`
Extrai todas as seções e tarefas do board.

**Seletores CSS utilizados:**
```python
"section.board_section"                        # Todas as seções
"h3.board_section__title span.simple_content"  # Título da seção
"div.board_section__task_list"                 # Lista de tarefas
"div.board_task"                               # Cada tarefa
"div.task_content"                             # Número da cota
"div.task_description p"                       # Nome do cliente
"button.task_checkbox"                         # Checkbox
```

#### `mark_task_completed(driver, checkbox_element, progress_callback)`
Marca tarefa como concluída.

**Processo:**
1. Rola até o checkbox (scrollIntoView)
2. Aguarda 0.5s
3. Clica no checkbox
4. Aguarda 1s (animação)

#### `navigate_to_board_project(driver, progress_callback)`
Navega para o projeto "Lances Servopa Outubro Dia 8".

### 4. `automation/servopa_lances.py`

**Responsabilidade:** Automação completa de lances no Servopa

**Funções principais:**

#### `alterar_consorcio(driver, progress_callback)`
Clica em "Alterar Consórcio" para voltar à busca.

**Seletor:**
```python
"//a[@href='https://www.consorcioservopa.com.br/vendas/painel' 
    or contains(text(), 'Alterar Consórcio')]"
```

#### `buscar_grupo(driver, grupo_number, progress_callback)`
Busca grupo específico.

**Campos:**
- Input: `#grupofrm`
- Botão: `#btn_representante_cota`

#### `selecionar_cota(driver, cota_number, progress_callback)`
Localiza e seleciona cota na tabela.

**Estratégia:**
1. Busca todas as linhas: `table tbody tr`
2. Para cada linha, verifica 5ª coluna (cota)
3. Quando encontra, clica na linha

#### `navegar_para_lances(driver, progress_callback)`
Clica no link "Lances".

#### `executar_lance(driver, progress_callback)`
Executa o lance completo.

**Passos:**
1. Lê valor de `#tx_lanfix`
2. Copia para `#tx_lanfix_emb` (com delay)
3. Clica em `a#btn_simular`
4. Aguarda simulação (3s)
5. Clica em `a.printBt` (Registrar)
6. Aguarda registro (3s)

#### `processar_lance_completo(driver, grupo, cota, progress_callback)`
Orquestra todo o processo para uma cota.

### 5. `automation/cycle_orchestrator.py`

**Responsabilidade:** Orquestração do ciclo completo

**Funções principais:**

#### `switch_to_window_with_url(driver, url_part, progress_callback)`
Muda para aba que contém parte da URL.

**Uso:**
```python
switch_to_window_with_url(driver, "servopa")  # Vai para aba Servopa
switch_to_window_with_url(driver, "todoist")  # Vai para aba Todoist
```

#### `executar_ciclo_completo(driver, board_data, progress_callback)`
Loop principal que processa todas as tarefas.

**Algoritmo:**
```python
para cada seção em board_data['sections']:
    para cada tarefa em seção['tasks']:
        1. Muda para aba Servopa
        2. Processa lance (servopa_lances.processar_lance_completo)
        3. Muda para aba Todoist
        4. Marca checkbox (todoist_board_extractor.mark_task_completed)
        5. Volta para aba Servopa
        6. Próxima tarefa
```

**Tratamento de erros:**
- Captura exceções em cada tarefa
- Registra erro em `stats['failed']`
- Continua com próxima tarefa
- Tenta voltar para Servopa mesmo após erro

#### `executar_automacao_completa(driver, progress_callback)`
Ponto de entrada principal.

**Validações:**
- Verifica se há 2 abas abertas
- Muda para Todoist para extração
- Executa ciclo completo
- Retorna estatísticas

## Padrões de Código

### 1. Progress Callback

Todas as funções aceitam `progress_callback` opcional:

```python
def minha_funcao(driver, progress_callback=None):
    if progress_callback:
        progress_callback("📋 Mensagem de progresso")
```

### 2. Retornos

**Funções booleanas:**
```python
def fazer_algo(driver):
    try:
        # ... código ...
        return True
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro: {e}")
        return False
```

**Funções com dados:**
```python
def extrair_algo(driver):
    try:
        # ... extração ...
        return {
            'success': True,
            'data': dados
        }
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Erro: {e}")
        return None
```

### 3. Delays e Waits

**Delays fixos:**
```python
time.sleep(0.5)  # Delay curto
time.sleep(1)    # Delay médio
time.sleep(3)    # Delay longo
```

**Waits explícitos:**
```python
wait = WebDriverWait(driver, TIMEOUT)
element = wait.until(EC.presence_of_element_located((By.ID, "elemento")))
```

**Digitação natural:**
```python
for char in texto:
    input_field.send_keys(char)
    time.sleep(0.1)  # 100ms por caractere
```

## Tratamento de Erros

### Estratégias

1. **Try-Except em cada função**
   - Captura exceções específicas
   - Log detalhado do erro
   - Retorno apropriado (False, None, etc.)

2. **Continue-on-error no ciclo**
   - Erro em uma tarefa não para o ciclo
   - Próxima tarefa é processada
   - Estatísticas registram falhas

3. **Navegador mantido aberto**
   - Permite debug visual
   - Verificação manual de erros
   - Estado preservado

### Exceções Comuns

```python
TimeoutException      # Elemento não encontrado no tempo limite
NoSuchElementException  # Elemento não existe na página
WebDriverException    # Problemas com o driver
Exception             # Outros erros genéricos
```

## Performance

### Otimizações

1. **Waits explícitos vs implícitos**
   - Uso de `WebDriverWait` para esperar elementos
   - Evita `time.sleep` quando possível

2. **Reutilização do driver**
   - Uma única instância para todo o ciclo
   - Duas abas mantidas abertas
   - Troca rápida entre abas

3. **Delays naturais**
   - Simula comportamento humano
   - Evita detecção de bot
   - Reduz erro de "element not interactable"

### Métricas Esperadas

- **Login Servopa:** ~10s
- **Login Todoist:** ~15s
- **Extração board:** ~5s
- **Lance individual:** ~30s
- **Marcar checkbox:** ~2s

**Total por tarefa:** ~35s

## Segurança

### Credenciais

- Armazenadas em `credentials.json`
- Não versionadas (adicionar ao .gitignore)
- Formato JSON simples
- Senhas em texto plano (local)

### Anti-detecção

```python
# Configurações do Chrome
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Remove flag webdriver
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

## Manutenção

### Pontos de Atenção

1. **Mudanças na estrutura HTML**
   - Todoist: Classes CSS dinâmicas
   - Servopa: IDs e estrutura de tabela
   - **Solução:** Usar seletores múltiplos, XPath alternativos

2. **Timeouts**
   - Ajustar `TIMEOUT` conforme conexão
   - Considerar horário de pico
   - **Recomendação:** 20-30s

3. **Novos campos no Servopa**
   - Verificar se formulários mudaram
   - Adicionar novos campos se necessário
   - **Teste:** Executar manualmente primeiro

### Logs e Debug

**Níveis de log:**
- 🚀 Início de processo
- 📋 Informação
- ✅ Sucesso
- ⚠️ Aviso
- ❌ Erro
- 🔄 Mudança de estado
- 📊 Estatísticas

**Exemplo de log completo:**
```
[10:30:15] 🚀 Iniciando sistema...
[10:30:20] 📋 Login Servopa...
[10:30:25] ✅ Login concluído
[10:30:30] 🔄 Abrindo nova aba
[10:30:35] 📋 Login Todoist...
[10:30:45] ✅ Login concluído
[10:30:50] 📊 Board extraído: 3 colunas, 9 tarefas
[10:31:00] 🚀 Iniciando ciclo...
[10:31:05] ┌─ Tarefa 1/9
[10:31:05] │  📝 Cota: 1874
[10:31:05] │  👤 Nome: Gil Zanobia
[10:31:10] 🌐 [SERVOPA] Processando lance...
[10:31:30] ✅ [SERVOPA] Lance registrado
[10:31:32] 📋 [TODOIST] Marcando checkbox...
[10:31:35] ✅ [TODOIST] Marcado
[10:31:37] 🎉 Tarefa concluída
[10:31:37] 📊 Progresso: 1/9
```

## Extensibilidade

### Adicionar Novo Site

1. Criar módulo em `auth/`
2. Implementar função de login
3. Adicionar extração de dados
4. Atualizar `cycle_orchestrator.py`

### Adicionar Nova Funcionalidade

1. Criar função no módulo apropriado
2. Adicionar `progress_callback` opcional
3. Retornar estrutura consistente
4. Atualizar interface gráfica se necessário

### Testes

Criar testes em `test_*.py`:
```python
def test_minha_funcao():
    driver = create_driver()
    try:
        resultado = minha_funcao(driver, print)
        assert resultado is not None
        print("✅ Teste passou")
    finally:
        driver.quit()
```

## Troubleshooting

### Problemas Comuns

1. **"Element not interactable"**
   - Adicionar `time.sleep()` antes do clique
   - Usar `scrollIntoView()`
   - Verificar se elemento está visível

2. **"Timeout"**
   - Aumentar `TIMEOUT`
   - Verificar conexão
   - Confirmar que página carregou

3. **"Element not found"**
   - Verificar seletor CSS/XPath
   - Confirmar que estrutura HTML não mudou
   - Adicionar seletores alternativos

4. **Checkbox não marca**
   - Verificar se já está marcado
   - Adicionar delay maior
   - Usar JavaScript para clicar

### Debug

**Adicionar prints:**
```python
print(f"DEBUG: URL atual = {driver.current_url}")
print(f"DEBUG: Elemento encontrado = {element}")
print(f"DEBUG: Texto = {element.text}")
```

**Pausar execução:**
```python
input("DEBUG: Pressione ENTER para continuar...")
```

---

**Versão:** 1.0  
**Última atualização:** Outubro 2025
