# 🎨 Ícone Personalizado OXCASH

## Sobre o Ícone

O BCI-ON1 agora possui um **ícone personalizado** com a logo do OXCASH (troféu dourado em fundo azul gradiente) para o atalho no Windows.

## Como Funciona

### Durante a Instalação

Quando você executa `install.bat`, o instalador automaticamente:

1. ✅ Instala a biblioteca **Pillow** (para criar imagens)
2. 🎨 Executa `create_icon.py` que gera o arquivo `oxcash_icon.ico`
3. 🔗 Cria um atalho na **área de trabalho** chamado "BCI-ON1 Web"
4. 🖼️ Associa o ícone personalizado ao atalho

### Criação Manual do Ícone

Se você quiser recriar o ícone manualmente:

```bash
# Windows
python create_icon.py
```

Isso criará o arquivo `oxcash_icon.ico` com múltiplas resoluções (16x16 até 256x256).

### Criação Manual do Atalho

Para criar um novo atalho com o ícone:

```bash
# Windows
create_shortcut_with_icon.bat
```

## Detalhes Técnicos

### Arquivo: `oxcash_icon.ico`

- **Formato**: ICO (ícone do Windows)
- **Resoluções**: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256 pixels
- **Design**: 
  - Fundo: Gradiente azul (#1e3a8a → #3b82f6)
  - Troféu: Dourado (#fbbf24) com brilho
  - Estilo: Moderno, minimalista

### Script: `create_icon.py`

Usa a biblioteca **Pillow** para:
- Criar múltiplas resoluções do ícone
- Desenhar o troféu usando formas geométricas
- Aplicar gradiente de fundo
- Adicionar efeitos de brilho
- Salvar no formato `.ico` multi-resolução

### Script: `create_shortcut_with_icon.bat`

Usa **VBScript** para:
- Criar atalho na área de trabalho
- Apontar para `web\run_web.bat`
- Associar o ícone personalizado
- Configurar descrição e diretório de trabalho

## Benefícios

✨ **Visual Profissional**: Ícone personalizado em vez do padrão de engrenagens do Windows

🎯 **Identidade Visual**: Logo OXCASH reconhecível

🚀 **Facilidade**: Um clique para iniciar o sistema

🖥️ **Nativo do Windows**: Integração completa com o sistema operacional

## Compatibilidade

- ✅ Windows 7 ou superior
- ✅ Suporta HiDPI/Retina (múltiplas resoluções)
- ✅ Compatível com temas claro e escuro do Windows

## Troubleshooting

### Ícone não aparece

1. Recarregue o cache de ícones do Windows:
   ```bash
   ie4uinit.exe -show
   ```

2. Ou reinicie o Explorer:
   ```bash
   taskkill /f /im explorer.exe
   start explorer.exe
   ```

### Erro ao criar ícone

Se `create_icon.py` falhar:

1. Instale Pillow manualmente:
   ```bash
   pip install Pillow
   ```

2. Execute novamente:
   ```bash
   python create_icon.py
   ```

### Atalho sem ícone

Se o atalho foi criado mas sem ícone:

1. Execute:
   ```bash
   create_shortcut_with_icon.bat
   ```

2. Isso recriará o atalho com o ícone correto

## Personalização

Para modificar o ícone, edite `create_icon.py` e altere:

- **Cores**: Variáveis `gold`, gradiente RGB
- **Tamanho do troféu**: Variável `trophy_size`
- **Efeitos**: Brilho, sombras, etc.

Depois execute:
```bash
python create_icon.py
```

---

**Desenvolvido para o projeto BCI-ON1 - OXCASH** 🏆
