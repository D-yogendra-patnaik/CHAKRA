from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ============================================================
# PILLAR 3: Ethics Layer Plugin — Filter API Models
# ============================================================
class FilterContext(BaseModel):
    role: Optional[str] = None
    locale: Optional[str] = None

class FilterRequest(BaseModel):
    tenant_id: str
    session_id: str
    prompt: str
    context: Optional[FilterContext] = None

class FilterResponse(BaseModel):
    action: str = Field(..., description="allow | warn | block | sanitize")
    risk_score: float
    labels: List[str]
    explanation: str
    sanitized_prompt: Optional[str] = None
    pipeline_trace: Optional[List[Dict[str, Any]]] = Field(
        None, description="Step-by-step trace of each guardrail stage's decision"
    )

# ============================================================
# PILLAR 1: AI Red Team Simulator Models
# ============================================================
class RedTeamRunRequest(BaseModel):
    suite_name: str
    tenant_id: str
    prompts: Optional[List[str]] = None
    categories: Optional[List[str]] = Field(
        None, description="Filter by attack category: injection, jailbreak, pii, benign, social_engineering"
    )

class RedTeamPromptResult(BaseModel):
    prompt: str
    category: str
    action: str
    risk_score: float
    labels: List[str]
    explanation: str

class RedTeamRunResponse(BaseModel):
    run_id: str
    status: str
    results_summary: Dict[str, Any]
    prompt_results: Optional[List[RedTeamPromptResult]] = None

# ============================================================
# PILLAR 2: Trustworthiness Scorecard Models
# ============================================================
class TrustworthinessDimension(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=10, description="Score from 0 (worst) to 10 (best)")
    detail: str

class ScorecardResponse(BaseModel):
    tenant_id: str
    window: str
    block_rate: float
    warn_rate: float
    action_counts: Dict[str, int]
    top_labels: List[str]
    trust_score: float
    dimensions: Optional[List[TrustworthinessDimension]] = Field(
        None, description="Breakdown by safety, bias, compliance"
    )

# ============================================================
# PILLAR 4: LLM Audit API Models
# ============================================================
class AuditDecisionTrace(BaseModel):
    stage: str
    risk_contributed: float
    labels_added: List[str]
    reason: str

class AuditLogEntry(BaseModel):
    id: str
    tenant_id: str
    session_id: str
    timestamp: str
    action: str
    risk_score: float
    labels: List[str]
    prompt_snippet: Optional[str] = None
    explanation: Optional[str] = None
    decision_trace: Optional[List[AuditDecisionTrace]] = None
    latency_ms: Optional[float] = None

class AuditLogsResponse(BaseModel):
    logs: List[AuditLogEntry]
    total: int
    page: int
