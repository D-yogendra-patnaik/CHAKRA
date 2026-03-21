from typing import List
from dataclasses import dataclass, field

@dataclass
class GuardrailResult:
    risk_score: float = 0.0
    labels: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    action: str = "allow"
    explanation: str = "Passed all checks"
    sanitized_prompt: str = None
    # Pipeline trace for explainability (Pillar 4: LLM Audit API)
    pipeline_trace: List[dict] = field(default_factory=list)

    def merge(self, other: 'GuardrailResult', stage_name: str = "unknown"):
        prev_score = self.risk_score
        prev_labels = list(self.labels)

        self.risk_score = max(self.risk_score, other.risk_score)
        self.labels.extend([l for l in other.labels if l not in self.labels])
        self.reasons.extend(other.reasons)

        # Record trace entry for this stage
        new_labels = [l for l in other.labels if l not in prev_labels]
        self.pipeline_trace.append({
            "stage": stage_name,
            "risk_contributed": round(other.risk_score, 3),
            "labels_added": new_labels,
            "reason": "; ".join(other.reasons) if other.reasons else "No issues detected"
        })

from src.api.models import FilterRequest
from src.engine.heuristics import evaluate_heuristics
from src.engine.ml_classifier import evaluate_ml
from src.engine.vector_search import evaluate_vector
from src.engine.policy import apply_policy

async def evaluate_prompt(request: FilterRequest) -> GuardrailResult:
    final_result = GuardrailResult()
    
    # 1. Heuristics (Regex, Keywords)
    h_result = await evaluate_heuristics(request.prompt)
    final_result.merge(h_result, stage_name="Heuristic Analysis")
    
    # 2. ML Classifier
    ml_result = await evaluate_ml(request.prompt)
    final_result.merge(ml_result, stage_name="ML Classifier")
    
    # 3. Vector Search (FAISS)
    v_result = await evaluate_vector(request.prompt)
    final_result.merge(v_result, stage_name="Vector Similarity Search")
    
    # 4. Apply Policy based on Tenant Config
    final_result = await apply_policy(request.tenant_id, final_result)
    
    return final_result
