"""
SelfLearn - FastAPI Web Server
"""
import os
import sys
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import setup_logging, DEFAULT_CONFIG
from referee import Referee


app = FastAPI(
    title="SelfLearn API",
    description="Autonomous self-learning system API",
    version="1.0.0"
)

# Global referee instance
referee: Optional[Referee] = None
logger = None


def get_referee() -> Referee:
    """Get or create referee instance."""
    global referee, logger
    
    if referee is None:
        logger = setup_logging('INFO')
        referee = Referee(
            data_dir='data',
            config=DEFAULT_CONFIG,
            logger=logger
        )
    
    return referee


class TrainRequest(BaseModel):
    """Request model for training."""
    competitions: int = 3
    rounds: int = 5
    tasks_per_round: int = 20
    epochs: int = 10
    batch_size: int = 32


class AdminAction(BaseModel):
    """Request model for admin actions."""
    confirm: bool = True


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SelfLearn API",
        "version": "1.0.0",
        "description": "Autonomous self-learning system"
    }


@app.get("/status")
async def get_status():
    """Get current system status."""
    try:
        ref = get_referee()
        status = ref.get_status()
        return {
            "status": "ok",
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results")
async def get_results():
    """Get all competition results."""
    try:
        ref = get_referee()
        results = ref.get_results()
        return {
            "status": "ok",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def get_models():
    """Get information about available models."""
    try:
        ref = get_referee()
        models = ref.get_models_info()
        return {
            "status": "ok",
            "data": models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/{competition_id}")
async def get_metrics(competition_id: int):
    """Get detailed metrics for a specific competition."""
    try:
        ref = get_referee()
        results = ref.get_results()
        
        competitions = results.get('competitions', [])
        if competition_id < 1 or competition_id > len(competitions):
            raise HTTPException(
                status_code=404,
                detail=f"Competition {competition_id} not found"
            )
        
        competition = competitions[competition_id - 1]
        return {
            "status": "ok",
            "data": competition
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
async def start_training(
    request: TrainRequest,
    background_tasks: BackgroundTasks
):
    """Start training process."""
    try:
        ref = get_referee()
        
        if ref.is_running:
            raise HTTPException(
                status_code=400,
                detail="Training already in progress"
            )
        
        # Run training in background
        def run_training():
            try:
                ref.run_competition(
                    competitions=request.competitions,
                    rounds_per_competition=request.rounds,
                    tasks_per_round=request.tasks_per_round,
                    epochs=request.epochs,
                    batch_size=request.batch_size
                )
            except Exception as e:
                logger.error(f"Training failed: {e}")
        
        background_tasks.add_task(run_training)
        
        return {
            "status": "started",
            "message": f"Training started with {request.competitions} competitions",
            "parameters": {
                "competitions": request.competitions,
                "rounds": request.rounds,
                "tasks_per_round": request.tasks_per_round
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/reset")
async def reset_system(request: AdminAction):
    """Reset all system state and results."""
    try:
        if not request.confirm:
            raise HTTPException(
                status_code=400,
                detail="Confirmation required"
            )
        
        ref = get_referee()
        ref.reset()
        
        # Reset global referee to force re-initialization
        global referee
        referee = None
        
        return {
            "status": "ok",
            "message": "System reset complete"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/stop")
async def stop_training(request: AdminAction):
    """Stop current training."""
    try:
        ref = get_referee()
        
        if not ref.is_running:
            raise HTTPException(
                status_code=400,
                detail="No training in progress"
            )
        
        ref.stop()
        
        return {
            "status": "ok",
            "message": "Stop requested"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
