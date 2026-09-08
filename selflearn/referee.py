# -*- coding: utf-8 -*-
"""Модуль Рефери: оркестрация соревнований, раундов, статистика."""
import os
import sys
import time
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from common import load_yaml, ensure, jdump, jload, get_logger


class Referee:
    """Оркестратор цикла самообучения: соревнования, раунды, статистика."""
    
    def __init__(self, config_path, log_dir="./logs"):
        self.cfg = load_yaml(config_path)
        self.log = get_logger("referee", str(Path(log_dir) / "referee.log"))
        self.base_dir = ensure(self.cfg.get("base_dir", "./data/referee"))
        
        # Состояние
        self.state = jload(self.base_dir / "state.json", {
            "competition": 0,
            "round": 0,
            "task": 0,
            "phase": "idle",  # idle, competition, round, finished
        })
        
        # Статистика
        self.stats = jload(self.base_dir / "stats.json", {
            "competitions": [],
            "rounds": [],
            "tasks": [],
        })
        
        self.log.info(f"Рефери инициализирован: competition={self.state['competition']}, round={self.state['round']}")
    
    def start_competition(self):
        """Начало нового соревнования."""
        self.state["competition"] += 1
        self.state["round"] = 0
        self.state["phase"] = "competition"
        
        comp_stats = {
            "id": self.state["competition"],
            "start_time": time.time(),
            "rounds": [],
        }
        self.stats["competitions"].append(comp_stats)
        
        self.log.info(f"=== Начато соревнование #{self.state['competition']} ===")
        self.save_state()
        return self.state["competition"]
    
    def start_round(self, competition_id=None):
        """Начало нового раунда."""
        if competition_id is None:
            competition_id = self.state["competition"]
        
        self.state["round"] += 1
        self.state["task"] = 0
        self.state["phase"] = "round"
        
        round_stats = {
            "competition": competition_id,
            "round": self.state["round"],
            "start_time": time.time(),
            "tasks": [],
            "results": [],
        }
        self.stats["rounds"].append(round_stats)
        
        self.log.info(f"--- Раунд #{self.state['round']} (соревнование #{competition_id}) ---")
        self.save_state()
        return self.state["round"]
    
    def run_task(self, teacher, student, task_data):
        """Выполнение одной задачи: Учитель дает данные, Ученик предсказывает."""
        self.state["task"] += 1
        
        # Получаем данные от Учителя
        sample = task_data
        
        # Ученик делает предсказание
        pred = student.predict(
            sample["image_path"],
            sample.get("metadata_path")
        )
        
        # Загружаем правильный ответ
        meta = jload(sample["metadata_path"])
        
        # Сравниваем
        result = {
            "task": self.state["task"],
            "sample_id": sample["id"],
            "prediction": pred,
            "ground_truth": meta,
            "correct": pred.get("is_broken") == meta.get("is_broken", False),
            "time": time.time(),
        }
        
        self.stats["rounds"][-1]["tasks"].append(result)
        self.log.debug(f"Задача {self.state['task']}: correct={result['correct']}")
        
        return result
    
    def end_round(self, student, teacher):
        """Завершение раунда: статистика, анализ слабостей, подготовка к следующему."""
        round_stats = self.stats["rounds"][-1]
        round_stats["end_time"] = time.time()
        round_stats["duration"] = round_stats["end_time"] - round_stats["start_time"]
        
        # Подсчет статистики
        total_tasks = len(round_stats["tasks"])
        correct_tasks = sum(1 for t in round_stats["tasks"] if t["correct"])
        accuracy = correct_tasks / total_tasks if total_tasks > 0 else 0.0
        
        round_stats["accuracy"] = accuracy
        round_stats["total"] = total_tasks
        round_stats["correct"] = correct_tasks
        
        self.log.info(f"Раунд завершен: {correct_tasks}/{total_tasks} верно (accuracy={accuracy:.3f})")
        
        # Анализ слабых мест для фокусировки Учителя
        weaknesses = student.analyze_weaknesses(round_stats["tasks"])
        
        # Передаем фокус Учителю
        teacher.save_focus_weights(weaknesses)
        
        self.log.info(f"Слабые места: {weaknesses}")
        self.save_state()
        
        return {
            "accuracy": accuracy,
            "total": total_tasks,
            "correct": correct_tasks,
            "weaknesses": weaknesses,
        }
    
    def end_competition(self, student, all_train_samples):
        """Завершение соревнования: обучение на всех данных, выбор лучшей модели."""
        comp_stats = self.stats["competitions"][-1]
        comp_stats["end_time"] = time.time()
        
        self.log.info(f"=== Завершение соревнования #{self.state['competition']} ===")
        
        # Разделяем данные на train/val
        split_idx = int(len(all_train_samples) * 0.8)
        train_samples = all_train_samples[:split_idx]
        val_samples = all_train_samples[split_idx:]
        
        # Обучаем модели
        epochs = self.cfg.get("training_epochs", 1)
        train_result = student.train_models(train_samples, val_samples, epochs)
        
        comp_stats["best_model"] = train_result.get("best_model")
        comp_stats["best_score"] = train_result.get("score")
        
        self.log.info(f"Лучшая модель соревнования: {train_result.get('best_model')} (score={train_result.get('score'):.4f})")
        
        self.state["phase"] = "finished"
        self.save_state()
        
        return comp_stats
    
    def run_full_cycle(self, teacher, student, num_competitions=3, rounds_per_comp=5, tasks_per_round=10):
        """Полный цикл самообучения."""
        all_samples = []
        
        for comp in range(num_competitions):
            self.start_competition()
            
            for rnd in range(rounds_per_comp):
                self.start_round()
                
                # Учитель генерирует батч данных
                focus = teacher.get_focus_weights()
                samples = teacher.get_batch(tasks_per_round, self.state["round"], focus)
                all_samples.extend(samples)
                
                # Выполняем задачи
                for sample in samples:
                    self.run_task(teacher, student, sample)
                
                # Завершаем раунд
                self.end_round(student, teacher)
                
                # Даем время Ученику на подготовку (в реальности здесь может быть дообучение)
                time.sleep(0.1)
            
            # Завершаем соревнование
            self.end_competition(student, all_samples)
        
        self.log.info("=== Полный цикл завершен ===")
        return self.get_final_stats()
    
    def get_final_stats(self):
        """Получение итоговой статистики."""
        # Считаем total_tasks корректно
        total_tasks = 0
        for r in self.stats["rounds"]:
            if "total" in r:
                total_tasks += r["total"]
            elif "tasks" in r:
                total_tasks += len(r["tasks"])
        
        accuracies = [r.get("accuracy", 0.0) for r in self.stats["rounds"] if "accuracy" in r]
        overall_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
        
        final = {
            "total_competitions": len(self.stats["competitions"]),
            "total_rounds": len(self.stats["rounds"]),
            "total_tasks": total_tasks,
            "overall_accuracy": overall_accuracy,
            "best_model": self.stats["competitions"][-1].get("best_model") if self.stats["competitions"] else None,
            "competitions": self.stats["competitions"],
        }
        
        jdump(final, self.base_dir / "final_stats.json")
        return final
    
    def save_state(self):
        """Сохранение состояния."""
        jdump(self.state, self.base_dir / "state.json")
        jdump(self.stats, self.base_dir / "stats.json")
    
    def resume(self):
        """Возобновление с последнего состояния."""
        saved_state = jload(self.base_dir / "state.json")
        if saved_state:
            self.state = saved_state
            self.log.info(f"Состояние восстановлено: competition={self.state['competition']}, round={self.state['round']}")
        return self.state


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="./config/referee.yaml")
    ap.add_argument("--action", choices=["run", "resume", "status"], default="status")
    args = ap.parse_args()
    
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        ensure(cfg_path.parent)
        jdump({
            "base_dir": "./data/referee",
            "num_competitions": 2,
            "rounds_per_competition": 3,
            "tasks_per_round": 5,
            "training_epochs": 1,
        }, cfg_path)
    
    referee = Referee(args.config)
    
    if args.action == "status":
        print(json.dumps(referee.state, indent=2, ensure_ascii=False))
    elif args.action == "run":
        # Для демонстрации создаем упрощенные Teacher и Student
        from teacher import Teacher
        from student import Student
        
        t_cfg = Path("./config/teacher.yaml")
        if not t_cfg.exists():
            jdump({"base_dir": "./data/teacher"}, t_cfg)
        
        s_cfg = Path("./config/student.yaml")
        if not s_cfg.exists():
            jdump({"base_dir": "./data/student", "models": [{"name": "simple", "type": "simple"}]}, s_cfg)
        
        teacher = Teacher(str(t_cfg))
        student = Student(str(s_cfg))
        
        result = referee.run_full_cycle(teacher, student, num_competitions=2, rounds_per_comp=2, tasks_per_round=3)
        print(json.dumps(result, indent=2, ensure_ascii=False))
