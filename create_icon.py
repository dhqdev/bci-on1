#!/usr/bin/env python3
"""
Script para criar um ícone personalizado para o BCI-ON1
Gera um arquivo .ico com logo do OXCASH
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_oxcash_icon():
    """Cria ícone com logo OXCASH"""
    
    # Tamanhos de ícone do Windows
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Cria imagem com fundo gradiente azul
        img = Image.new('RGB', (size, size), color='#1e3a8a')
        draw = ImageDraw.Draw(img)
        
        # Gradiente (simplificado)
        for y in range(size):
            progress = y / size
            r = int(30 + (59 - 30) * progress)
            g = int(58 + (130 - 58) * progress)
            b = int(138 + (246 - 138) * progress)
            draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))
        
        # Desenha troféu (emoji-style)
        # Tamanho do troféu proporcional ao ícone
        trophy_size = int(size * 0.6)
        trophy_x = (size - trophy_size) // 2
        trophy_y = int(size * 0.2)
        
        # Copa do troféu (amarelo dourado)
        gold = '#fbbf24'
        
        # Copa superior
        cup_top = int(trophy_size * 0.3)
        cup_height = int(trophy_size * 0.5)
        cup_width = int(trophy_size * 0.8)
        
        # Desenha a copa
        draw.ellipse(
            [trophy_x + (trophy_size - cup_width) // 2, trophy_y,
             trophy_x + (trophy_size + cup_width) // 2, trophy_y + cup_top],
            fill=gold
        )
        
        # Corpo da copa
        draw.rectangle(
            [trophy_x + (trophy_size - cup_width) // 2, trophy_y + cup_top // 2,
             trophy_x + (trophy_size + cup_width) // 2, trophy_y + cup_height],
            fill=gold
        )
        
        # Base do troféu
        base_height = int(trophy_size * 0.15)
        base_width = cup_width
        draw.rectangle(
            [trophy_x + (trophy_size - base_width) // 2, trophy_y + cup_height,
             trophy_x + (trophy_size + base_width) // 2, trophy_y + cup_height + base_height],
            fill=gold
        )
        
        # Pedestal
        pedestal_width = int(base_width * 1.2)
        pedestal_height = int(trophy_size * 0.1)
        draw.rectangle(
            [trophy_x + (trophy_size - pedestal_width) // 2, trophy_y + cup_height + base_height,
             trophy_x + (trophy_size + pedestal_width) // 2, trophy_y + cup_height + base_height + pedestal_height],
            fill='#d97706'
        )
        
        # Adiciona brilho
        if size >= 48:
            shine_size = int(cup_width * 0.3)
            draw.ellipse(
                [trophy_x + int(trophy_size * 0.25), trophy_y + int(cup_top * 0.5),
                 trophy_x + int(trophy_size * 0.25) + shine_size, trophy_y + int(cup_top * 0.5) + shine_size],
                fill='#fef3c7'
            )
        
        images.append(img)
    
    # Salva como .ico multi-resolução
    icon_path = os.path.join(os.path.dirname(__file__), 'oxcash_icon.ico')
    images[0].save(icon_path, format='ICO', sizes=[(img.size[0], img.size[1]) for img in images])
    
    print(f"✅ Ícone criado: {icon_path}")
    return icon_path

if __name__ == '__main__':
    try:
        print("🎨 Criando ícone personalizado OXCASH...")
        icon_path = create_oxcash_icon()
        print(f"✨ Ícone salvo em: {icon_path}")
    except ImportError:
        print("⚠️  Pillow não instalado. Instalando...")
        import subprocess
        subprocess.run(['pip', 'install', 'Pillow'], check=True)
        print("✅ Pillow instalado! Execute o script novamente.")
    except Exception as e:
        print(f"❌ Erro ao criar ícone: {e}")
