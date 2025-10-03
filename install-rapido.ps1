# 🔧 INSTALADOR COMPLETO - OXCASH BCI-ON1
# Instala TUDO: Git, Python, Chrome, Dependências
# Execute este comando no PowerShell (como Administrador):
# irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    🚀 INSTALADOR COMPLETO - OXCASH BCI-ON1" -ForegroundColor Yellow
Write-Host "    Instala TUDO automaticamente!" -ForegroundColor Yellow
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

# Função para baixar e instalar programas
function Install-Program {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Args = "/S"
    )
    
    Write-Host "📥 Baixando $Name..." -ForegroundColor Yellow
    $installer = "$env:TEMP\$Name-installer.exe"
    
    try {
        # Usa TLS 1.2 para downloads
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $installer -UseBasicParsing
        
        Write-Host "🔧 Instalando $Name..." -ForegroundColor Yellow
        Start-Process -FilePath $installer -ArgumentList $Args -Wait -NoNewWindow
        
        Remove-Item $installer -Force
        Write-Host "✅ $Name instalado com sucesso!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Erro ao instalar $Name : $_" -ForegroundColor Red
        return $false
    }
}

# Função para verificar se programa está instalado
function Test-ProgramInstalled {
    param([string]$Command)
    
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Verifica Git
Write-Host "🔍 Verificando Git..." -ForegroundColor Cyan
$gitFound = $false

# Verifica se Git está no PATH
if (Test-ProgramInstalled "git") {
    $gitVersion = git --version
    Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
    $gitFound = $true
} 
# Verifica se Git está instalado mas não está no PATH
elseif (Test-Path "C:\Program Files\Git\cmd\git.exe") {
    $env:Path += ";C:\Program Files\Git\cmd"
    $gitVersion = git --version
    Write-Host "✅ Git encontrado (adicionado ao PATH): $gitVersion" -ForegroundColor Green
    $gitFound = $true
}
elseif (Test-Path "${env:ProgramFiles(x86)}\Git\cmd\git.exe") {
    $env:Path += ";${env:ProgramFiles(x86)}\Git\cmd"
    $gitVersion = git --version
    Write-Host "✅ Git encontrado (adicionado ao PATH): $gitVersion" -ForegroundColor Green
    $gitFound = $true
}

if (-not $gitFound) {
    Write-Host "❌ Git não encontrado - tentando instalar..." -ForegroundColor Yellow
    
    # Detecta arquitetura
    $arch = if ([Environment]::Is64BitOperatingSystem) { "64" } else { "32" }
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-$arch-bit.exe"
    
    if (Install-Program "Git" $gitUrl "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS=`"icons,ext\reg\shellhere,assoc,assoc_sh`"") {
        # Adiciona Git ao PATH da sessão atual
        $env:Path += ";C:\Program Files\Git\cmd"
        Write-Host "✅ Git instalado e configurado!" -ForegroundColor Green
        $gitFound = $true
    } else {
        Write-Host "❌ FALHA ao instalar Git automaticamente!" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 SOLUÇÃO MANUAL:" -ForegroundColor Yellow
        Write-Host "   1. Baixe Git: https://git-scm.com/download/win" -ForegroundColor White
        Write-Host "   2. Instale normalmente" -ForegroundColor White
        Write-Host "   3. Execute este instalador novamente" -ForegroundColor White
        Write-Host ""
        pause
        exit 1
    }
}

Write-Host ""

# Verifica Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Cyan
$pythonFound = $false
$pythonCmd = ""

# Tenta diferentes comandos Python
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python (\d+\.\d+\.\d+)") {
            Write-Host "✅ Python encontrado: $version" -ForegroundColor Green
            $pythonCmd = $cmd
            $pythonFound = $true
            break
        }
    }
    catch {
        # Comando não existe, continua tentando
    }
}

# Verifica se Python está instalado mas não no PATH
if (-not $pythonFound) {
    $pythonPaths = @(
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python310\python.exe",
        "${env:LOCALAPPDATA}\Programs\Python\Python311\python.exe",
        "${env:LOCALAPPDATA}\Programs\Python\Python312\python.exe"
    )
    
    foreach ($path in $pythonPaths) {
        if (Test-Path $path) {
            $dir = Split-Path $path
            $env:Path += ";$dir;$dir\Scripts"
            $version = & python --version 2>&1
            Write-Host "✅ Python encontrado (adicionado ao PATH): $version" -ForegroundColor Green
            $pythonCmd = "python"
            $pythonFound = $true
            break
        }
    }
}

if (-not $pythonFound) {
    Write-Host "❌ Python não encontrado - tentando instalar..." -ForegroundColor Yellow
    
    # Python 3.11.6 (versão estável e compatível)
    $pythonUrl = "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe"
    
    if (Install-Program "Python" $pythonUrl "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0") {
        # Adiciona Python ao PATH da sessão atual
        $env:Path += ";C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
        
        # Aguarda 5 segundos para instalação finalizar
        Write-Host "⏳ Aguardando instalação finalizar..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        # Tenta novamente
        try {
            $version = python --version 2>&1
            Write-Host "✅ Python instalado: $version" -ForegroundColor Green
            $pythonFound = $true
        }
        catch {
            Write-Host "❌ FALHA ao instalar Python automaticamente!" -ForegroundColor Red
            Write-Host ""
            Write-Host "🔧 SOLUÇÃO MANUAL:" -ForegroundColor Yellow
            Write-Host "   1. Baixe Python: https://www.python.org/downloads/" -ForegroundColor White
            Write-Host "   2. Durante instalação, MARQUE: 'Add Python to PATH'" -ForegroundColor White
            Write-Host "   3. Reinicie o computador" -ForegroundColor White
            Write-Host "   4. Execute este instalador novamente" -ForegroundColor White
            Write-Host ""
            pause
            exit 1
        }
    } else {
        Write-Host "❌ FALHA ao instalar Python automaticamente!" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 SOLUÇÃO MANUAL:" -ForegroundColor Yellow
        Write-Host "   1. Baixe Python: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "   2. Durante instalação, MARQUE: 'Add Python to PATH'" -ForegroundColor White
        Write-Host "   3. Reinicie o computador" -ForegroundColor White
        Write-Host "   4. Execute este instalador novamente" -ForegroundColor White
        Write-Host ""
        pause
        exit 1
    }
}

Write-Host ""

# Verifica Chrome
Write-Host "🔍 Verificando Google Chrome..." -ForegroundColor Cyan
$chromeInstalled = $false

# Verifica múltiplos locais do Chrome
$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        $chromeInstalled = $true
        Write-Host "✅ Chrome encontrado: $path" -ForegroundColor Green
        break
    }
}

if (-not $chromeInstalled) {
    Write-Host "❌ Chrome não encontrado - instalando automaticamente..." -ForegroundColor Yellow
    
    $chromeUrl = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    
    if (Install-Program "Chrome" $chromeUrl "/silent /install") {
        Write-Host "✅ Chrome instalado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Instalação manual necessária: https://www.google.com/chrome/" -ForegroundColor Yellow
    }
}

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

# Clona ou atualiza repositório
Write-Host "📥 Baixando código do GitHub..." -ForegroundColor Cyan

# Verifica se Git está disponível
try {
    $null = git --version 2>&1
} catch {
    Write-Host "❌ Git não está disponível no PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 SOLUÇÃO:" -ForegroundColor Yellow
    Write-Host "   1. Baixe o projeto manualmente: https://github.com/dhqdev/bci-on1/archive/refs/heads/main.zip" -ForegroundColor White
    Write-Host "   2. Extraia para: $installDir" -ForegroundColor White
    Write-Host "   3. Execute: $installDir\install.bat" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

if (Test-Path ".git") {
    Write-Host "🔄 Repositório já existe, atualizando..." -ForegroundColor Yellow
    try {
        git pull origin main 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Código atualizado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Erro ao atualizar, continuando com versão local..." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Erro ao atualizar, continuando com versão local..." -ForegroundColor Yellow
    }
} else {
    Write-Host "📥 Clonando repositório..." -ForegroundColor Yellow
    try {
        git clone https://github.com/dhqdev/bci-on1.git . 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Código baixado com sucesso!" -ForegroundColor Green
        } else {
            throw "Git clone falhou"
        }
    } catch {
        Write-Host "❌ Erro ao baixar código do GitHub!" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 DOWNLOAD MANUAL:" -ForegroundColor Yellow
        Write-Host "   1. Acesse: https://github.com/dhqdev/bci-on1/archive/refs/heads/main.zip" -ForegroundColor Cyan
        Write-Host "   2. Baixe o arquivo ZIP" -ForegroundColor White
        Write-Host "   3. Extraia para: $installDir" -ForegroundColor White
        Write-Host "   4. Abra PowerShell como Admin em $installDir" -ForegroundColor White
        Write-Host "   5. Execute: .\install.bat" -ForegroundColor Green
        Write-Host ""
        Write-Host "OU tente novamente com melhor conexão de internet" -ForegroundColor Yellow
        Write-Host ""
        pause
        exit 1
    }
}

# Executa instalador batch (instala dependências Python, cria venv, etc)
Write-Host "🚀 Instalando dependências Python..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "install.bat") {
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
        Write-Host "   OPÇÃO 1: Clique no atalho do Desktop" -ForegroundColor Yellow
        Write-Host "   📌 'BCI-ON1 Web' (ícone OXCASH)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   OPÇÃO 2: Execute manualmente" -ForegroundColor Yellow
        Write-Host "   cd $installDir" -ForegroundColor White
        Write-Host "   .\run.bat" -ForegroundColor White
        Write-Host ""
        Write-Host "Depois acesse no navegador:" -ForegroundColor Cyan
        Write-Host "   http://localhost:5000" -ForegroundColor Green
        Write-Host ""
        Write-Host "📚 Documentação completa:" -ForegroundColor Cyan
        Write-Host "   $installDir\README.md" -ForegroundColor White
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        
        # Pergunta se quer iniciar agora
        $resposta = Read-Host "Deseja iniciar o sistema agora? (S/N)"
        if ($resposta -eq "S" -or $resposta -eq "s") {
            Write-Host ""
            Write-Host "🚀 Iniciando servidor..." -ForegroundColor Cyan
            Write-Host "Aguarde alguns segundos..." -ForegroundColor Yellow
            Write-Host ""
            Start-Process -FilePath "$installDir\run.bat"
            Start-Sleep -Seconds 3
            Start-Process "http://localhost:5000"
        }
    } else {
        Write-Host ""
        Write-Host "❌ Erro durante instalação (código: $exitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔍 Possíveis causas:" -ForegroundColor Yellow
        Write-Host "   - Python não está no PATH" -ForegroundColor White
        Write-Host "   - Sem permissão para criar arquivos" -ForegroundColor White
        Write-Host "   - Sem conexão com a internet" -ForegroundColor White
        Write-Host ""
        Write-Host "📝 Tente:" -ForegroundColor Yellow
        Write-Host "   1. Reiniciar o computador" -ForegroundColor White
        Write-Host "   2. Executar novamente como Administrador" -ForegroundColor White
        Write-Host "   3. Verificar se Python está instalado: python --version" -ForegroundColor White
        Write-Host ""
    }
} else {
    Write-Host "❌ Arquivo install.bat não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📁 Verifique se o código foi baixado corretamente em:" -ForegroundColor Yellow
    Write-Host "   $installDir" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 SOLUÇÃO ALTERNATIVA:" -ForegroundColor Yellow
    Write-Host "   1. Baixe manualmente: https://github.com/dhqdev/bci-on1/archive/refs/heads/main.zip" -ForegroundColor Cyan
    Write-Host "   2. Extraia para o Desktop" -ForegroundColor White
    Write-Host "   3. Entre na pasta extraída" -ForegroundColor White
    Write-Host "   4. Clique duas vezes em install.bat" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📚 PRECISA DE AJUDA?" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se algo deu errado, você tem 3 opções:" -ForegroundColor White
Write-Host ""
Write-Host "1️⃣  DOWNLOAD MANUAL (Mais Fácil):" -ForegroundColor Green
Write-Host "   - Baixe: https://github.com/dhqdev/bci-on1/archive/refs/heads/main.zip" -ForegroundColor Cyan
Write-Host "   - Extraia para Desktop\bci-on1" -ForegroundColor White
Write-Host "   - Execute install.bat" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  INSTALAR PRÉ-REQUISITOS MANUALMENTE:" -ForegroundColor Green
Write-Host "   - Git: https://git-scm.com/download/win" -ForegroundColor Cyan
Write-Host "   - Python: https://www.python.org/downloads/ (MARQUE 'Add to PATH')" -ForegroundColor Cyan
Write-Host "   - Depois execute este script novamente" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  COMANDOS MANUAIS (Avançado):" -ForegroundColor Green
Write-Host "   cd Desktop" -ForegroundColor White
Write-Host "   git clone https://github.com/dhqdev/bci-on1.git" -ForegroundColor White
Write-Host "   cd bci-on1" -ForegroundColor White
Write-Host "   install.bat" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
