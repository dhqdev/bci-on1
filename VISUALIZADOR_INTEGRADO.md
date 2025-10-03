# 🖥️ Visualizador Integrado de Automação - OXCASH

## 📋 Sobre a Funcionalidade

O **Dashboard do BCI-ON1** agora possui um **visualizador integrado** que permite ver a automação acontecendo **em tempo real**, diretamente na interface web, sem precisar abrir abas externas ou ver o Chrome separadamente!

## ✨ O que mudou?

### ❌ ANTES:
- 3 cards desnecessários (WhatsApp, Histórico, Credenciais) ocupando espaço
- Automação abre Chrome em janela separada
- Usuário precisa alternar entre navegador e Chrome
- Difícil acompanhar o que está acontecendo

### ✅ AGORA:
- **Visualizador grande e integrado** no Dashboard
- **Screenshots em tempo real** do navegador Selenium (atualiza a cada 2 segundos)
- **Controles inline** (Iniciar/Parar) ao lado do visualizador
- **Log compacto** mostrando eventos em tempo real
- **Barra de progresso** integrada
- **Opção de tela cheia** para ver detalhes
- Cards removidos (já existem abas dedicadas para eles)

---

## 🎯 Funcionalidades

### 1. **Visualizador de Screenshots**
- Captura automática do navegador Selenium a cada 2 segundos
- Exibe a tela do Chrome diretamente no Dashboard
- Atualização em tempo real via WebSocket
- Qualidade ajustável e responsiva

### 2. **Controles Integrados**
- **Coluna lateral esquerda** (3 colunas):
  - Card Dia 8 com botões Iniciar/Parar
  - Card Dia 16 com botões Iniciar/Parar
  - Link para abrir em aba separada (se preferir)

- **Visualizador principal** (9 colunas):
  - Screenshot do navegador (500px de altura)
  - Log console compacto (150px)
  - Barra de progresso com status

### 3. **Logs em Tempo Real**
- Console integrado mostrando eventos
- Cores diferenciadas (sucesso=verde, erro=vermelho, info=azul)
- Scroll automático
- Limite de 50 linhas (otimização)

### 4. **Barra de Progresso**
- Atualização sincronizada com a automação
- Texto descritivo do que está sendo feito
- Visual clean e moderno

### 5. **Controles Adicionais**
- **Botão Atualizar** (⟳): Força atualização do screenshot
- **Botão Tela Cheia** (⛶): Expande o visualizador para fullscreen

---

## 🏗️ Arquitetura Técnica

### Frontend (index.html)

```html
<div class="row">
  <!-- Coluna Esquerda (3 cols) - Controles -->
  <div class="col-md-3">
    <!-- Cards Dia 8 e Dia 16 -->
  </div>
  
  <!-- Coluna Direita (9 cols) - Visualizador -->
  <div class="col-md-9">
    <div class="browser-viewer">
      <!-- Screenshot -->
      <div class="browser-screen">
        <img id="browser-screenshot" />
      </div>
      
      <!-- Log Console -->
      <div class="browser-log"></div>
      
      <!-- Progress Bar -->
      <div class="browser-progress"></div>
    </div>
  </div>
</div>
```

### Backend (app.py)

**Novo Endpoint:**
```python
@app.route('/api/automation/screenshot/<dia>', methods=['GET'])
def api_automation_screenshot(dia):
    """Retorna screenshot do navegador Selenium em base64"""
    driver = app_state.get(f'driver_{dia}')
    screenshot_png = driver.get_screenshot_as_png()
    screenshot_base64 = base64.b64encode(screenshot_png).decode('utf-8')
    return jsonify({'success': True, 'screenshot': screenshot_base64})
```

**Como funciona:**
1. Selenium já abre o Chrome durante a automação
2. Endpoint `/api/automation/screenshot/<dia>` captura tela com `driver.get_screenshot_as_png()`
3. Converte para base64 e retorna via JSON
4. Frontend faz polling a cada 2 segundos
5. Atualiza `<img>` com `data:image/png;base64,{screenshot}`

