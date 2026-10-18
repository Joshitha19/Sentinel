"""
Training & Telemetry API Routes.
Manages asynchronous training runs, curriculum adjustments, and real-time state.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import threading
import json
import time
import asyncio
from pathlib import Path

from app.config import RESULTS_DIR
from app.domains import get_domain
from app.core.splits import create_splits
from app.core.loop import SentinelTrainingLoop
from app.api.ws_stream import ws_manager

router = APIRouter(prefix="/api/train", tags=["training"])

# Persistent State File
RUNS_FILE = RESULTS_DIR / "runs.json"

# In-memory execution state
TRAINING_STATE = {
    "status": "idle",  # "idle" | "running" | "completed" | "error"
    "domain_id": "transactions",
    "round": 0,
    "total_rounds": 12,
    "weights": {"alpha": 1.0, "beta": 1.2, "gamma": 1.0},
    "latest_event": None,
    "error_message": None,
    "active_archive_size": 0,
    "active_loop": None,
}


def load_stored_runs() -> Dict[str, Any]:
    if RUNS_FILE.exists():
        try:
            with open(RUNS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_stored_run(run_id: str, data: Dict[str, Any]):
    runs = load_stored_runs()
    runs[run_id] = data
    runs["latest_run"] = data
    with open(RUNS_FILE, "w") as f:
        json.dump(runs, f, indent=2)


class StartTrainingRequest(BaseModel):
    domain_id: str = "transactions"
    alpha: float = 1.0
    beta: float = 1.2
    gamma: float = 1.0
    curriculum: bool = True
    n_rounds: int = 12
    max_samples: int = 4000
    use_offline_sim: bool = False


class AdjustWeightsRequest(BaseModel):
    alpha: float
    beta: float
    gamma: float


def run_training_worker(request: StartTrainingRequest, loop_async: asyncio.AbstractEventLoop):
    """Worker executed in background thread."""
    global TRAINING_STATE
    try:
        domain = get_domain(request.domain_id)
        TRAINING_STATE["status"] = "running"
        TRAINING_STATE["domain_id"] = request.domain_id
        TRAINING_STATE["total_rounds"] = request.n_rounds
        TRAINING_STATE["weights"] = {"alpha": request.alpha, "beta": request.beta, "gamma": request.gamma}

        # Broadcast start
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast({
                "event": "training_started",
                "data": {"domain": domain.name, "rounds": request.n_rounds}
            }),
            loop_async
        )

        # Load data & create splits
        df, X, y = domain.load_data(
            use_offline_sim=request.use_offline_sim,
            max_samples=request.max_samples
        )
        splits = create_splits(
            X, y,
            train_ratio=0.60,
            val_ratio=0.15,
            calib_ratio=0.15,
            test_ratio=0.10,
            hidden_class=domain.hidden_class_label
        )

        sentinel_loop = SentinelTrainingLoop(
            domain=domain,
            splits=splits,
            alpha=request.alpha,
            beta=request.beta,
            gamma=request.gamma,
            curriculum=request.curriculum,
            n_rounds=request.n_rounds,
            random_seed=42
        )
        TRAINING_STATE["active_loop"] = sentinel_loop

        def on_event(event_dict: Dict[str, Any]):
            event_name = event_dict.get("event")
            data = event_dict.get("data", {})
            if event_name == "training_round":
                TRAINING_STATE["round"] = data.get("round", 0)
                TRAINING_STATE["latest_event"] = data
                TRAINING_STATE["active_archive_size"] = data.get("archive_size", 0)
                TRAINING_STATE["weights"] = data.get("weights", TRAINING_STATE["weights"])

            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast(event_dict),
                loop_async
            )

        report = sentinel_loop.run(event_callback=on_event)

        TRAINING_STATE["status"] = "completed"
        run_id = f"run_{domain.id}_{int(time.time())}"
        save_stored_run(run_id, {
            "run_id": run_id,
            "domain_id": domain.id,
            "domain_name": domain.name,
            "timestamp": time.time(),
            "report": report
        })

    except Exception as e:
        TRAINING_STATE["status"] = "error"
        TRAINING_STATE["error_message"] = str(e)
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast({"event": "training_error", "data": {"error": str(e)}}),
            loop_async
        )


@router.post("/start")
def start_training(request: StartTrainingRequest, background_tasks: BackgroundTasks):
    """Initiates live training run."""
    global TRAINING_STATE
    if TRAINING_STATE["status"] == "running":
        raise HTTPException(status_code=400, detail="Training is already running")

    loop_async = asyncio.get_event_loop()
    threading.Thread(
        target=run_training_worker,
        args=(request, loop_async),
        daemon=True
    ).start()

    return {"message": "Training initiated successfully", "domain": request.domain_id}


@router.post("/stop")
def stop_training():
    """Cancels active training run."""
    global TRAINING_STATE
    TRAINING_STATE["status"] = "idle"
    return {"message": "Training stopped"}


@router.get("/status")
def get_training_status():
    """Returns current telemetry and execution status."""
    return {
        "status": TRAINING_STATE["status"],
        "domain_id": TRAINING_STATE["domain_id"],
        "round": TRAINING_STATE["round"],
        "total_rounds": TRAINING_STATE["total_rounds"],
        "weights": TRAINING_STATE["weights"],
        "active_archive_size": TRAINING_STATE["active_archive_size"],
        "latest_event": TRAINING_STATE["latest_event"],
        "error_message": TRAINING_STATE["error_message"]
    }


@router.post("/adjust_weights")
def adjust_weights(req: AdjustWeightsRequest):
    """Dynamically adjusts alpha, beta, gamma during training."""
    global TRAINING_STATE
    TRAINING_STATE["weights"] = {"alpha": req.alpha, "beta": req.beta, "gamma": req.gamma}
    active_loop = TRAINING_STATE.get("active_loop")
    if active_loop:
        active_loop.alpha_base = req.alpha
        active_loop.beta_base = req.beta
        active_loop.gamma_base = req.gamma
    return {"message": "Weights updated", "weights": TRAINING_STATE["weights"]}
