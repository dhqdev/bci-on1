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
    Write-Host "⚠️  Este script precisa de privilégios de Administrador..." -ForegroundColor Yellow
    Write-Host "🔄 Solicitando permissão de Administrador..." -ForegroundColor Cyan
    
    # Tenta reexecutar como Admin automaticamente
    try {
        $scriptContent = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1" -UseBasicParsing
        $tempScript = "$env:TEMP\bci-install-temp.ps1"
        $scriptContent.Content | Out-File -FilePath $tempScript -Encoding UTF8
        
        Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$tempScript`"" -Verb RunAs
        exit
    }
    catch {
        Write-Host ""
        Write-Host "❌ Não foi possível elevar permissões automaticamente" -ForegroundColor Red
        Write-Host ""
        Write-Host "📝 Por favor, execute manualmente como Administrador:" -ForegroundColor White
        Write-Host "   1. Clique com botão direito no PowerShell" -ForegroundColor Cyan
        Write-Host "   2. Escolha 'Executar como Administrador'" -ForegroundColor Cyan
        Write-Host "   3. Execute: irm https://raw.githubusercontent.com/dhqdev/bci-on1/main/install-rapido.ps1 | iex" -ForegroundColor Green
        Write-Host ""
        pause
        exit 1
    }
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
    Write-Host "❌ Git não encontrado - instalando automaticamente..." -ForegroundColor Yellow
    
    # Detecta arquitetura
    $arch = if ([Environment]::Is64BitOperatingSystem) { "64" } else { "32" }
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-$arch-bit.exe"
    
    Write-Host "📥 Baixando Git..." -ForegroundColor Yellow
    $installer = "$env:TEMP\git-installer.exe"
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $gitUrl -OutFile $installer -UseBasicParsing
        
        Write-Host "🔧 Instalando Git (isso pode levar alguns minutos)..." -ForegroundColor Yellow
        
        # Instala Git com PATH automático e componentes essenciais
        $gitArgs = @(
            "/VERYSILENT",
            "/NORESTART", 
            "/NOCANCEL",
            "/SP-",
            "/CLOSEAPPLICATIONS",
            "/RESTARTAPPLICATIONS",
            "/COMPONENTS=icons,ext\reg\shellhere,assoc,assoc_sh",
            "/DIR=C:\Program Files\Git",
            "/ALLUSERS"
        )
        
        $process = Start-Process -FilePath $installer -ArgumentList $gitArgs -Wait -PassThru -NoNewWindow
        Remove-Item $installer -Force
        
        if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 3010) {
            Write-Host "✅ Git instalado com sucesso!" -ForegroundColor Green
            
            # Adiciona Git ao PATH da sessão atual E permanentemente
            $gitPath = "C:\Program Files\Git\cmd"
            
            # PATH da sessão atual
            $env:Path += ";$gitPath"
            
            # PATH permanente (System)
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            if ($currentPath -notlike "*$gitPath*") {
                [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gitPath", "Machine")
                Write-Host "✅ Git adicionado ao PATH do sistema" -ForegroundColor Green
            }
            
            # Recarrega o PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            # Aguarda e testa
            Start-Sleep -Seconds 3
            
            try {
                $testGit = & git --version 2>&1
                Write-Host "✅ Git verificado: $testGit" -ForegroundColor Green
                $gitFound = $true
            }
            catch {
                Write-Host "⚠️  Git instalado mas precisa reiniciar o PowerShell" -ForegroundColor Yellow
                $gitFound = $true
            }
        } else {
            throw "Instalação retornou código: $($process.ExitCode)"
        }
    }
    catch {
        Write-Host "❌ Erro ao instalar Git: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 INSTALAÇÃO MANUAL:" -ForegroundColor Yellow
        Write-Host "   1. Baixe: https://git-scm.com/download/win" -ForegroundColor Cyan
        Write-Host "   2. Execute o instalador" -ForegroundColor White
        Write-Host "   3. Use as opções padrão (importante: marque 'Add to PATH')" -ForegroundColor White
        Write-Host "   4. Execute este instalador novamente" -ForegroundColor White
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
    Write-Host "❌ Python não encontrado - instalando automaticamente..." -ForegroundColor Yellow
    
    # Python 3.11.6 (versão estável e compatível)
    $pythonUrl = "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe"
    
    Write-Host "📥 Baixando Python 3.11.6..." -ForegroundColor Yellow
    $installer = "$env:TEMP\python-installer.exe"
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installer -UseBasicParsing
        
        Write-Host "🔧 Instalando Python (isso pode levar alguns minutos)..." -ForegroundColor Yellow
        
        # Instala Python com PATH automático para TODOS os usuários
        $pythonArgs = @(
            "/quiet",
            "InstallAllUsers=1",
            "PrependPath=1",
            "Include_test=0",
            "Include_pip=1",
            "Include_doc=0",
            "TargetDir=C:\Program Files\Python311"
        )
        
        $process = Start-Process -FilePath $installer -ArgumentList $pythonArgs -Wait -PassThru -NoNewWindow
        Remove-Item $installer -Force
        
        if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 3010) {
            Write-Host "✅ Python instalado com sucesso!" -ForegroundColor Green
            
            # Adiciona Python ao PATH da sessão atual E permanentemente
            $pythonPath = "C:\Program Files\Python311"
            $pythonScripts = "C:\Program Files\Python311\Scripts"
            
            # PATH da sessão atual
            $env:Path += ";$pythonPath;$pythonScripts"
            
            # PATH permanente (System)
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            if ($currentPath -notlike "*$pythonPath*") {
                [Environment]::SetEnvironmentVariable("Path", "$currentPath;$pythonPath;$pythonScripts", "Machine")
                Write-Host "✅ Python adicionado ao PATH do sistema" -ForegroundColor Green
            }
            
            # Recarrega o PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            # Aguarda instalação finalizar completamente
            Write-Host "⏳ Finalizando configuração do Python..." -ForegroundColor Yellow
            Start-Sleep -Seconds 8
            
            # Testa Python
            try {
                $testPython = & python --version 2>&1
                Write-Host "✅ Python verificado: $testPython" -ForegroundColor Green
                $pythonCmd = "python"
                $pythonFound = $true
            }
            catch {
                # Tenta com py launcher
                try {
                    $testPy = & py --version 2>&1
                    Write-Host "✅ Python verificado via py launcher: $testPy" -ForegroundColor Green
                    $pythonCmd = "py"
                    $pythonFound = $true
                }
                catch {
                    Write-Host "⚠️  Python instalado mas precisa reiniciar o PowerShell" -ForegroundColor Yellow
                    $pythonFound = $true
                }
            }
        } else {
            throw "Instalação retornou código: $($process.ExitCode)"
        }
    }
    catch {
        Write-Host "❌ Erro ao instalar Python: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "🔧 INSTALAÇÃO MANUAL:" -ForegroundColor Yellow
        Write-Host "   1. Baixe: https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host "   2. Execute o instalador" -ForegroundColor White
        Write-Host "   3. ⚠️  IMPORTANTE: Marque 'Add Python to PATH'" -ForegroundColor Red
        Write-Host "   4. Reinicie o computador" -ForegroundColor White
        Write-Host "   5. Execute este instalador novamente" -ForegroundColor White
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
        
        # Cria atalho executável na área de trabalho
        Write-Host "🔗 Criando atalho na área de trabalho..." -ForegroundColor Cyan
        
        $desktopPath = [Environment]::GetFolderPath("Desktop")
        $shortcutPath = "$desktopPath\BCI-ON1 Web.lnk"
        $targetPath = "$installDir\INICIAR_BCI.bat"
        $iconPath = "$installDir\oxcash_icon.ico"
        
        # Cria ícone se não existir
        if (-not (Test-Path $iconPath)) {
            Write-Host "🎨 Criando ícone..." -ForegroundColor Yellow
            
            # Verifica se Pillow está instalado
            try {
                & "$installDir\venv\Scripts\python.exe" -c "import PIL" 2>&1 | Out-Null
            }
            catch {
                Write-Host "📦 Instalando Pillow..." -ForegroundColor Yellow
                & "$installDir\venv\Scripts\pip.exe" install Pillow | Out-Null
            }
            
            # Cria o ícone
            if (Test-Path "$installDir\create_icon.py") {
                & "$installDir\venv\Scripts\python.exe" "$installDir\create_icon.py" 2>&1 | Out-Null
            }
        }
        
        # Cria o atalho usando VBScript
        $vbsScript = @"
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "$shortcutPath"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "$targetPath"
oLink.WorkingDirectory = "$installDir"
oLink.Description = "Iniciar BCI-ON1 Interface Web"
oLink.WindowStyle = 1
"@
        
        if (Test-Path $iconPath) {
            $vbsScript += "`noLink.IconLocation = `"$iconPath`""
        }
        
        $vbsScript += "`noLink.Save"
        
        $vbsFile = "$env:TEMP\create_shortcut.vbs"
        $vbsScript | Out-File -FilePath $vbsFile -Encoding ASCII
        
        Start-Process "wscript.exe" -ArgumentList "`"$vbsFile`"" -Wait -NoNewWindow
        Remove-Item $vbsFile -Force
        
        if (Test-Path $shortcutPath) {
            Write-Host "✅ Atalho criado na área de trabalho!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Não foi possível criar atalho automaticamente" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "🎯 Como iniciar o sistema:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "   📌 OPÇÃO 1 (RECOMENDADO): Clique duas vezes no atalho" -ForegroundColor Yellow
        Write-Host "      'BCI-ON1 Web' na sua área de trabalho" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   📌 OPÇÃO 2: Clique duas vezes em:" -ForegroundColor Yellow
        Write-Host "      $installDir\INICIAR_BCI.bat" -ForegroundColor White
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
        if ($resposta -eq "S" -or $resposta -eq "s" -or $resposta -eq "") {
            Write-Host ""
            Write-Host "🚀 Iniciando servidor..." -ForegroundColor Cyan
            Write-Host "⏳ Aguarde alguns segundos..." -ForegroundColor Yellow
            Write-Host ""
            
            # Inicia usando o novo script
            Start-Process -FilePath "$installDir\INICIAR_BCI.bat"
            Start-Sleep -Seconds 5
            
            # Abre o navegador
            Start-Process "http://localhost:5000"
            
            Write-Host "✅ Sistema iniciado!" -ForegroundColor Green
            Write-Host "📱 O navegador deve abrir automaticamente" -ForegroundColor Cyan
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
