"""Decision Constraint Optimization Subsystem (Google OR-Tools CP-SAT)."""

from backend.app.intelligence.optimizer import ConstellationOptimizer, get_optimizer
from backend.app.core.schemas import ScheduleDecision

# Compatibility alias
CPSATOptimizer = ConstellationOptimizer
get_cpsat_optimizer = get_optimizer

__all__ = [
    "ConstellationOptimizer",
    "get_optimizer",
    "CPSATOptimizer",
    "get_cpsat_optimizer",
    "ScheduleDecision",
]
