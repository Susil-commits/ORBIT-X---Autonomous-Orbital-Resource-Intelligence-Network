"""Tests for Spacecraft Health AI (Isolation Forest)."""

from app.core.schemas import TelemetryFrame, HealthStatus
from app.intelligence.health_ai import get_health_ai


def test_nominal_telemetry():
    health_ai = get_health_ai()
    nominal_frame = TelemetryFrame(
        timestamp_s=100.0,
        bus_voltage_v=28.1,
        solar_current_a=6.2,
        battery_temp_c=20.0,
        payload_temp_c=22.0,
        reaction_wheel_jitter_dps=0.02,
        rf_snr_db=18.0,
        anomaly_score=0.0,
        health_status=HealthStatus.NOMINAL,
    )
    score, status = health_ai.evaluate_telemetry(nominal_frame)
    assert score < 0.55
    assert status == HealthStatus.NOMINAL


def test_severe_fault_telemetry():
    health_ai = get_health_ai()
    fault_frame = TelemetryFrame(
        timestamp_s=200.0,
        bus_voltage_v=18.5,  # Severe voltage drop
        solar_current_a=0.1,
        battery_temp_c=65.0,  # Thermal runaway
        payload_temp_c=58.0,
        reaction_wheel_jitter_dps=0.85,  # Severe jitter
        rf_snr_db=2.0,  # Loss of signal
        anomaly_score=0.0,
        health_status=HealthStatus.NOMINAL,
    )
    score, status = health_ai.evaluate_telemetry(fault_frame)
    assert score > 0.70
    assert status in [HealthStatus.DEGRADED, HealthStatus.CRITICAL_FAULT]


def test_synthetic_fault_evaluation_metrics():
    """Validates Precision, Recall, F1 and False Alarm Rate on multi-fault space dataset."""
    health_ai = get_health_ai()
    metrics = health_ai.evaluate_synthetic_faults(num_nominal=500, num_anomalies_per_type=25)
    
    assert metrics["precision"] > 0.70
    assert metrics["recall"] > 0.75
    assert metrics["f1_score"] > 0.70
    assert metrics["false_alarm_rate_pct"] < 10.0
    assert "THERMAL_RUNAWAY" in metrics["per_fault_recall_pct"]
    assert "VOLTAGE_BROWNOUT" in metrics["per_fault_recall_pct"]

