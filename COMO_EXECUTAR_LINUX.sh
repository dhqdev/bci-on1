#!/bin/bash
# COMO_EXECUTAR_LINUX.sh
# Guia visual rápido de execução

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  🤖 BCI-ON1 - COMO EXECUTAR NO LINUX                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  MÉTODO MAIS FÁCIL - LAUNCHER INTERATIVO                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Execute no terminal:

   cd /home/david/bci-on1
   bash iniciar.sh

Você verá um menu com opções:

   [1] 🌐 Iniciar Interface Web (RECOMENDADO)
   [2] 📊 Ver Status do Sistema
   [3] 📝 Ver Logs e Histórico
   [4] ⚙️  Configurar Credenciais
   [5] 🔄 Reinstalar Sistema
   [0] 🚪 Sair

Escolha [1] e acesse: http://localhost:5000


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  MÉTODO DIRETO - INTERFACE WEB                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Execute no terminal:

   cd /home/david/bci-on1
   bash web/run_web.sh

Depois abra o navegador em: http://localhost:5000


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ATALHOS RÁPIDOS                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Você pode criar um atalho no desktop ou um alias no .bashrc:

   # Adicione no seu ~/.bashrc:
   alias bci='cd /home/david/bci-on1 && bash iniciar.sh'

Depois use apenas: bci


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  O QUE FAZER DEPOIS DE INICIAR                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. Configure as credenciais (Servopa, Todoist, Evolution API)
2. Teste as conexões
3. Execute a automação Dia 8 ou Dia 16
4. Acompanhe o histórico de execuções


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PROBLEMAS COMUNS                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

❌ Erro: "ModuleNotFoundError: No module named 'flask'"
   Solução: Use bash web/run_web.sh (ativa ambiente virtual)

❌ Erro: "Ambiente virtual não encontrado"
   Solução: Execute bash install.sh primeiro

❌ Erro: "Chrome não encontrado"
   Solução: sudo apt install google-chrome-stable


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  DOCUMENTAÇÃO COMPLETA                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   cat GUIA_RAPIDO_LINUX.md
   cat README.md


╔═══════════════════════════════════════════════════════════════╗
║  💡 DICA: Execute agora bash iniciar.sh para começar!       ║
╚═══════════════════════════════════════════════════════════════╝

EOF
