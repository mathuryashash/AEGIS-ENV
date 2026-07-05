"""Client for AEGIS-Env environment.

This module provides a client interface for connecting to the AEGIS-Env
FastAPI server running on Hugging Face Spaces.
"""

import os
from openenv.core.generic_client import GenericEnvClient


def get_client(base_url: str = None) -> GenericEnvClient:
    """Get an EnvClient connected to the AEGIS-Env Space or local server.

    Args:
        base_url: HF Space URL or local URL (defaults to env var AEGIS_BASE_URL)

    Returns:
        A GenericEnvClient instance connected to the AEGIS-Env server.
    """
    base_url = base_url or os.environ.get("AEGIS_BASE_URL", "http://localhost:7860")
    client = GenericEnvClient(base_url=base_url)
    return client.sync()
