"""Decision Audit Logging and Traceability."""

from backend.app.intelligence.decision_logger import DecisionLogger, LoggedDecisionEvent, get_decision_logger

# Compatibility alias
DecisionAuditLogger = DecisionLogger
DecisionRecord = LoggedDecisionEvent

__all__ = [
    "DecisionLogger",
    "LoggedDecisionEvent",
    "DecisionAuditLogger",
    "DecisionRecord",
    "get_decision_logger",
]
