"""
Overseer Worker Dispatch Module
Add this to your overseer to dispatch tasks to worker agents.
"""

import os
import asyncio
import httpx
from typing import List, Optional

# === WORKER CONFIG ===
WORKERS = {
    "friend_hf": os.environ.get(
        "FRIEND_WORKER_URL", "https://hitanshu10-WORKER.hf.space/execute"
    ),
    "local": os.environ.get(
        "LOCAL_WORKER_URL", "https://struggle-trend-possible.ngrok-free.dev/execute"
    ),
    "friend_laptop": os.environ.get(
        "FRIEND_LAPTOP_URL",
        "https://palpitant-silvicolous-jamey.ngrok-free.dev/execute",
    ),
}

ROUND_ROBIN = {"friend_hf": 0, "local": 0}


async def dispatch_to_worker(task: dict, worker_name: Optional[str] = None) -> dict:
    """
    Send task to a worker and get result.

    Args:
        task: Dict with keys like 'instructions', 'context', 'worker_role', 'task_id'
        worker_name: Specific worker to use, or None for round-robin

    Returns:
        Dict with 'status', 'worker_id', 'result'
    """
    # Pick worker
    if worker_name is None:
        worker_name = "friend_hf"  # Default to friend
        # To use both in round-robin:
        # worker_name = min(ROUND_ROBIN, key=ROUND_ROBIN.get)
        # ROUND_ROBIN[worker_name] += 1

    worker_url = WORKERS.get(worker_name)
    if not worker_url:
        return {"status": "error", "error": f"Unknown worker: {worker_name}"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(worker_url, json=task)
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "worker_id": worker_name,
                    "result": result.get("result", {}),
                }
            else:
                return {
                    "status": "error",
                    "worker_id": worker_name,
                    "error": f"Worker returned {response.status_code}",
                }
    except Exception as e:
        return {"status": "error", "worker_id": worker_name, "error": str(e)}


async def dispatch_to_all_workers(task: dict) -> List[dict]:
    """Send task to all workers, return all results."""
    results = []
    for worker_name, worker_url in WORKERS.items():
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(worker_url, json=task)
                if response.status_code == 200:
                    results.append(
                        {
                            "worker_id": worker_name,
                            "result": response.json().get("result", {}),
                        }
                    )
        except Exception as e:
            results.append({"worker_id": worker_name, "error": str(e)})
    return results


def get_worker_urls() -> dict:
    """Get current worker URLs."""
    return WORKERS.copy()


def set_worker_url(name: str, url: str):
    """Update a worker URL (e.g., after starting ngrok)."""
    WORKERS[name] = url
    print(f"Updated worker '{name}' URL to: {url}")
