"""ORBIT-X Decision Intelligence Subsystem.

Combines neural candidate ranking with Google OR-Tools CP-SAT deterministic
constraint optimization, human-in-the-loop governance, and continuous feedback alignment.
"""

from decision.human_review.governance import HumanGovernanceEngine, OperatorReviewSubmission
from decision.feedback.loop import FeedbackLoopManager

# Backward-compatible re-exports
from backend.app.intelligence.optimizer import (
    ConstellationOptimizer,
    get_optimizer,
)
from backend.app.intelligence.decision_logger import (
    DecisionLogger,
    LoggedDecisionEvent,
    get_decision_logger,
)
from backend.app.core.schemas import ScheduleDecision

# Compatibility aliases
OptimizationResult = ScheduleDecision
DecisionAuditLogger = DecisionLogger
DecisionRecord = LoggedDecisionEvent

__all__ = [
    "HumanGovernanceEngine",
    "OperatorReviewSubmission",
    "FeedbackLoopManager",
    "ConstellationOptimizer",
    "ScheduleDecision",
    "OptimizationResult",
    "get_optimizer",
    "DecisionLogger",
    "LoggedDecisionEvent",
    "DecisionAuditLogger",
    "DecisionRecord",
    "get_decision_logger",
]
