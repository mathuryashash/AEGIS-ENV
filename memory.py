import json
import os
from typing import List, Dict, Optional


class MemoryLedger:
    """MEM-01/05: Memory ledger with JSON persistence tracing worker violation histories."""

    def __init__(self):
        self.entries: List[Dict[str, str]] = []

    def add(self, worker_id: str, violation_type: str, evidence: str) -> None:
        """Adds a new memory, truncating evidence to 200 chars to avoid prompt bloat."""
        clipped_evidence = evidence[:200]
        self.entries.append(
            {
                "worker_id": worker_id,
                "violation_type": violation_type,
                "evidence": clipped_evidence,
            }
        )
        # Maintain hard cap of 5000
        if len(self.entries) > 5000:
            self.entries.pop(0)

    def retrieve(self, worker_id: str, violation_type: str) -> List[Dict[str, str]]:
        """MEM-02: Exact keyword match filtering returning max 3 items."""
        matches = [
            e
            for e in self.entries
            if e["worker_id"] == worker_id and e["violation_type"] == violation_type
        ]
        # Return top_k=3 (the 3 most recent logically, so fetch from end or just standard)
        return matches[-3:]

    def clear(self) -> None:
        """MEM-04: Clear ledger for memory ablation experiments."""
        self.entries.clear()

    def save(self, path: Optional[str] = None) -> None:
        """MEM-01: Serializes the entire chain manually to JSON to prevent mid-rollout disk friction."""
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "data", "memory_ledger.json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.entries, f, indent=2)

    def load(self, path: Optional[str] = None) -> None:
        """Reloads ledger state."""
        load_path = (
            path
            if path is not None
            else os.path.join(os.path.dirname(__file__), "data", "memory_ledger.json")
        )
        try:
            with open(load_path, "r") as f:
                self.entries = json.load(f)
        except FileNotFoundError:
            self.entries = []
