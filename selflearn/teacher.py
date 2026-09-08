# -*- coding: utf-8 -*-
"""Модуль Учитель: генерация данных с учетом слабых мест Ученика."""
import os
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from common import load_yaml, ensure, jdump, jload, get_logger
from synthesize import generate_page, generate_mask, save_sample
from degrade import apply_degrade, DEGRADES


class Teacher:
    """Генератор учебных данных с адаптацией под слабые места Ученика."""
    
    def __init__(self, config_path, log_dir="./logs"):
        self.cfg = load_yaml(config_path)
        self.log = get_logger("teacher", str(Path(log_dir) / "teacher.log"))
        self.base_dir = ensure(self.cfg.get("base_dir", "./data/teacher"))
        self.generated_count = jload(self.base_dir / "generated_count.json", 0)
        self.issued_ids = set(jload(self.base_dir / "issued_ids.json", []))
        
    def get_focus_weights(self):
        """Получить веса фокусировки от Рефери (если есть)."""
        focus_path = self.base_dir / "focus_weights.json"
        return jload(focus_path, {})
    
    def select_degradations(self, round_num, focus_weights):
        """Выбрать типы и интенсивность искажений на основе раунда и фокуса."""
        base_intensity = min(1.0, 0.1 + round_num * 0.1)
        
        # Если есть фокус на определенных типах искажений
        deg_weights = focus_weights.get("degradations", {})
        
        degradations = []
        for deg_name in DEGRADES.keys():
            weight = deg_weights.get(deg_name, 0.5)
            if random.random() < weight:
                intensity = min(1.0, base_intensity + random.uniform(-0.1, 0.2))
                degradations.append((deg_name, intensity))
        
        # Всегда добавляем немного случайных искажений для разнообразия
        if not degradations and random.random() < 0.3:
            deg_name = random.choice(list(DEGRADES.keys()))
            degradations.append((deg_name, base_intensity * 0.5))
        
        return degradations
    
    def generate_sample(self, idx, round_num, focus_weights):
        """Сгенерировать один образец с учетом сложности раунда."""
        # Базовая сложность растет с раундом
        complexity = min(1.0, 0.2 + round_num * 0.15)
        
        # Параметры генерации
        width = random.randint(600, 1000)
        height = random.randint(400, 800)
        
        # Генерируем чистую страницу
        img, blocks = generate_page(width=width, height=height, seed=idx)
        mask = generate_mask(blocks, width, height)
        
        # Применяем искажения
        degradations = self.select_degradations(round_num, focus_weights)
        applied_degrades = []
        
        for deg_name, intensity in degradations:
            try:
                img = apply_degrade(img, deg_name, intensity)
                applied_degrades.append({"name": deg_name, "intensity": intensity})
            except Exception as e:
                self.log.warning(f"Не удалось применить {deg_name}: {e}")
        
        # С вероятностью генерируем "битые" данные
        is_broken = random.random() < self.cfg.get("broken_probability", 0.02)
        if is_broken:
            # Создаем заведомо проблемное изображение
            broken_type = random.choice(["black", "empty", "cropped"])
            if broken_type == "black":
                img = Image.new("RGB", (width, height), (0, 0, 0))
            elif broken_type == "empty":
                img = Image.new("RGB", (width, height), (255, 255, 255))
            elif broken_type == "cropped":
                img = img.crop((0, 0, width // 4, height // 4))
            
            applied_degrades.append({"name": "broken", "type": broken_type})
            blocks = []  # Нет разметки для битых данных
        
        metadata = {
            "id": idx,
            "round": round_num,
            "width": img.width,
            "height": img.height,
            "blocks": blocks,
            "degradations": applied_degrades,
            "is_broken": is_broken,
            "complexity": complexity,
        }
        
        return img, metadata, mask
    
    def get_batch(self, batch_size, round_num, focus_weights=None):
        """Сгенерировать батч образцов."""
        if focus_weights is None:
            focus_weights = self.get_focus_weights()
        
        samples = []
        for i in range(batch_size):
            idx = self.generated_count + i
            
            # Проверка на повторения
            while idx in self.issued_ids:
                idx += 1
            
            img, metadata, mask = self.generate_sample(idx, round_num, focus_weights)
            
            # Сохраняем
            img_path, meta_path, mask_path = save_sample(
                self.base_dir / f"round_{round_num}", 
                idx, 
                img, 
                metadata["blocks"], 
                mask
            )
            jdump(metadata, meta_path.replace(".json", "_full.json"))
            
            self.issued_ids.add(idx)
            
            samples.append({
                "id": idx,
                "image_path": img_path,
                "metadata_path": meta_path,
                "mask_path": mask_path,
                "metadata": metadata,
            })
        
        self.generated_count += batch_size
        jdump(self.generated_count, self.base_dir / "generated_count.json")
        jdump(list(self.issued_ids), self.base_dir / "issued_ids.json")
        
        self.log.info(f"Сгенерировано {batch_size} образцов для раунда {round_num}")
        return samples
    
    def save_focus_weights(self, weights):
        """Сохранить веса фокусировки от Рефери."""
        jdump(weights, self.base_dir / "focus_weights.json")
        self.log.info(f"Сохранены веса фокусировки: {weights}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="./config/teacher.yaml")
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--batch", type=int, default=5)
    args = ap.parse_args()
    
    # Создаем конфиг по умолчанию если нет
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        ensure(cfg_path.parent)
        jdump({
            "base_dir": "./data/teacher",
            "broken_probability": 0.02,
            "max_batch_size": 20,
        }, cfg_path)
    
    teacher = Teacher(args.config)
    focus = teacher.get_focus_weights()
    samples = teacher.get_batch(args.batch, args.round, focus)
    
    print(f"Сгенерировано {len(samples)} образцов:")
    for s in samples[:3]:
        print(f"  ID={s['id']}, broken={s['metadata']['is_broken']}, degs={len(s['metadata']['degradations'])}")
