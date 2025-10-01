# ⚡ GUIA RÁPIDO - INÍCIO IMEDIATO

## 🚀 3 Passos para Começar

### 1️⃣ INSTALAR (2 minutos)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
bash install.sh
```

✅ Instala Python, Chrome, dependências automaticamente

---

### 2️⃣ CONFIGURAR (1 minuto)

```bash
python main_gui.py
```

Na interface:
1. Clique na aba **"🔐 Credenciais"**
2. Preencha os campos (já vêm preenchidos)
3. Clique **"💾 Salvar"**

---

### 3️⃣ EXECUTAR (Click único)

1. Clique na aba **"🚀 Automação"**
2. Clique **"🚀 Iniciar"**
3. Aguarde e acompanhe os logs

**Pronto!** 🎉

---

## 🎥 O Que Acontece

```
┌────────────────────────────────────────┐
│ 1. Abre Chrome com 2 abas             │
│    • Servopa (login automático)       │
│    • Todoist (login automático)       │
├────────────────────────────────────────┤
│ 2. Extrai board do Todoist            │
│    • Todas as colunas (grupos)        │
│    • Todas as linhas (cotas)          │
├────────────────────────────────────────┤
│ 3. Para CADA linha:                   │
│    a) Vai para SERVOPA                │
│       • Busca grupo                   │
│       • Seleciona cota                │
│       • Faz o lance                   │
│    b) Vai para TODOIST                │
│       • Marca checkbox ✅             │
│    c) Volta para SERVOPA              │
│       • Próxima linha                 │
├────────────────────────────────────────┤
│ 4. Mostra estatísticas                │
│    • Quantas concluídas               │
│    • Quantas falhadas                 │
│    • Taxa de sucesso                  │
└────────────────────────────────────────┘
```

---

## 📋 Checklist Pré-Execução

Antes de clicar "Iniciar", certifique-se:

- [ ] Chrome instalado
- [ ] Internet conectada
- [ ] Credenciais salvas
- [ ] Board do Todoist tem tarefas

---

## 🎯 Durante a Execução

### O que você verá:

```
[10:30:15] 🚀 Iniciando automação...
[10:30:20] ✅ Login Servopa concluído!
[10:30:35] ✅ Login Todoist concluído!
[10:30:45] 📊 Board extraído: 3 colunas, 9 tarefas

[10:30:50] ┌─────────────────────────────────┐
[10:30:50] │ COLUNA 1/3: 1550 - dia 8       │
[10:30:50] └─────────────────────────────────┘

[10:30:55] ┌─ Tarefa 1/3 ──────────────────
[10:30:55] │  📝 Cota: 1874
[10:30:55] │  👤 Nome: Gil Zanobia
[10:31:00] 🌐 [SERVOPA] Processando lance...
[10:31:20] ✅ [SERVOPA] Lance registrado!
[10:31:22] 📋 [TODOIST] Marcando checkbox...
[10:31:25] ✅ [TODOIST] Tarefa marcada!
[10:31:27] 🎉 Tarefa concluída!
[10:31:27] 📊 Progresso: 1/9 tarefas
```

### Status Cards mostram:
```
┌──────────┬──────────┬──────────┬──────────┐
│ Servopa  │ Todoist  │ Cliente  │  Lances  │
│ ✅ OK    │ ✅ OK    │ ⏳ Proc. │ ⏳ Proc. │
└──────────┴──────────┴──────────┴──────────┘
```

---

## ⏱️ Tempo Esperado

| Tarefas | Tempo |
|---------|-------|
| 3 tarefas | ~2 min |
| 9 tarefas | ~5 min |
| 20 tarefas | ~12 min |

**Média:** ~35 segundos por tarefa

---

## 🎉 Após Conclusão

### Você verá:

```
═══════════════════════════════════════════
🎉 CICLO COMPLETO FINALIZADO!
═══════════════════════════════════════════
✅ Tarefas concluídas: 8/9
❌ Tarefas com falha: 1/9
📊 Taxa de sucesso: 88.9%
═══════════════════════════════════════════
```

### Navegador:
- ✅ Fica **aberto** para verificação
- ✅ Você pode **conferir** os lances manualmente
- ✅ **Feche** quando terminar

---

## ⚠️ Se der Erro

### Erro de Login?
1. Verifique credenciais na aba "🔐 Credenciais"
2. Teste login manual nos sites
3. Salve novamente as credenciais

### Timeout?
- Internet lenta? Aguarde mais tempo
- Sites lentos? Execute em outro horário
- Problema persiste? Veja TECHNICAL_DOCS.md

### Elemento não encontrado?
- Sites mudaram? Pode precisar atualizar código
- Veja logs detalhados
- Contate suporte

---

## 💡 Dicas Rápidas

1. **Primeira vez?** 
   - Execute com poucas tarefas primeiro
   - Acompanhe o navegador visualmente

2. **Muitas tarefas?**
   - Execute em horário de baixo tráfego
   - Considere dividir em lotes

3. **Quer automatizar mais?**
   - Veja README_USER_GUIDE.md para recursos avançados
   - TECHNICAL_DOCS.md para desenvolvedores

---

## 📞 Precisa de Ajuda?

1. **Logs na interface** - Tudo que acontece está lá
2. **README_USER_GUIDE.md** - Documentação completa
3. **TECHNICAL_DOCS.md** - Detalhes técnicos
4. **test_cycle_complete.py** - Teste passo a passo

---

## 🎓 Próximos Passos

Depois de dominar o básico:

1. ✅ Ajustar timeouts se necessário
2. ✅ Personalizar credenciais
3. ✅ Automatizar tarefas recorrentes
4. ✅ Explorar funcionalidades avançadas

---

## ✨ Pronto para Começar?

```bash
python main_gui.py
```

**Boa automação!** 🚀

---

**v1.0** | **Outubro 2025** | **Status: Produção ✅**
