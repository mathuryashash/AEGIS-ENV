from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict

class ScenarioTemplate(BaseModel):
    """Template for ground-truth offline generated training scenarios."""
    scenario_id: str
    level: int
    
    # Pre-calculated simulation traces avoiding runtime groq
    worker_cot_trace: str
    worker_output: str
    db_query_trace: List[str]
    api_call_log: List[dict]
    
    # Ground truth RL constraints
    decision: str  # ALLOW, BLOCK, ESCALATE
    violation_type: str
    applicable_rules: List[str]
    suspicious_apis_caught: bool = False
    earliest_detectable_turn: Optional[int] = None

    model_config = ConfigDict(extra='forbid')
