from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Enums ---

class MediaType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"

class Decision(str, Enum):
    SHIP = "ship"
    ITERATE = "iterate"
    ROLLBACK = "rollback"

class ExperimentStatus(str, Enum):
    RUNNING = "running"
    FAILED = "failed"
    AWAITING_DECISION = "awaiting_decision"
    COMPLETE = "complete"

# --- Input Models ---

class ExperimentInput(BaseModel):
    media_id: str
    media_type: MediaType
    model_list: List[str] = Field(..., max_items=3, min_items=1)
    user_api_keys: Dict[str, str] # Ephemeral, not stored
    experiment_metadata: Optional[Dict[str, Any]] = None

# --- Persistence Models (Supabase) ---

class ExperimentRow(BaseModel):
    experiment_id: str
    created_at: datetime
    media_id: str
    status: ExperimentStatus
    decision: Optional[Decision] = None
    decision_reason: Optional[str] = None
    recommendation: Optional[str] = None
    recommendation_reason: Optional[str] = None

class ModelRunResult(BaseModel):
    run_id: str
    experiment_id: str
    model_name: str
    raw_output: str # URL or content
    latency_ms: int
    cost_usd: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EvaluationScore(BaseModel):
    metric_name: str
    score: float
    reasoning: str

class EvaluationResult(BaseModel):
    eval_id: str
    run_id: str
    scores: List[EvaluationScore]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ComparisonResult(BaseModel):
    experiment_id: str
    winning_model: str
    reason: str
    tradeoffs: Optional[Any] = {} # Relaxed to Any to prevent crash
