#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Точка входа: запуск всех модулей для самообучения."""
import argparse
import sys
import time
from pathlib import Path

# Добавляем текущую директорию в path
sys.path.insert(0, str(Path(__file__).parent))

from common import ensure, jdump, get_logger
from referee import Referee
from teacher import Teacher
from student import Student


def main():
    ap = argparse.ArgumentParser(description="SelfLearn - автономная система самообучения")
    ap.add_argument("--action", choices=["run", "api", "test", "status"], default="run",
                    help="Действие: run (запуск цикла), api (веб-сервер), test (тест), status (статус)")
    ap.add_argument("--config-dir", type=str, default="./config", help="Директория с конфигами")
    ap.add_argument("--data-dir", type=str, default="./data", help="Директория для данных")
    ap.add_argument("--log-dir", type=str, default="./logs", help="Директория для логов")
    ap.add_argument("--competitions", type=int, default=2, help="Количество соревнований")
    ap.add_argument("--rounds", type=int, default=3, help="Раундов на соревнование")
    ap.add_argument("--tasks", type=int, default=5, help="Задач на раунд")
    ap.add_argument("--epochs", type=int, default=1, help="Эпох обучения")
    ap.add_argument("--host", type=str, default="0.0.0.0", help="Хост для API")
    ap.add_argument("--port", type=int, default=8000, help="Порт для API")
    
    args = ap.parse_args()
    
    # Создаем директории
    config_dir = ensure(args.config_dir)
    data_dir = ensure(args.data_dir)
    log_dir = ensure(args.log_dir)
    
    # Создаем конфиги по умолчанию если нет
    ref_cfg = config_dir / "referee.yaml"
    if not ref_cfg.exists():
        jdump({
            "base_dir": str(data_dir / "referee"),
            "num_competitions": args.competitions,
            "rounds_per_competition": args.rounds,
            "tasks_per_round": args.tasks,
            "training_epochs": args.epochs,
        }, ref_cfg)
    
    t_cfg = config_dir / "teacher.yaml"
    if not t_cfg.exists():
        jdump({
            "base_dir": str(data_dir / "teacher"),
            "broken_probability": 0.02,
            "max_batch_size": 20,
        }, t_cfg)
    
    s_cfg = config_dir / "student.yaml"
    if not s_cfg.exists():
        jdump({
            "base_dir": str(data_dir / "student"),
            "models": [
                {"name": "simple_classifier", "type": "simple"},
            ],
        }, s_cfg)
    
    # Инициализация логгера
    log = get_logger("main", str(log_dir / "main.log"))
    log.info(f"SelfLearn запущен: action={args.action}")
    
    if args.action == "status":
        referee = Referee(str(ref_cfg), str(log_dir))
        print(f"Состояние: {referee.state}")
        return 0
    
    elif args.action == "test":
        # Быстрый тест системы
        log.info("=== Запуск быстрого теста ===")
        
        teacher = Teacher(str(t_cfg), str(log_dir))
        student = Student(str(s_cfg), str(log_dir))
        referee = Referee(str(ref_cfg), str(log_dir))
        
        # Генерируем один образец
        samples = teacher.get_batch(3, round_num=1, focus_weights={})
        log.info(f"Сгенерировано {len(samples)} образцов")
        
        # Тестируем предсказание
        if samples:
            pred = student.predict(samples[0]["image_path"])
            log.info(f"Предсказание: {pred}")
        
        # Тестируем оценку
        eval_result = student.evaluate(samples)
        log.info(f"Оценка: {eval_result}")
        
        log.info("=== Тест завершен успешно ===")
        return 0
    
    elif args.action == "run":
        # Полный цикл самообучения
        log.info("=== Запуск полного цикла самообучения ===")
        
        teacher = Teacher(str(t_cfg), str(log_dir))
        student = Student(str(s_cfg), str(log_dir))
        referee = Referee(str(ref_cfg), str(log_dir))
        
        # Проверяем не было ли предыдущего запуска
        if referee.state.get("phase") == "running":
            log.warning("Обнаружен незавершенный процесс. Возобновление...")
            referee.resume()
        
        try:
            result = referee.run_full_cycle(
                teacher, 
                student, 
                num_competitions=args.competitions,
                rounds_per_comp=args.rounds,
                tasks_per_round=args.tasks,
            )
            
            log.info(f"Цикл завершен: {result}")
            print(f"\n{'='*60}")
            print(f"РЕЗУЛЬТАТЫ:")
            print(f"  Соревнований: {result['total_competitions']}")
            print(f"  Раундов: {result['total_rounds']}")
            print(f"  Задач: {result['total_tasks']}")
            print(f"  Общая точность: {result['overall_accuracy']:.3f}")
            print(f"  Лучшая модель: {result['best_model']}")
            print(f"{'='*60}\n")
            
            return 0
            
        except KeyboardInterrupt:
            log.info("Прервано пользователем")
            referee.state["phase"] = "stopped"
            referee.save_state()
            return 1
        except Exception as e:
            log.error(f"Ошибка: {e}", exc_info=True)
            return 1
    
    elif args.action == "api":
        # Запуск веб-сервера
        log.info(f"Запуск API сервера на {args.host}:{args.port}")
        
        try:
            import uvicorn
            from api import app
            uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            log.error("FastAPI или uvicorn не установлены. Установите: pip install fastapi uvicorn")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
