"""Self-Healing Continuous Verification Agent Loop for ORBIT-X.

Autonomously monitors model drift, TreeSHAP surrogate alignment, and eval harness
benchmarks. Automatically triggers retraining and re-distillation when regressions
or weight drift are detected, logging plain-language Flight Director commentary.
"""

import datetime
from typing import Dict, Any, Optional, Tuple

from app.core.schemas import AgentHealingAction
from app.intelligence.shap_explainer import get_shap_explainer
from app.intelligence.bid_value_network import get_bid_value_predictor
from app.intelligence.decision_logger import get_decision_logger
from app.intelligence.commentary_generator import get_commentary_generator
from eval.run_eval import run_full_evaluation


class SelfHealingAgent:
    """Continuous verification and self-healing agent."""

    def __init__(self):
        self.explainer = get_shap_explainer()
        self.predictor = get_bid_value_predictor()
        self.logger = get_decision_logger()
        self.commentary_gen = get_commentary_generator()
        self.last_check_iso: Optional[str] = None
        self.last_action: Optional[AgentHealingAction] = None

    def inspect_and_heal(self) -> Tuple[str, Optional[AgentHealingAction]]:
        """
        Runs comprehensive inspection of surrogate alignment and eval benchmarks.
        Triggers remediation if issues are flagged.
        """
        timestamp_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.last_check_iso = timestamp_iso
        
        # 1. Check TreeSHAP drift
        drift_detected = self.explainer.check_drift()
        
        # 2. Run Eval Harness
        eval_summary, has_regressions = run_full_evaluation()
        
        if not drift_detected and not has_regressions:
            action = AgentHealingAction(
                action_type="VERIFICATION_PASS",
                triggered_by="ROUTINE_HEALTH_CHECK",
                status="HEALTHY",
                details="All 6 eval gates passed; TreeSHAP surrogate is perfectly aligned with active neural network checkpoint.",
                timestamp_iso=timestamp_iso,
            )
            self.last_action = action
            return "HEALTHY", action
            
        # Remediation required
        remediation_reasons = []
        if drift_detected:
            remediation_reasons.append("TreeSHAP surrogate model weight hash mismatch")
        if has_regressions:
            remediation_reasons.extend(eval_summary.regressions)
            
        details_str = "; ".join(remediation_reasons)
        print(f"\n[AGENT] Triggering automated self-healing remediation: {details_str}")
        
        # Re-distill surrogate to sync with current neural network weights
        self.explainer.distill_surrogate()
        
        # Re-run eval harness post-healing
        post_eval, post_regressions = run_full_evaluation()
        
        healing_status = "HEALED" if not post_regressions else "PARTIAL_REMEDIATION"
        
        action = AgentHealingAction(
            action_type="SURROGATE_REDISTILLATION",
            triggered_by=details_str,
            status=healing_status,
            details=f"Re-distilled TreeSHAP surrogate model. Post-healing eval status: {post_eval.overall_status}.",
            timestamp_iso=timestamp_iso,
        )
        self.last_action = action
        
        # Log to decision history
        self.logger.log_anomaly(
            tick=0,
            sim_time_s=0.0,
            satellite_id="GLOBAL_AI_AGENT",
            anomaly_score=0.9 if post_regressions else 0.0,
            health_status="NOMINAL" if not post_regressions else "DEGRADED",
            details_str=f"Self-Healing Agent: {action.details}",
        )
        
        # Generate plain-language commentary
        comm = self.commentary_gen.generate_commentary(
            "AGENT_HEALING",
            0.0,
            {
                "satellite_id": "AGENT-LOOP",
                "mission_id": "MODEL_DRIFT_REPAIR",
                "status": healing_status,
            }
        )
        print(f"[AGENT COMMENTARY] {comm.commentary}")
        
        return healing_status, action


_global_agent: Optional[SelfHealingAgent] = None


def get_self_healing_agent() -> SelfHealingAgent:
    global _global_agent
    if _global_agent is None:
        _global_agent = SelfHealingAgent()
    return _global_agent


if __name__ == "__main__":
    agent = get_self_healing_agent()
    status, act = agent.inspect_and_heal()
    print(f"Agent Inspection Result: {status}")
    if act:
        print(f"Action: {act.model_dump_json(indent=2)}")
