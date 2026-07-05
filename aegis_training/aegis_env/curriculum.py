"""
Curriculum scheduling and scenario loading for AEGIS-Env.
"""

import os
import json
import random
from typing import Dict, Any, Optional

from scripts.adversarial_generator import AdversarialGenerator

MAX_TOKENS = 300  # Layer-3: token cap (~300 words)


def truncate_to_tokens(text: str, max_tokens: int = MAX_TOKENS) -> str:
    """Layer-3 fix: hardcap tokens to prevent context blowup during training."""
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens]) + " [TRUNCATED]"


def wrap_with_delimiters(text: str) -> str:
    """Layer-3 fix: fence worker output to prevent prompt injection."""
    return f"[WORKER_THOUGHTS_START]\n{text}\n[WORKER_THOUGHTS_END]"


class CurriculumScheduler:
    """CUR-01, CUR-02: Support for Level 3 (Adversarial) escalation."""

    @staticmethod
    def get_level(training_step: int) -> int:
        if training_step < 150:
            return 1
        if training_step < 300:
            return 2
        return 3


class ScenarioLoader:
    """SCN-10: Scenario loader with support for Level 3 Adversarial generation."""

    def __init__(self, scenario_dir: Optional[str] = None, seed: int = 42):
        self._rng = random.Random(seed)
        self.seed = seed
        self.scenarios_by_level: Dict[int, list] = {}
        self.train_scenarios: list = []
        self.eval_scenarios: list = []
        self._step_counter = 0  # Layer-2: circular buffer counter

        if scenario_dir and os.path.exists(scenario_dir):
            for level in [1, 2]:
                level_path = os.path.join(scenario_dir, f"level_{level}")
                if os.path.exists(level_path):
                    scenarios = []
                    for fname in os.listdir(level_path):
                        if fname.endswith(".json"):
                            fpath = os.path.join(level_path, fname)
                            with open(fpath, "r", encoding="utf-8") as f:
                                scenarios.append(json.load(f))
                    self.scenarios_by_level[level] = scenarios

            # 80/20 train/eval partition
            all_scenarios = (
                self.scenarios_by_level.get(1, [])
                + self.scenarios_by_level.get(2, [])
            )
            self._rng.shuffle(all_scenarios)
            split = int(len(all_scenarios) * 0.8)
            self.train_scenarios = all_scenarios[:split]
            self.eval_scenarios = all_scenarios[split:]

    def sample(self, level: int, mode: str = "train") -> Dict[str, Any]:
        """Layer-2 fix: circular buffer modulo prevents IndexError on exhaustion.
        For level 3, use AdversarialGenerator on Level 2 scenarios.
        """
        pool = self.train_scenarios if mode == "train" else self.eval_scenarios
        if not pool:
            raise ValueError(
                f"No scenarios found for mode='{mode}'. Check scenario_dir."
            )
            
        # Circular modulo — never raises IndexError
        idx = self._step_counter % len(pool)
        self._step_counter += 1
        scenario = pool[idx]
        
        if level >= 3:
            return AdversarialGenerator.generate(scenario, seed=self.seed + self._step_counter)
            
        return scenario

    def reset_counter(self) -> None:
        """Reset circular counter for a new training run."""
        self._step_counter = 0
