# -*- coding: utf-8 -*-
"""Модуль Ученик: модели, инференс, дообучение."""
import os
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from common import load_yaml, ensure, jdump, jload, get_logger, iou, match_boxes, token_f1, mask_iou


class StudentModel:
    """Базовая модель для классификации/сегментации/детекции."""
    
    def __init__(self, name, model_type="simple"):
        self.name = name
        self.model_type = model_type
        self.is_trained = False
        self.version = 0
        
    def predict(self, image_path, metadata_path=None):
        """Предсказание для одного образца."""
        # Заглушка - будет переопределено в реальных моделях
        return {
            "classification": {"label": "unknown", "confidence": 0.5},
            "segments": [],
            "description": "",
            "is_broken": False,
        }
    
    def train(self, data_dir, epochs=1):
        """Обучение модели."""
        self.is_trained = True
        self.version += 1
        return {"loss": 0.5, "accuracy": 0.7}


class SimpleClassifier(StudentModel):
    """Простой классификатор на основе эвристик."""
    
    def predict(self, image_path, metadata_path=None):
        from PIL import Image
        import numpy as np
        
        img = Image.open(image_path)
        arr = np.asarray(img)
        
        # Эвристика для определения "битых" изображений
        mean_brightness = arr.mean()
        std_brightness = arr.std()
        
        is_broken = False
        label = "normal"
        confidence = 0.5
        
        if mean_brightness < 20:
            is_broken = True
            label = "black"
            confidence = 0.95
        elif mean_brightness > 240 and std_brightness < 10:
            is_broken = True
            label = "empty"
            confidence = 0.95
        elif std_brightness < 20:
            is_broken = True
            label = "low_contrast"
            confidence = 0.8
        
        # Простая сегментация по контрасту
        segments = []
        if not is_broken:
            gray = arr.mean(axis=2) if len(arr.shape) == 3 else arr
            threshold = np.percentile(gray, 30)
            mask = gray < threshold
            
            # Находим связные области (упрощенно)
            rows = np.any(mask, axis=1)
            cols = np.any(mask, axis=0)
            if rows.any() and cols.any():
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]
                segments.append([int(cmin), int(rmin), int(cmax), int(rmax)])
        
        description = f"Image type: {label}, brightness: {mean_brightness:.1f}"
        
        return {
            "classification": {"label": label, "confidence": confidence},
            "segments": segments,
            "description": description,
            "is_broken": is_broken,
        }