### WebSocket Integration

```javascript
// Atualiza screenshot a cada 2 segundos
setInterval(updateViewerScreenshot, 2000);

async function updateViewerScreenshot() {
    if (!currentViewerDia) return;
    
    const response = await fetch(`/api/automation/screenshot/${currentViewerDia}`);
    const data = await response.json();
    
    if (data.success && data.screenshot) {
        document.getElementById('browser-screenshot').src = 
            'data:image/png;base64,' + data.screenshot;
    }
}

// Escuta eventos de log e progresso
socket.on('log', function(data) {
    if (currentViewerDia === data.dia) {
        addViewerLog(data.message);
    }
});

socket.on('progress', function(data) {
    if (currentViewerDia === data.dia) {
        updateViewerProgress(data.value, data.message);
    }
});
```

---

## 🎨 Estilos CSS

```css
/* Visualizador de Automação */
.browser-viewer {
    height: 100%;
}

.browser-screen {
    height: 500px;
    background: #1e293b;
    display: flex;
    align-items: center;
    justify-content: center;
}

.browser-screenshot {
    width: 100%;
    height: 100%;
    object-fit: contain; /* Mantém proporção */
}

.browser-log {
    height: 150px;
    background: #0f172a;
    color: #e2e8f0;
    overflow-y: auto;
    font-family: 'Consolas', monospace;
}

.browser-progress {
    padding: 1rem;
    background: white;
}

/* Tela cheia */
.browser-viewer:fullscreen .browser-screen {
    height: calc(100vh - 300px);
}
```

---

## 🚀 Como Usar

### Opção 1: Dashboard Integrado (Recomendado)

1. Acesse: `http://localhost:5000`
2. No **Dashboard**, veja a seção "Visualizador de Automação"
3. Clique em **"Iniciar"** no card "Automação Dia 8" ou "Dia 16"
4. Acompanhe a automação em tempo real no visualizador central
5. Use **"Parar"** para interromper a qualquer momento
6. Opcionalmente, clique em **⛶ Tela Cheia** para expandir

### Opção 2: Aba Separada (Antigo Modo)

1. No card da automação, clique em **"Abrir em aba separada"**
2. Será redirecionado para `/automation/dia8` ou `/automation/dia16`
3. Funciona como antes, com controles dedicados

---

## 📊 Fluxo de Dados

```
1. Usuário clica "Iniciar Dia 8"
   ↓
2. Frontend chama POST /api/automation/start/dia8
   ↓
3. Backend inicia thread de automação
   ↓
4. Selenium abre Chrome e começa automação
   ↓
5. WebSocket envia eventos:
   - 'log': Mensagens de progresso
   - 'progress': % de conclusão
   - 'automation_status': Estado (running/stopped)
   ↓
6. Frontend faz polling a cada 2s:
   GET /api/automation/screenshot/dia8
   ↓
7. Backend captura screenshot do Chrome
   ↓
8. Retorna PNG em base64
   ↓
9. Frontend atualiza <img> com nova screenshot
   ↓
10. Usuário vê tela do Chrome em tempo real
```

---

## 🔧 Configurações e Otimizações

### Intervalo de Atualização
```javascript
// Atualiza a cada 2 segundos (pode ajustar)
setInterval(updateViewerScreenshot, 2000);
```

### Qualidade da Screenshot
```python
# No Selenium, já retorna PNG otimizado
screenshot_png = driver.get_screenshot_as_png()

# Alternativa com qualidade configurável (JPEG):
from PIL import Image
import io

screenshot = driver.get_screenshot_as_png()
img = Image.open(io.BytesIO(screenshot))
buffer = io.BytesIO()
img.save(buffer, format='JPEG', quality=70)  # 70% qualidade
screenshot_base64 = base64.b64encode(buffer.getvalue()).decode()
```

### Performance

