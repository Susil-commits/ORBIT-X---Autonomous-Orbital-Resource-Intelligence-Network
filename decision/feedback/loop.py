"""Continuous Feedback Loop Dataset & AI Calibration.

Consolidates approved, rejected, and investigated recommendations alongside
observed ground-truth outcomes to evaluate and calibrate retrieval and ML ranking models.
"""

from typing import List, Dict, Any, Optional


class FeedbackLoopManager:
    """Manages the continuous feedback dataset for model & agent improvement."""

    def __init__(self):
        self._feedback_dataset: List[Dict[str, Any]] = []

    def record_feedback(
        self,
        decision_id: str,
        human_decision: str,
        rationale: str,
        model_version: str = "CrossAttention-v2.1",
        actual_outcome: str = "SUCCESS_NOMINAL",
    ) -> Dict[str, Any]:
        entry = {
            "feedback_id": f"fbk_{len(self._feedback_dataset) + 1:04d}",
            "decision_id": decision_id,
            "human_decision": human_decision,
            "rationale": rationale,
            "model_version": model_version,
            "actual_outcome": actual_outcome,
            "alignment_score": 1.0 if human_decision == "APPROVE" and "SUCCESS" in actual_outcome else 0.5,
        }
        self._feedback_dataset.append(entry)
        return entry

    def get_dataset_statistics(self) -> Dict[str, Any]:
        total = len(self._feedback_dataset)
        if total == 0:
            return {"total_feedback_records": 0, "approval_rate": 0.0, "average_alignment": 1.0}

        approvals = sum(1 for f in self._feedback_dataset if f["human_decision"] == "APPROVE")
        avg_align = sum(f["alignment_score"] for f in self._feedback_dataset) / total

        return {
            "total_feedback_records": total,
            "approval_rate": round(approvals / total, 3),
            "average_alignment": round(avg_align, 3),
        }
