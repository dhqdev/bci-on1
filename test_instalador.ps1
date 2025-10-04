# 🧪 TESTE DO INSTALADOR AUTOMÁTICO
# Execute este script para testar se tudo está funcionando

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    🧪 TESTE DO INSTALADOR AUTOMÁTICO" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Teste 1: Verifica se install-rapido.ps1 existe
Write-Host "📝 Teste 1: Verificando install-rapido.ps1..." -ForegroundColor Cyan
if (Test-Path "install-rapido.ps1") {
    Write-Host "✅ PASSOU - install-rapido.ps1 existe" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "❌ FALHOU - install-rapido.ps1 não encontrado" -ForegroundColor Red
    $testsFailed++
}

# Teste 2: Verifica se INICIAR_BCI.bat existe
Write-Host "📝 Teste 2: Verificando INICIAR_BCI.bat..." -ForegroundColor Cyan
if (Test-Path "INICIAR_BCI.bat") {
    Write-Host "✅ PASSOU - INICIAR_BCI.bat existe" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "❌ FALHOU - INICIAR_BCI.bat não encontrado" -ForegroundColor Red
    $testsFailed++
}

# Teste 3: Verifica se INICIAR_WEB.bat existe
Write-Host "📝 Teste 3: Verificando INICIAR_WEB.bat..." -ForegroundColor Cyan
if (Test-Path "INICIAR_WEB.bat") {
    Write-Host "✅ PASSOU - INICIAR_WEB.bat existe" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "❌ FALHOU - INICIAR_WEB.bat não encontrado" -ForegroundColor Red
    $testsFailed++
}

# Teste 4: Verifica conteúdo do install-rapido.ps1
Write-Host "📝 Teste 4: Verificando melhorias no install-rapido.ps1..." -ForegroundColor Cyan
$content = Get-Content "install-rapido.ps1" -Raw

$checks = @{
    "Instalação automática de Git" = $content -match "InstallAllUsers"
    "Configuração de PATH" = $content -match "SetEnvironmentVariable"
    "Instalação automática de Python" = $content -match "PrependPath=1"
    "Criação de atalho" = $content -match "create_shortcut"
    "Elevação de privilégios" = $content -match "RunAs"
}

$allPassed = $true
foreach ($check in $checks.GetEnumerator()) {
    if ($check.Value) {
        Write-Host "  ✅ $($check.Key)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($check.Key)" -ForegroundColor Red
        $allPassed = $false
    }
}

if ($allPassed) {
    Write-Host "✅ PASSOU - Todas as melhorias implementadas" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "❌ FALHOU - Algumas melhorias faltando" -ForegroundColor Red
    $testsFailed++
}

# Teste 5: Verifica conteúdo do INICIAR_BCI.bat
Write-Host "📝 Teste 5: Verificando INICIAR_BCI.bat..." -ForegroundColor Cyan
$batContent = Get-Content "INICIAR_BCI.bat" -Raw

if ($batContent -match "web\\app.py" -and $batContent -match "venv\\Scripts\\activate") {
    Write-Host "✅ PASSOU - INICIAR_BCI.bat configurado corretamente" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "❌ FALHOU - INICIAR_BCI.bat com problemas" -ForegroundColor Red
    $testsFailed++
}

# Teste 6: Verifica documentação
Write-Host "📝 Teste 6: Verificando documentação..." -ForegroundColor Cyan
$docs = @(
    "MELHORIAS_INSTALADOR_AUTOMATICO.md",
    "INSTALACAO_RAPIDA.md",
    "RESUMO_CORRECOES_INSTALADOR.md"
)

$docsPassed = $true
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "  ✅ $doc" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $doc não encontrado" -ForegroundColor Red
        $docsPassed = $false
    }
}

if ($docsPassed) {
    Write-Host "✅ PASSOU - Toda documentação criada" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "❌ FALHOU - Documentação incompleta" -ForegroundColor Red
    $testsFailed++
}

# Resultado final
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    📊 RESULTADO DOS TESTES" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Testes Passados: $testsPassed" -ForegroundColor Green

if ($testsFailed -eq 0) {
    Write-Host "❌ Testes Falhados: $testsFailed" -ForegroundColor Green
} else {
    Write-Host "❌ Testes Falhados: $testsFailed" -ForegroundColor Red
}

Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "🎉 TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ O instalador está pronto para uso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Próximos passos:" -ForegroundColor Cyan
    Write-Host "   1. Commit das mudanças:" -ForegroundColor White
    Write-Host "      git add ." -ForegroundColor Gray
    Write-Host "      git commit -m 'feat: Instalacao 100% automatica'" -ForegroundColor Gray
    Write-Host "      git push origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. Testar em um PC limpo:" -ForegroundColor White
    Write-Host "      irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "⚠️  ALGUNS TESTES FALHARAM" -ForegroundColor Yellow
    Write-Host "Revise os erros acima antes de continuar." -ForegroundColor Yellow
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

