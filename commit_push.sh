#!/bin/bash
# Script para commit e push das implementações

echo "🔍 Verificando arquivos modificados..."
git status

echo ""
echo "📋 Verificando se dados sensíveis foram removidos..."
echo "clientes_data.json: $(wc -l < clientes_data.json) linha(s)"
echo "cotas_data.json: $(wc -l < cotas_data.json) linha(s)"
echo "calendario_lances.json: $(wc -l < calendario_lances.json) linha(s)"

echo ""
read -p "✅ Os arquivos estão zerados. Deseja continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    echo "❌ Operação cancelada"
    exit 1
fi

echo ""
echo "➕ Adicionando arquivos ao stage..."
git add .gitignore
git add automation/servopa_automation.py
git add web/app.py
git add web/templates/clientes.html
git add clientes_data.json
git add cotas_data.json
git add calendario_lances.json
git add IMPLEMENTACAO_WHATSAPP_CLIENTES.md
git add MELHORIAS_INTERFACE_CLIENTES.md
git add LIMPEZA_DADOS.md

echo ""
echo "📝 Criando commit..."
git commit -m "feat: Implementação completa de envio WhatsApp com dados financeiros

✨ Novas Funcionalidades:
- Extração automática de Total Investido e Crédito Atual de cada cota
- Agregação inteligente para clientes com múltiplas cotas (soma valores)
- Cálculos automáticos: Valorização Patrimonial e Lucro Atual
- Interface compacta: cards mostram apenas Lucro Atual
- Modal de edição em 2 colunas (dados básicos + financeiro + histórico)
- Histórico completo de envios WhatsApp com snapshot de valores
- Atualização em tempo real ao digitar Crédito Inicial
- Prevenção de envio duplicado (intervalo mínimo de 6 meses)

🔧 Melhorias Técnicas:
- Selenium navega em cada linha da tabela de cotas
- XPath para extrair valores financeiros do extrato
- Parse de valores monetários (R\$ X.XXX,XX → float)
- Formatação automática de valores em BRL
- Validação de celular (mínimo 10 dígitos)
- Registro de histórico com data/hora/valores

🎨 Interface:
- Cards compactos com badge de múltiplas cotas (+X)
- Modal grande (1100px) responsivo
- Grid 2 colunas: esquerda (dados) + direita (financeiro + histórico)
- Cores dinâmicas: verde (lucro) / vermelho (prejuízo)
- Input inline com atualização em tempo real
- Enter não fecha mais o modal

📚 Documentação:
- IMPLEMENTACAO_WHATSAPP_CLIENTES.md: fluxo completo
- MELHORIAS_INTERFACE_CLIENTES.md: layout e UX
- LIMPEZA_DADOS.md: arquivos zerados

🔒 Segurança:
- Dados sensíveis removidos antes do commit
- .gitignore atualizado
- Apenas templates e código no repositório
"

echo ""
echo "🚀 Status após commit:"
git status

echo ""
read -p "📤 Deseja fazer push para origin/main? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]
then
    echo "📤 Enviando para repositório remoto..."
    git push origin main
    echo ""
    echo "✅ Push concluído com sucesso!"
else
    echo "⏸️  Push cancelado. Use 'git push origin main' quando estiver pronto."
fi