class Student:
    """Модуль Ученик: управление моделями, инференс, обучение."""
    
    def __init__(self, config_path, log_dir="./logs"):
        self.cfg = load_yaml(config_path)
        self.log = get_logger("student", str(Path(log_dir) / "student.log"))
        self.base_dir = ensure(self.cfg.get("base_dir", "./data/student"))
        self.models_dir = ensure(self.base_dir / "models")
        
        # Реестр моделей
        self.models = {}
        self.best_model_name = None
        self.model_history = jload(self.base_dir / "model_history.json", [])
        
        # Инициализация моделей из конфига
        for mcfg in self.cfg.get("models", []):
            name = mcfg.get("name", "default")
            mtype = mcfg.get("type", "simple")
            self.models[name] = SimpleClassifier(name, mtype)
        
        if not self.models:
            self.models["default"] = SimpleClassifier("default")
        
        self.log.info(f"Инициализировано {len(self.models)} моделей")
    
    def predict(self, image_path, metadata_path=None, model_name=None):
        """Предсказание для одного образца используя лучшую или указанную модель."""
        if model_name is None:
            model_name = self.best_model_name or list(self.models.keys())[0]
        
        model = self.models.get(model_name)
        if not model:
            self.log.error(f"Модель {model_name} не найдена")
            return None
        
        return model.predict(image_path, metadata_path)
    
    def evaluate(self, samples, model_name=None):
        """Оценка качества модели на выборке."""
        if model_name is None:
            model_name = self.best_model_name or list(self.models.keys())[0]
        
        model = self.models.get(model_name)
        if not model:
            return None
        
        results = {
            "total": len(samples),
            "correct_class": 0,
            "correct_broken": 0,
            "iou_segments": [],
            "token_f1_desc": [],
        }
        
        for sample in samples:
            pred = self.predict(sample["image_path"], sample.get("metadata_path"), model_name)
            if pred is None:
                continue
            
            # Загружаем ground truth
            meta = jload(sample["metadata_path"])
            gt_is_broken = meta.get("is_broken", False)
            gt_blocks = meta.get("blocks", [])
            
            # Классификация broken/not broken
            if pred["is_broken"] == gt_is_broken:
                results["correct_broken"] += 1
            
            # IoU для сегментов
            if gt_blocks and pred["segments"]:
                pred_boxes = pred["segments"]
                gt_boxes = [b["bbox"] for b in gt_blocks]
                p, r, miou = match_boxes(pred_boxes, gt_boxes)
                results["iou_segments"].append(miou)
            
            # Token F1 для описания (если есть GT текст)
            if gt_blocks:
                gt_text = " ".join(b.get("text", "") for b in gt_blocks)
                if gt_text:
                    f1 = token_f1(pred["description"], gt_text)
                    results["token_f1_desc"].append(f1)
        
        # Вычисляем средние метрики
        results["avg_iou"] = sum(results["iou_segments"]) / len(results["iou_segments"]) if results["iou_segments"] else 0.0
        results["avg_token_f1"] = sum(results["token_f1_desc"]) / len(results["token_f1_desc"]) if results["token_f1_desc"] else 0.0
        results["accuracy_broken"] = results["correct_broken"] / results["total"] if results["total"] > 0 else 0.0
        
        return results
    
    def train_models(self, train_samples, val_samples=None, epochs=1):
        """Обучение всех доступных моделей и выбор лучшей."""
        self.log.info(f"Начало обучения на {len(train_samples)} образцах, эпох: {epochs}")
        
        best_score = -1
        best_model = None
        
        for name, model in self.models.items():
            self.log.info(f"Обучение модели {name}...")
            
            # Тренировка (заглушка - в реальности здесь будет настоящее обучение)
            train_result = model.train(str(self.base_dir / "train"), epochs)
            
            # Оценка на валидации
            if val_samples:
                eval_result = self.evaluate(val_samples, name)
                score = eval_result["avg_iou"] * 0.5 + eval_result["accuracy_broken"] * 0.5
            else:
                score = train_result.get("accuracy", 0.5)
            
            self.log.info(f"Модель {name}: score={score:.4f}")
            
            if score > best_score:
                best_score = score
                best_model = name
            
            # Сохраняем историю
            self.model_history.append({
                "model": name,
                "score": score,
                "train_result": train_result,
                "timestamp": str(Path(__file__).stat().st_mtime),
            })
        
        self.best_model_name = best_model
        jdump(self.model_history, self.base_dir / "model_history.json")
        self.log.info(f"Лучшая модель: {best_model} (score={best_score:.4f})")
        
        return {"best_model": best_model, "score": best_score}
    
    def analyze_weaknesses(self, all_results):
        """Анализ слабых мест для передачи фокуса Учителю."""
        weaknesses = {
            "degradations": {},
            "task_types": {},
        }
        
        # Анализируем ошибки по типам искажений
        deg_errors = {}
        deg_total = {}
        
        for result in all_results:
            meta = jload(result.get("metadata_path", ""))
            if not meta:
                continue
            
            degs = meta.get("degradations", [])
            is_error = not result.get("correct", False)
            
            for deg in degs:
                deg_name = deg.get("name", "unknown")
                deg_total[deg_name] = deg_total.get(deg_name, 0) + 1
                if is_error:
                    deg_errors[deg_name] = deg_errors.get(deg_name, 0) + 1
        
        # Вычисляем веса для фокуса
        for deg_name in deg_total:
            error_rate = deg_errors.get(deg_name, 0) / deg_total[deg_name]
            weaknesses["degradations"][deg_name] = min(1.0, error_rate * 2)
        
        return weaknesses
    
    def save_state(self):
        """Сохранение состояния Ученика."""
        state = {
            "best_model": self.best_model_name,
            "model_count": len(self.models),
            "history_length": len(self.model_history),
        }
        jdump(state, self.base_dir / "state.json")
        self.log.info("Состояние сохранено")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="./config/student.yaml")
    ap.add_argument("--action", choices=["predict", "train", "eval"], default="predict")
    ap.add_argument("--image", type=str, help="Путь к изображению")
    args = ap.parse_args()
    
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        ensure(cfg_path.parent)
        jdump({
            "base_dir": "./data/student",
            "models": [
                {"name": "simple_classifier", "type": "simple"},
            ],
        }, cfg_path)
    
    student = Student(args.config)
    
    if args.action == "predict" and args.image:
        result = student.predict(args.image)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "train":
        # Для теста создаем фиктивные данные
        train_samples = [{"image_path": args.image or "./test.png", "metadata_path": None}]
        result = student.train_models(train_samples, epochs=1)
        print(json.dumps(result, indent=2, ensure_ascii=False))
