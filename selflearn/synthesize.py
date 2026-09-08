# -*- coding: utf-8 -*-
"""Синтез страниц с разметкой: текст, блоки, маски."""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
except Exception:
    FONT = ImageFont.load_default()


def generate_page(width=800, height=600, bg_color=(255, 255, 255), seed=None):
    """Генерация чистой страницы с текстом и разметкой."""
    if seed is not None:
        random.seed(seed)
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Генерируем несколько текстовых блоков
    blocks = []
    y_start = 40
    line_height = 24
    num_blocks = random.randint(2, 5)
    
    for _ in range(num_blocks):
        x0 = random.randint(30, 150)
        y0 = y_start + random.randint(0, 50)
        block_width = random.randint(200, 500)
        num_lines = random.randint(2, 6)
        block_height = num_lines * line_height
        
        # Рисуем прямоугольник блока
        color = (random.randint(220, 255), random.randint(220, 255), random.randint(220, 255))
        draw.rectangle([x0, y0, x0 + block_width, y0 + block_height], fill=color, outline=(100, 100, 100))
        
        # Генерируем псевдо-текст
        text_lines = []
        for i in range(num_lines):
            line_len = random.randint(20, 60)
            line = "".join(random.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(line_len))
            text_lines.append(line)
        
        text = "\n".join(text_lines)
        draw.text((x0 + 5, y0 + 3), text, fill=(0, 0, 0), font=FONT)
        
        blocks.append({
            "id": len(blocks),
            "bbox": [x0, y0, x0 + block_width, y0 + block_height],
            "text": text,
            "type": random.choice(["paragraph", "header", "table", "figure"]),
        })
        
        y_start += block_height + random.randint(10, 30)
    
    return img, blocks


def generate_mask(blocks, width, height, mode="multi"):
    """Генерация маски сегментации по блокам."""
    mask = np.zeros((height, width), dtype=np.uint8)
    draw = ImageDraw.Draw(Image.fromarray(mask))
    
    for i, block in enumerate(blocks):
        x0, y0, x1, y1 = block["bbox"]
        if mode == "binary":
            val = 255
        else:
            val = min(255, (i + 1) * 40)
        draw.rectangle([x0, y0, x1, y1], fill=val)
    
    return mask


def save_sample(out_dir, idx, img, blocks, mask=None):
    """Сохранение образца: изображение, JSON с разметкой, маска."""
    from common import ensure, jdump
    
    out_dir = ensure(out_dir)
    img_path = out_dir / f"{idx:06d}.png"
    meta_path = out_dir / f"{idx:06d}.json"
    
    img.save(img_path)
    jdump({"blocks": blocks, "width": img.width, "height": img.height}, meta_path)
    
    if mask is not None:
        mask_path = out_dir / f"{idx:06d}_mask.png"
        Image.fromarray(mask).save(mask_path)
    
    return str(img_path), str(meta_path), str(mask_path) if mask is not None else None


if __name__ == "__main__":
    # Тест генерации
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "./data/synthetic"
    for i in range(5):
        img, blocks = generate_page(seed=i)
        mask = generate_mask(blocks, img.width, img.height)
        ip, mp, mskp = save_sample(out, i, img, blocks, mask)
        print(f"Saved: {ip}, {mp}, {mskp}")
