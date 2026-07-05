"""Client for AEGIS-Env server."""

from openenv import EnvClient


def get_client(repo_id: str = "YashashMathur/AEGIS-ENV") -> EnvClient:
    """Get an EnvClient connected to the AEGIS-Env Space."""
    return EnvClient(repo_id=repo_id)
