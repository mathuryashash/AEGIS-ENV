import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .environment import AEGISEnvironment
from .models import AEGISAction


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize environment on startup, not at import time."""
    scenario_dir = os.getenv("SCENARIO_DIR", None)
    worker_mode = os.getenv("WORKER_MODE", "scripted")
    memory_enabled = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
    seed = int(os.getenv("SEED", "42"))

    env = AEGISEnvironment(
        scenario_dir=scenario_dir,  # type: ignore
        worker_mode=worker_mode,
        memory_enabled=memory_enabled,
        seed=seed,
    )
    app.state.env = env
    yield


app = FastAPI(
    title="AEGIS-Env Server",
    description="OpenEnv backend for RL model oversight.",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "AEGIS-ENV is running. Use POST /reset and POST /step."}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reset")
async def reset_env(request: Request):
    """Starts a new episode, generating scenario logs and clearing limits."""
    env = request.app.state.env
    obs, info = env.reset()
    return {"observation": obs, "info": info}


@app.post("/step")
async def step_env(request: Request):
    """Layer-1 FIX: Accepts any dict body — validates internally, never returns 422.

    Invalid actions yield reward=0.0 via the format gate instead of crashing.
    """
    env = request.app.state.env

    # Parse body leniently
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Internal validation — mirrors environment.py step() gate
    try:
        validated = AEGISAction(**body)
        action_dict = validated.model_dump()
        action_dict["__valid__"] = True
    except (ValidationError, TypeError):
        action_dict = {
            "decision": "ALLOW",
            "confidence": 0.5,
            "violation_type": "none",
            "explanation": "",
            "__valid__": False,  # format gate → 0.0 reward, episode continues
        }

    obs, reward, done, info = env.step(action_dict)
    return {"observation": obs, "reward": reward, "done": done, "info": info}
