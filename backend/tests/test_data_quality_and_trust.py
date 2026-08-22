"""Tests for Data Quality Agent, Ask ORBIT-X Trust Layer, and Human-in-the-Loop Feedback."""

import pytest
from app.core.schemas import TelemetryFrame, HealthStatus, HumanFeedbackRequest
from app.intelligence.data_quality_agent import get_data_quality_agent
from app.intelligence.trust_layer import get_trust_layer_engine


def test_data_quality_agent_nominal_and_drift():
    """Validates data quality audits on nominal and drifted telemetry frames."""
    agent = get_data_quality_agent()

    # Nominal frame
    nominal_frame = TelemetryFrame(
        timestamp_s=10.0,
        bus_voltage_v=28.2,
        solar_current_a=5.5,
        battery_temp_c=20.0,
        payload_temp_c=22.0,
        reaction_wheel_jitter_dps=0.02,
        rf_snr_db=18.5,
        anomaly_score=0.1,
        health_status=HealthStatus.NOMINAL,
    )

    report = agent.audit_telemetry_stream([nominal_frame])
    assert report.is_nominal is True
    assert report.overall_quality_score >= 0.95
    assert len(report.alerts) == 0

    # Corrupted frame with over-voltage
    corrupt_frame = TelemetryFrame(
        timestamp_s=15.0,
        bus_voltage_v=42.0,  # Extreme over-voltage
        solar_current_a=5.5,
        battery_temp_c=85.0,  # Extreme thermal spike
        payload_temp_c=22.0,
        reaction_wheel_jitter_dps=1.5,
        rf_snr_db=18.5,
        anomaly_score=0.9,
        health_status=HealthStatus.CRITICAL_FAULT,
    )
    drift_report = agent.audit_telemetry_stream([corrupt_frame])
    assert drift_report.is_nominal is False
    assert len(drift_report.alerts) >= 2


def test_ask_orbitx_trust_layer_response():
    """Validates that Ask ORBIT-X produces grounded responses with evidence, confidence, and citations."""
    trust_engine = get_trust_layer_engine()
    res = trust_engine.ask_orbitx("Why was satellite 3 assigned to Hurricane Alpha?")

    assert res.grounded is True
    assert 0.0 <= res.confidence_score <= 1.0
    assert res.confidence_level in ["HIGH", "MEDIUM", "LOW"]
    assert len(res.evidence) >= 3
    assert len(res.tools_used) >= 2
    assert res.lineage_summary is not None


def test_human_feedback_recording_and_retrieval():
    """Validates recording of human-in-the-loop review actions."""
    trust_engine = get_trust_layer_engine()
    req = HumanFeedbackRequest(
        decision_record_id="REC-TEST-001",
        mission_id="M-TEST-100",
        feedback_type="APPROVE",
        operator_notes="Verified battery margin > 30% and sunlit imaging window.",
    )
    resp = trust_engine.record_feedback(req)
    assert resp.status == "RECORDED"
    assert resp.feedback_id.startswith("FB-")

    history = trust_engine.get_all_feedback()
    assert any(f["decision_record_id"] == "REC-TEST-001" for f in history)
