"""Multivariate Isolation Forest Anomaly Detection Model.

Unsupervised anomaly detector for operational telemetry health scoring,
sensor degradation alerting, and risk penalty injection into ML/CP-SAT decision pipelines.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestAnomalyDetector:
    """Multivariate Isolation Forest detector for continuous telemetry streams."""

    SENSOR_FEATURE_NAMES = [
        "battery_soc",
        "battery_temp_c",
        "bus_voltage_v",
        "comm_latency_ms",
        "link_snr_db",
        "memory_util_pct",
        "power_draw_w",
    ]

    def __init__(self, n_estimators: int = 150, contamination: float = 0.05, threshold: float = 0.0):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.threshold = threshold
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=42,
        )
        self.is_fitted = False
        self._bootstrap_nominal_model()

    def _bootstrap_nominal_model(self):
        """Initializes with nominal baseline telemetry distributions."""
        np.random.seed(42)
        n_samples = 800
        nominal_soc = np.random.uniform(0.6, 0.95, n_samples)
        nominal_temp = np.random.normal(22.0, 3.0, n_samples)
        nominal_volt = np.random.normal(28.0, 0.4, n_samples)
        nominal_latency = np.random.normal(45.0, 6.0, n_samples)
        nominal_snr = np.random.normal(18.0, 1.5, n_samples)
        nominal_mem = np.random.uniform(20.0, 50.0, n_samples)
        nominal_power = np.random.normal(35.0, 4.0, n_samples)

        X_nominal = np.column_stack([
            nominal_soc,
            nominal_temp,
            nominal_volt,
            nominal_latency,
            nominal_snr,
            nominal_mem,
            nominal_power,
        ])
        self.model.fit(X_nominal)
        self.is_fitted = True

    def score_telemetry(self, telemetry_vector: np.ndarray) -> Dict[str, Any]:
        """
        Computes anomaly score and classification.
        decision_function < threshold (0.0) indicates operational anomaly.
        """
        X = np.asarray(telemetry_vector, dtype=np.float64).reshape(1, -1)
        raw_decision = float(self.model.decision_function(X)[0])
        # Logistic anomaly score in [0.0, 1.0] where > 0.5 is anomaly
        anomaly_score = float(1.0 / (1.0 + np.exp(raw_decision * 10.0)))
        is_anomaly = bool(raw_decision < self.threshold)

        severity = "NOMINAL"
        if anomaly_score > 0.80:
            severity = "CRITICAL"
        elif anomaly_score > 0.65:
            severity = "HIGH"
        elif is_anomaly:
            severity = "MEDIUM"

        return {
            "raw_decision": round(raw_decision, 4),
            "anomaly_score": round(anomaly_score, 4),
            "is_anomaly": is_anomaly,
            "severity": severity,
            "threshold": self.threshold,
            "risk_penalty": self.compute_risk_penalty(raw_decision if is_anomaly else 0.0),
        }

    @staticmethod
    def compute_risk_penalty(anomaly_margin: float, lambda_penalty: float = 2.5) -> float:
        """
        Calculates multiplicative or additive penalty to adjust candidate win probabilities.
        """
        if anomaly_margin >= 0.0:
            return 0.0
        return float(round(min(1.0, abs(anomaly_margin) * lambda_penalty), 3))
