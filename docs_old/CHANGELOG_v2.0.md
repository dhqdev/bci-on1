# 📝 Changelog - BCI-ON1 v2.0

**Data:** 02 de Outubro de 2025

## 🎯 Mudanças Principais

### ✅ Versão Web Única
- **Removida** a versão desktop (Tkinter)
- **Mantida** apenas a versão web moderna (Flask)
- Interface mais moderna, responsiva e acessível

### 🚀 Instalação Simplificada

#### Melhorias no `setup-windows.bat`:
1. **Detecção de permissões de administrador**
2. **Menu de opções** quando diretório já existe:
   - `[1]` Atualizar projeto (git pull)
   - `[2]` Remover e reinstalar
   - `[3]` Cancelar
3. **Melhor tratamento de erros** com mensagens claras
4. **Criação automática de atalho** na área de trabalho
5. **Validações aprimoradas** para Git, Python e Chrome

#### Atalho Automático:
- Arquivo `BCI-ON1-Web.bat` criado na área de trabalho
- Um clique para iniciar o sistema
- Ativa ambiente virtual automaticamente
- Abre diretamente a interface web

### 📋 Arquivos Modificados

#### 1. `run.bat`
- Agora exibe aviso de que versão desktop foi desativada
- Orienta usuário para usar versão web

#### 2. `main.py`
- Código de automação local removido
- Exibe mensagem de redirecionamento para web

#### 3. `main_gui.py`
- Interface Tkinter desativada
- Exibe instruções para usar versão web

#### 4. `setup-windows.bat`
- Menu interativo com 3 opções
- Criação automática de atalho na área de trabalho
- Melhor tratamento de erros
- Validação de permissões
- Opção de atualizar sem reinstalar

#### 5. `web/run_web.bat`
- Melhorado com mais validações
- Mensagens mais claras
- Verifica ambiente virtual antes de iniciar

#### 6. `README.md`
- Atualizado para refletir apenas versão web
- Destaque para atalho da área de trabalho
- Instruções simplificadas

### 📁 Novos Arquivos

#### 1. `INICIAR_WEB.bat`
- Script auxiliar para iniciar a versão web
- Detecta automaticamente o diretório do projeto
- Validações de ambiente

#### 2. `TROUBLESHOOTING.md`
- Guia completo de solução de problemas
- Erros comuns e suas soluções
- Instruções de diagnóstico
- Comandos úteis para debug

#### 3. `COMO_USAR.txt`
- Guia rápido de uso
- Instalação em 1 comando
- Funcionalidades principais
- Configuração inicial

### 🔧 Melhorias Técnicas

1. **Tratamento de erros robusto:**
   - Tentativas múltiplas de remoção de diretório
   - Mensagens claras sobre o que fazer
   - Timeouts para evitar conflitos

2. **Validações aprimoradas:**
   - Verifica se está rodando como admin (recomendado)
   - Valida cada passo da instalação
   - Verifica conexão com GitHub

3. **Experiência do usuário:**
   - Cores no terminal (color 0B - verde água)
   - Mensagens formatadas e claras
   - Progresso visual de cada etapa
   - Atalho na área de trabalho para fácil acesso

### 📊 Comparação: Antes vs Depois

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Interfaces** | Desktop + Web | Apenas Web |
| **Instalação** | Script básico | Script interativo com opções |
| **Atalho** | Manual | Automático na área de trabalho |
| **Atualização** | Tinha que reinstalar tudo | Opção de git pull |
| **Erros** | Mensagens genéricas | Mensagens detalhadas + troubleshooting |
| **Uso** | Navegar até pasta e executar | 1 clique no atalho |

### 🎯 Benefícios

✅ **Mais fácil de usar** - Um clique e pronto!  
✅ **Menos confusão** - Apenas uma interface (web)  
✅ **Mais moderno** - Interface web responsiva  
✅ **Melhor suporte** - Guia de troubleshooting completo  
✅ **Atualização fácil** - Git pull sem reinstalar  
✅ **Menos erros** - Validações e tratamento robusto  

### 🚀 Como Usar Agora

#### Instalação (1 comando):
```powershell
irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/setup-windows.bat -OutFile setup.bat; .\setup.bat
```

#### Executar:
1. Clique no atalho `BCI-ON1-Web.bat` na área de trabalho
2. Abra: http://localhost:5000

#### Atualizar:
```powershell
cd %USERPROFILE%\bci-on1
git pull origin main
```

### 📌 Notas Importantes

- ⚠️ Versão desktop **descontinuada** - apenas web
- ✅ Atalho criado **automaticamente** na instalação
- 🔄 Pode atualizar sem reinstalar (opção 1 no instalador)
- 📖 Consulte `TROUBLESHOOTING.md` em caso de problemas

---

## 🐛 Correções de Bugs

1. **Instalador travando ao remover diretório:**
   - Adicionado timeout antes de remover
   - Tentativas múltiplas de remoção
   - Mensagem clara se falhar

2. **Ambiente virtual não encontrado:**
   - Validação antes de executar
   - Mensagem de erro clara
   - Instrução de como corrigir

3. **Porta 5000 ocupada:**
   - Documentado no troubleshooting
   - Instruções de como verificar e resolver

---

## 📅 Próximas Versões (Planejado)

- [ ] Abrir navegador automaticamente após iniciar servidor
- [ ] Configuração de porta customizável via interface
- [ ] Modo dark/light theme na interface web
- [ ] Exportação de relatórios em PDF
- [ ] API REST para integração externa

---

**Desenvolvido por:** dhqdev  
**Repositório:** https://github.com/dhqdev/bci-on1  
**Versão:** 2.0 - Web Only Edition  
**Data:** 02/10/2025
