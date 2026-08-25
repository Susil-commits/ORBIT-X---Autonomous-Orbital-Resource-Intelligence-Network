"""Unit & Integration Tests for Calibrated Decision & Refusal Framework.

Tests:
1. Good Context -> Agent Reasons -> Decision (ASSIGN) matching exact requested schema:
   {
     "prediction": "satellite_07",
     "confidence": 0.91,
     "context_quality": 0.97,
     "evidence_count": 4,
     "constraint_status": "PASS",
     "decision": "ASSIGN"
   }
2. Bad / Stale Context -> Agent Refuses -> Requests Fresh Downlink Evidence (REFUSE).
3. Deprecated Dataset -> Agent Refuses -> Fallback to Verified Prior (REFUSE).
4. Missing Lineage Provenance -> Agent Refuses -> Re-sign Provenance DAG (REFUSE).
5. Nonexistent Entity -> Anti-Hallucination Gate -> Agent Refuses (REFUSE).
6. Physical Battery Floor Constraint Violation -> Agent Refuses (REFUSE).
"""

import pytest
from app.intelligence.calibrated_decision_engine import (
    CalibratedDecisionEngine,
    CalibratedDecision,
    DecisionAction,
    ConstraintStatus,
    RefusalCategory,
    get_calibrated_decision_engine,
)


def test_good_context_assign_decision():
    engine = get_calibrated_decision_engine()
    decision = engine.evaluate_decision(
        mission_id="M-204",
        mission_requirements={"priority": 4.0, "deadline_slack_s": 1500.0},
        candidate_satellites=[
            {"id": "satellite_07", "battery_soc": 0.88, "battery_temp_c": 22.0, "max_elevation_deg": 72.0},
            {"id": "satellite_02", "battery_soc": 0.65, "battery_temp_c": 24.0, "max_elevation_deg": 48.0},
            {"id": "satellite_05", "battery_soc": 0.52, "battery_temp_c": 26.0, "max_elevation_deg": 35.0},
        ],
        context_metadata={
            "telemetry_age_s": 4.2,
            "dataset_status": "VERIFIED",
            "lineage_hash": "a8f4c910b3e72d1f90e6a1bc5d2903fe",
            "schema_verified": True,
        },
    )

    summary = decision.to_summary_dict()
    assert summary["prediction"] == "satellite_07"
    assert summary["confidence"] == 0.91
    assert summary["context_quality"] == 0.97
    assert summary["evidence_count"] == 4
    assert summary["constraint_status"] == "PASS"
    assert summary["decision"] == "ASSIGN"
    assert decision.refusal_reason is None
    assert decision.refusal_category == RefusalCategory.NONE


def test_stale_telemetry_refusal():
    engine = get_calibrated_decision_engine()
    decision = engine.evaluate_decision(
        mission_id="M-205",
        mission_requirements={"priority": 3.0},
        candidate_satellites=[{"id": "satellite_03", "battery_soc": 0.80}],
        context_metadata={
            "telemetry_age_s": 2400.0,  # 40 minutes old (SLA violated)
            "dataset_status": "VERIFIED",
            "lineage_hash": "a8f4c910b3e72d1f90e6a1bc5d2903fe",
        },
    )

    assert decision.decision == DecisionAction.REFUSE
    assert decision.constraint_status == ConstraintStatus.FAIL
    assert decision.refusal_category == RefusalCategory.STALE_TELEMETRY
    assert "acquire_fresh_downlink_telemetry_pass" in decision.requested_actions


def test_deprecated_dataset_refusal():
    engine = get_calibrated_decision_engine()
    decision = engine.evaluate_decision(
        mission_id="M-206",
        mission_requirements={"priority": 3.0},
        candidate_satellites=[{"id": "satellite_01", "battery_soc": 0.90}],
        context_metadata={
            "telemetry_age_s": 5.0,
            "dataset_status": "DEPRECATED",
            "dataset_name": "legacy_v1_telemetry_csv",
            "lineage_hash": "a8f4c910b3e72d1f90e6a1bc5d2903fe",
        },
    )

    assert decision.decision == DecisionAction.REFUSE
    assert decision.refusal_category == RefusalCategory.DEPRECATED_DATASET
    assert "upgrade_to_verified_dataset_v2" in decision.requested_actions


def test_missing_lineage_refusal():
    engine = get_calibrated_decision_engine()
    decision = engine.evaluate_decision(
        mission_id="M-207",
        mission_requirements={"priority": 3.0},
        candidate_satellites=[{"id": "satellite_01", "battery_soc": 0.90}],
        context_metadata={
            "telemetry_age_s": 5.0,
            "dataset_status": "VERIFIED",
            "lineage_hash": "",  # Missing lineage
        },
    )

    assert decision.decision == DecisionAction.REFUSE
    assert decision.refusal_category == RefusalCategory.MISSING_LINEAGE


def test_nonexistent_satellite_refusal():
    engine = get_calibrated_decision_engine()
    decision = engine.evaluate_decision(
        mission_id="M-208",
        mission_requirements={"priority": 3.0},
        candidate_satellites=[],
        context_metadata={"is_unknown_entity": True},
    )

    assert decision.decision == DecisionAction.REFUSE
    assert decision.refusal_category == RefusalCategory.NONEXISTENT_ENTITY


def test_battery_floor_constraint_violation_refusal():
    engine = get_calibrated_decision_engine()
    decision = engine.evaluate_decision(
        mission_id="M-209",
        mission_requirements={"priority": 5.0},
        candidate_satellites=[
            {"id": "satellite_04", "battery_soc": 0.12, "battery_temp_c": 22.0}  # SoC 12% < 20% floor
        ],
        context_metadata={
            "telemetry_age_s": 3.0,
            "dataset_status": "VERIFIED",
            "lineage_hash": "a8f4c910b3e72d1f90e6a1bc5d2903fe",
        },
    )

    assert decision.decision == DecisionAction.REFUSE
    assert decision.constraint_status == ConstraintStatus.FAIL
    assert decision.refusal_category == RefusalCategory.HARD_CONSTRAINT_VIOLATION
