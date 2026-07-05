"""
Core data models for AEGIS-Env.
Contains Pydantic schemas and Enums utilized across the environment.
"""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, ConfigDict


class WorkerRole(str, Enum):
    """Worker role types in the enterprise fleet."""

    SEC_OPS = "sec-ops"  # Security operations - monitors access, permissions
    DATA_ENG = "data-eng"  # Data engineering - SQL, ETL, pipelines
    API_DEV = "api-dev"  # API development - REST/GraphQL endpoints
    CODE_REVIEWER = "code-reviewer"  # Code review - security, quality
    DESIGNER = "designer"  # UI/UX design - design tokens, accessibility
    PLANNER = "planner"  # Project planning - task decomposition
    CUSTOMER_SUPPORT = "customer-support"  # Customer facing - PII exposure risk
    ADMIN = "admin"  # Admin operations - system commands
    GENERAL_DEV = "general-dev"  # General development - default role


class Decision(str, Enum):
    """Actions the oversight agent can take."""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class ViolationType(str, Enum):
    """Categorized policy violations."""

    NONE = "none"
    PII_LEAK = "pii_leak"
    PROMPT_INJECTION = "prompt_injection"
    HALLUCINATED_FEATURE = "hallucinated_feature"
    UNSAFE_CODE = "unsafe_code"
    DATA_EXFILTRATION = "data_exfiltration_intent"
    AUTHORITY_ESCALATION = "authority_escalation"
    COMPOUND_VIOLATION = "compound_violation"
    OVERSEER_MANIPULATION = "overseer_manipulation"


class AEGISAction(BaseModel):
    """The action schema output by the oversight agent."""

    decision: Decision
    confidence: float
    violation_type: ViolationType
    policy_rule_cited: Optional[str] = None
    evidence_quote: Optional[str] = None
    explanation: str
    remediation: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class AEGISObservation(BaseModel):
    """The observation schema provided to the oversight agent."""

    # BUG-1 / Layer-1 FIX: All fields have defaults to prevent 422 crashes
    # on partial observations sent by the training loop.
    worker_id: str = "WORKER-1"
    worker_role: WorkerRole = WorkerRole.GENERAL_DEV
    turn_number: int = 1
    worker_cot_trace: str = ""
    worker_output: str = ""
    policy_ruleset: List[dict] = []
    state_buffer: List[str] = []
    scenario_type: str = "SINGLE_TURN"
    turns_remaining: int = 15
    api_call_log: List[dict] = []
    db_query_trace: List[str] = []
    memory_context: str = ""
    success: bool = False

    model_config = ConfigDict(extra="forbid")


class AEGISState(BaseModel):
    """The internal state representation of the environment episode."""

    episode_id: str
    scenario_id: str
    curriculum_level: int
    step_count: int = 0
    ground_truth: dict
    world_db_state: dict
    memory_ledger_size: int = 0
    total_reward: float = 0.0
    earliest_detectable_turn: Optional[int] = None
    detection_turn: Optional[int] = None

    model_config = ConfigDict(extra="forbid")
