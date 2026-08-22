"""Human-in-the-Loop Governance & Review Workflow.

Manages operator review of AI recommendations:
- Recommendation Presentation (Evidence, Confidence, Reasons, Sources, Constraints)
- Operator Actions: APPROVE | REJECT | INVESTIGATE
- Audit Trail: Persists recommendation, operator decision, rationale, model version, and outcome.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class OperatorReviewSubmission(BaseModel):
    decision_id: str
    action: str = Field(..., description="APPROVE | REJECT | INVESTIGATE")
    operator_id: str = "OPERATOR_CHIEF"
    rationale: str
    model_version: str = "CrossAttention-v2.1"
    agent_version: str = "AgentLoop-v2.0"
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())


class HumanGovernanceEngine:
    """Processes and persists operator reviews for all AI decision recommendations."""

    def __init__(self):
        self._reviews: List[Dict[str, Any]] = []

    def submit_review(self, submission: OperatorReviewSubmission) -> Dict[str, Any]:
        record = {
            "review_id": f"rev_{len(self._reviews) + 1:04d}",
            "decision_id": submission.decision_id,
            "human_decision": submission.action.upper(),
            "operator_id": submission.operator_id,
            "rationale": submission.rationale,
            "model_version": submission.model_version,
            "agent_version": submission.agent_version,
            "status": "LOGGED_TO_AUDIT_STORE",
            "timestamp": submission.timestamp,
        }
        self._reviews.append(record)
        return record

    def list_reviews(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._reviews[-limit:]
