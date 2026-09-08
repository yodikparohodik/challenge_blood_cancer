# -*- coding: utf-8 -*-
"""Web API для управления самообучением (FastAPI)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from common import jload, jdump, ensure, get_logger
from referee import Referee
from teacher import Teacher
from student import Student


app = FastAPI(title="SelfLearn API", version="1.0.0")

# Глобальные объекты (инициализируются при старте)
referee = None
teacher = None
student = None
log = None


class ResetRequest(BaseModel):
    full: bool = False


class TrainRequest(BaseModel):
    competitions: int = 2
    rounds_per_competition: int = 3
    tasks_per_round: int = 5
    epochs: int = 1


@app.on_event("startup")
async def startup():
    global referee, teacher, student, log
    
    base_dir = Path("./data")
    config_dir = Path("./config")
    log_dir = Path("./logs")
    
    ensure(log_dir)
    log = get_logger("api", str(log_dir / "api.log"))
    
    # Инициализация модулей
    ref_cfg = config_dir / "referee.yaml"
    t_cfg = config_dir / "teacher.yaml"
    s_cfg = config_dir / "student.yaml"
    
    if not ref_cfg.exists():
        jdump({"base_dir": "./data/referee"}, ref_cfg)
    if not t_cfg.exists():
        jdump({"base_dir": "./data/teacher"}, t_cfg)
    if not s_cfg.exists():
        jdump({"base_dir": "./data/student", "models": [{"name": "simple", "type": "simple"}]}, s_cfg)
    
    referee = Referee(str(ref_cfg), str(log_dir))
    teacher = Teacher(str(t_cfg), str(log_dir))
    student = Student(str(s_cfg), str(log_dir))
    
    log.info("API запущен")


@app.get("/")
async def root():
    return {"message": "SelfLearn API v1.0", "status": "running"}


@app.get("/status")
async def get_status():
    """Получить текущее состояние системы."""
    if not referee:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return {
        "state": referee.state,
        "phase": referee.state.get("phase", "idle"),
        "competition": referee.state.get("competition", 0),
        "round": referee.state.get("round", 0),
    }


@app.get("/results")
async def get_results():
    """Получить результаты обучения."""
    if not referee:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    final_stats = jload(referee.base_dir / "final_stats.json", {})
    return final_stats


@app.post("/admin/reset")
async def reset(request: ResetRequest = None):
    """Сбросить состояние для нового обучения."""
    if not referee:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    full = request.full if request else False
    
    if full:
        # Полная очистка всех данных
        import shutil
        for d in ["referee", "teacher", "student"]:
            data_dir = referee.base_dir.parent / d
            if data_dir.exists():
                shutil.rmtree(data_dir)
        
        # Пересоздаем объекты
        await startup()
    
    # Сброс состояния
    referee.state = {
        "competition": 0,
        "round": 0,
        "task": 0,
        "phase": "idle",
    }
    referee.stats = {
        "competitions": [],
        "rounds": [],
        "tasks": [],
    }
    referee.save_state()
    
    log.info("Состояние сброшено")
    return {"status": "reset", "full": full}


@app.post("/admin/stop")
async def stop():
    """Остановить текущий процесс обучения."""
    if not referee:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    referee.state["phase"] = "stopped"
    referee.save_state()
    
    log.info("Обучение остановлено пользователем")
    return {"status": "stopped"}


@app.post("/train")
async def train(request: TrainRequest = None):
    """Запустить процесс обучения."""
    if not referee:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if referee.state.get("phase") not in ["idle", "finished", "stopped"]:
        raise HTTPException(status_code=409, detail="Training already in progress")
    
    req = request or TrainRequest()
    
    # Запускаем в фоне (в реальности нужно использовать background tasks)
    try:
        result = referee.run_full_cycle(
            teacher, 
            student, 
            num_competitions=req.competitions,
            rounds_per_comp=req.rounds_per_competition,
            tasks_per_round=req.tasks_per_round,
        )
        return {"status": "completed", "result": result}
    except Exception as e:
        log.error(f"Ошибка обучения: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def get_models():
    """Получить информацию о моделях."""
    if not student:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    history = jload(student.base_dir / "model_history.json", [])
    state = jload(student.base_dir / "state.json", {})
    
    return {
        "best_model": state.get("best_model"),
        "history": history[-10:],  # Последние 10 записей
    }


@app.get("/samples/{sample_id}")
async def get_sample(sample_id: int):
    """Получить информацию об образце."""
    if not teacher:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Ищем образец в данных учителя
    sample_path = teacher.base_dir / f"{sample_id:06d}.json"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample not found")
    
    return jload(sample_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