- **Tamanho médio por screenshot**: ~100-300KB (PNG comprimido)
- **Bandwidth por minuto**: ~3-9MB (30 screenshots @ 2s cada)
- **Otimização**: Screenshots são carregadas sob demanda (só quando visualizador ativo)

### Limite de Log

```javascript
// Mantém apenas 50 linhas para evitar lag
while (console.children.length > 50) {
    console.removeChild(console.firstChild);
}
```

---

## 🐛 Troubleshooting

### Screenshot não aparece

**Causa**: Navegador não está ativo ou driver não foi inicializado

**Solução**:
1. Verifique se a automação foi iniciada
2. Verifique console do navegador (F12) para erros
3. Confira se endpoint `/api/automation/screenshot/<dia>` retorna dados

### Screenshot desatualizada

**Causa**: Intervalo de polling muito longo

**Solução**:
```javascript
// Reduza o intervalo (mas cuidado com performance)
setInterval(updateViewerScreenshot, 1000); // 1 segundo
```

### Log não atualiza

**Causa**: WebSocket desconectado

**Solução**:
1. Verifique status de conexão (badge no topo)
2. Recarregue a página
3. Verifique console: `socket.connected` deve ser `true`

### Tela cheia não funciona

**Causa**: Navegador bloqueia fullscreen automático

**Solução**:
- Usuário deve clicar manualmente no botão ⛶
- Não é possível forçar fullscreen programaticamente sem interação

---

## 📈 Melhorias Futuras

### Possíveis Enhancements:

1. **Controle de Zoom**
   - Botões +/- para aproximar screenshot
   - Útil para ver detalhes pequenos

2. **Pause/Play de Screenshot**
   - Pausar atualização para analisar frame específico
   - Útil para debug

3. **Download de Screenshot**
   - Botão para salvar screenshot atual
   - Útil para documentação/relatórios

4. **Multi-view**
   - Ver Dia 8 e Dia 16 lado a lado
   - Útil para comparar execuções

5. **Gravação de Vídeo**
   - Capturar todas screenshots e gerar MP4
   - Útil para treinamento/demo

6. **Screenshot History**
   - Slider de linha do tempo para ver screenshots passadas
   - Útil para revisar execução

7. **Overlay de Informações**
   - Mostrar dados sobre a screenshot (timestamp, ação atual, etc)
   - Útil para contexto

---

## 🎓 Casos de Uso

### 1. **Monitoramento Remoto**
- Gerente pode ver automação rodando em outra máquina
- Não precisa VNC/TeamViewer

### 2. **Debug em Tempo Real**
- Desenvolvedor vê exatamente o que Selenium está fazendo
- Identifica problemas visuais rapidamente

### 3. **Demonstração para Cliente**
- Mostrar automação funcionando em apresentação
- Mais profissional que abrir Chrome separado

### 4. **Treinamento**
- Ensinar novos usuários vendo a automação na interface
- Contexto melhor que só logs texto

### 5. **Operação Multitarefa**
- Rodar automação enquanto usa mesmo navegador para outras tarefas
- Não precisa alternar janelas

---

## 🔒 Segurança

### Considerações:

1. **Screenshots contêm dados sensíveis**
   - Números de conta, CPFs, nomes
   - Endpoint só acessível localmente (localhost)
   - Adicionar autenticação em produção

2. **Base64 pode ser grande**
   - Limite de tamanho de resposta HTTP
   - Comprimir ou usar JPEG se necessário

3. **Rate limiting**
   - Polling a cada 2s pode sobrecarregar
   - Implementar cache no backend

---

## 📝 Conclusão

O **Visualizador Integrado** transforma completamente a experiência de uso do BCI-ON1:

✅ **Antes**: Abrir Chrome separado, alternar janelas, perder contexto

✅ **Depois**: Tudo em uma tela, controles intuitivos, monitoramento em tempo real

A interface agora é **mais profissional, mais eficiente e mais fácil de usar**! 🎉

---

**Desenvolvido para o projeto BCI-ON1 - OXCASH** 🏆
