# 🔧 INSTALADOR RÁPIDO - OXCASH BCI-ON1
# Execute este comando no PowerShell (como Administrador):
# irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    🚀 INSTALADOR RÁPIDO - OXCASH BCI-ON1" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se está rodando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  ATENÇÃO: Execute como Administrador!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Clique com botão direito no PowerShell e escolha:" -ForegroundColor White
    Write-Host "   'Executar como Administrador'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Depois execute novamente:" -ForegroundColor White
    Write-Host "   irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex" -ForegroundColor Green
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ Executando como Administrador" -ForegroundColor Green
Write-Host ""

# Define diretório de instalação
$installDir = "$env:USERPROFILE\Desktop\bci-on1"

Write-Host "📁 Diretório de instalação: $installDir" -ForegroundColor Cyan
Write-Host ""

# Cria diretório se não existir
if (-not (Test-Path $installDir)) {
    Write-Host "📂 Criando diretório..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# Vai para o diretório
Set-Location $installDir

# Verifica se Git está instalado
Write-Host "🔍 Verificando Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Baixe e instale o Git:" -ForegroundColor Yellow
    Write-Host "   https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Depois execute este instalador novamente." -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host ""

# Clona ou atualiza repositório
if (Test-Path ".git") {
    Write-Host "🔄 Repositório já existe, atualizando..." -ForegroundColor Yellow
    git pull
} else {
    Write-Host "📥 Clonando repositório..." -ForegroundColor Yellow
    git clone https://github.com/dhqdev/bci-on1.git .
}

Write-Host ""
Write-Host "✅ Repositório atualizado!" -ForegroundColor Green
Write-Host ""

# Verifica se Python está instalado
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Baixe e instale o Python 3.11+:" -ForegroundColor Yellow
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE: Marque a opção 'Add Python to PATH' durante instalação!" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host ""

# Executa instalador batch (mais compatível)
Write-Host "🚀 Executando instalador..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path "install.bat") {
    # Permite execução temporariamente
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    
    # Executa install.bat
    cmd /c install.bat
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "    ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 Para iniciar o sistema:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "   1. Procure no Desktop o atalho: 'BCI-ON1 Web'" -ForegroundColor Yellow
        Write-Host "   2. Clique duas vezes para iniciar" -ForegroundColor Yellow
        Write-Host "   3. Acesse: http://localhost:5000" -ForegroundColor Green
        Write-Host ""
        Write-Host "📚 Documentação completa em:" -ForegroundColor Cyan
        Write-Host "   $installDir\README.md" -ForegroundColor White
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Erro durante instalação (código: $exitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔍 Verifique os logs acima para detalhes" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "❌ Arquivo install.bat não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📁 Certifique-se de estar no diretório correto:" -ForegroundColor Yellow
    Write-Host "   $installDir" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
