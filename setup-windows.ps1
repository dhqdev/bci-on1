# setup-windows.ps1 - Instalador BCI-ON1 em PowerShell
# Mais confiável que .bat para operações de arquivo

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BCI-ON1 - Instalador Automatico (PowerShell)" -ForegroundColor Cyan
Write-Host "  Sistema de Automacao Servopa + Todoist" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$INSTALL_DIR = "$env:USERPROFILE\bci-on1"

# Verifica se já existe
if (Test-Path $INSTALL_DIR) {
    Write-Host "[!] Instalacao existente encontrada em:" -ForegroundColor Yellow
    Write-Host "    $INSTALL_DIR" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opcoes:" -ForegroundColor White
    Write-Host "  [1] Atualizar projeto existente (git pull)" -ForegroundColor Green
    Write-Host "  [2] Remover e reinstalar do zero" -ForegroundColor Red
    Write-Host "  [3] Cancelar" -ForegroundColor Gray
    Write-Host ""
    
    $opcao = Read-Host "Escolha uma opcao [1/2/3]"
    
    switch ($opcao) {
        "1" {
            Write-Host "[*] Atualizando projeto existente..." -ForegroundColor Cyan
            Push-Location $INSTALL_DIR
            git pull origin main
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Projeto atualizado!" -ForegroundColor Green
            } else {
                Write-Host "[!] Erro ao atualizar. Continuando..." -ForegroundColor Yellow
            }
            Pop-Location
            $skipClone = $true
        }
        "2" {
            Write-Host "[*] Removendo diretorio antigo..." -ForegroundColor Cyan
            try {
                Remove-Item -Path $INSTALL_DIR -Recurse -Force -ErrorAction Stop
                Write-Host "[OK] Diretorio removido" -ForegroundColor Green
                $skipClone = $false
            }
            catch {
                Write-Host "[X] ERRO: Nao foi possivel remover o diretorio." -ForegroundColor Red
                Write-Host "    Feche todos os programas que possam estar usando:" -ForegroundColor Red
                Write-Host "    - Navegador, VS Code, Terminal, etc." -ForegroundColor Red
                Write-Host ""
                Write-Host "Erro: $_" -ForegroundColor Red
                pause
                exit 1
            }
        }
        "3" {
            Write-Host "[!] Instalacao cancelada." -ForegroundColor Yellow
            pause
            exit 0
        }
        default {
            Write-Host "[X] Opcao invalida!" -ForegroundColor Red
            pause
            exit 1
        }
    }
}

# Verifica Git
Write-Host "[*] Verificando Git..." -ForegroundColor Cyan
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Git instalado" -ForegroundColor Green
} else {
    Write-Host "[X] Git nao encontrado!" -ForegroundColor Red
    Write-Host "    Baixe em: https://git-scm.com/download/win" -ForegroundColor Yellow
    pause
    exit 1
}

# Verifica Python
Write-Host "[*] Verificando Python..." -ForegroundColor Cyan
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Python instalado" -ForegroundColor Green
} else {
    Write-Host "[X] Python nao encontrado!" -ForegroundColor Red
    Write-Host "    Baixe em: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "    IMPORTANTE: Marque 'Add Python to PATH'" -ForegroundColor Yellow
    pause
    exit 1
}

# Verifica Chrome
Write-Host "[*] Verificando Chrome..." -ForegroundColor Cyan
if (Test-Path "HKLM:\SOFTWARE\Google\Chrome\BLBeacon") {
    Write-Host "[OK] Chrome instalado" -ForegroundColor Green
} else {
    Write-Host "[!] Chrome nao encontrado" -ForegroundColor Yellow
    Write-Host "    Baixe em: https://www.google.com/chrome/" -ForegroundColor Yellow
}

Write-Host ""

# Clone repo (se necessário)
if (-not $skipClone) {
    Write-Host "[*] Clonando repositorio do GitHub..." -ForegroundColor Cyan
    git clone https://github.com/dhqdev/bci-on1.git $INSTALL_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[X] ERRO: Falha ao clonar repositorio" -ForegroundColor Red
        Write-Host "    Verifique sua conexao com a internet" -ForegroundColor Yellow
        pause
        exit 1
    }
    Write-Host "[OK] Repositorio clonado" -ForegroundColor Green
}

# Vai para o diretório
Set-Location $INSTALL_DIR

# Run installer
Write-Host ""
Write-Host "[*] Executando instalador de dependencias..." -ForegroundColor Cyan
Write-Host ""
& ".\install.bat"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] ERRO na instalacao de dependencias" -ForegroundColor Red
    pause
    exit 1
}

# Criar atalho na área de trabalho
Write-Host ""
Write-Host "[*] Criando atalho na area de trabalho..." -ForegroundColor Cyan

$DESKTOP = "$env:USERPROFILE\Desktop"
$SHORTCUT_FILE = "$DESKTOP\BCI-ON1-Web.bat"

$shortcutContent = @"
@echo off
title BCI-ON1 - Interface Web
color 0B

echo ==========================================
echo   BCI-ON1 - Sistema de Automacao
echo ==========================================
echo.

cd /d "$INSTALL_DIR"

if exist "venv\Scripts\activate.bat" (
    echo [+] Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else (
    echo [!] ERRO: Ambiente virtual nao encontrado!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Iniciando servidor web...
echo ==========================================
echo.
echo Apos iniciar, abra seu navegador em:
echo    http://localhost:5000
echo.
echo Pressione CTRL+C para parar o servidor.
echo ==========================================
echo.

cd web
python app.py

pause
"@

Set-Content -Path $SHORTCUT_FILE -Value $shortcutContent -Encoding ASCII
Write-Host "[OK] Atalho criado: $SHORTCUT_FILE" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  INSTALACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Projeto instalado em: $INSTALL_DIR" -ForegroundColor White
Write-Host ""
Write-Host "[OK] Atalho criado na area de trabalho: BCI-ON1-Web.bat" -ForegroundColor Green
Write-Host ""
Write-Host "Como executar:" -ForegroundColor White
Write-Host "  1. Clique no atalho 'BCI-ON1-Web.bat' na area de trabalho" -ForegroundColor Cyan
Write-Host "  2. Ou execute: cd $INSTALL_DIR\web && .\run_web.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "Apos iniciar, abra: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
pause
