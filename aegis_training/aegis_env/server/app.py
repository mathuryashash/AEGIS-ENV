import os
import uuid
from collections import OrderedDict
from typing import Dict
from fastapi import FastAPI, Request
from pydantic import ValidationError

from aegis_env.environment import AEGISEnvironment
from aegis_env.models import AEGISAction

scenario_dir = os.getenv("SCENARIO_DIR", None)
worker_mode = os.getenv("WORKER_MODE", "scripted")
memory_enabled = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
seed = int(os.getenv("SEED", "42"))

# Session registry — each client gets its own env instance
_sessions: OrderedDict[str, AEGISEnvironment] = OrderedDict()

MAX_SESSIONS = 100

def _get_or_create_env(session_id: str) -> AEGISEnvironment:
    if session_id in _sessions:
        _sessions.move_to_end(session_id)
        return _sessions[session_id]
    env = AEGISEnvironment(
        scenario_dir=scenario_dir,
        worker_mode=worker_mode,
        memory_enabled=memory_enabled,
        seed=seed,
    )
    _sessions[session_id] = env
    if len(_sessions) > MAX_SESSIONS:
        _sessions.popitem(last=False)  # evict oldest
    return env

app = FastAPI(title="AEGIS-Env", description="OpenEnv backend for RL model oversight.")


@app.get("/")
async def root():
    return {
        "name": "AEGIS-Env",
        "description": "OpenEnv backend for RL model oversight",
        "version": "1.0",
        "endpoints": {
            "POST /reset": "Start a new episode (returns session_id)",
            "POST /step": "Execute an action (body: {session_id, decision, confidence, violation_type, explanation})",
        },
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reset")
async def reset_env(request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    session_id = body.get("session_id") or str(uuid.uuid4())
    env = _get_or_create_env(session_id)
    obs, info = env.reset()
    return {"session_id": session_id, "observation": obs, "info": info}


@app.post("/step")
async def step_env(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    session_id = body.get("session_id", "default")
    env = _get_or_create_env(session_id)

    try:
        validated = AEGISAction(**{k: v for k, v in body.items() if k != "session_id"})
        action_dict = validated.model_dump()
        action_dict["__valid__"] = True
    except (ValidationError, TypeError):
        action_dict = {
            "decision": "ALLOW",
            "confidence": 0.5,
            "violation_type": "none",
            "explanation": "",
            "__valid__": False,
        }

    obs, reward, done, info = env.step(action_dict)
    return {
        "session_id": session_id,
        "observation": obs,
        "reward": float(reward),
        "done": done,
        "info": info,
    }


def main():
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
