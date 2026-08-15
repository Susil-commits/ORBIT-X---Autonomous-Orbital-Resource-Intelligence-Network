"""Spacecraft Telemetry Anomaly Detection using Isolation Forest."""

from typing import List, Tuple, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest

from app.core.schemas import TelemetryFrame, HealthStatus


class SpacecraftHealthAI:
    def __init__(self, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=random_state,
        )
        self._is_trained = False
        self._train_baseline()

    def _train_baseline(self, num_samples: int = 2000):
        """Trains the Isolation Forest on synthetic normal operational telemetry."""
        np.random.seed(42)
        
        # Nominal telemetry distributions
        v_bus = np.random.normal(28.2, 0.4, num_samples)
        i_solar = np.random.uniform(0.0, 7.5, num_samples)
        t_batt = np.random.normal(20.0, 3.0, num_samples)
        t_payload = np.random.normal(23.0, 4.0, num_samples)
        jitter = np.random.exponential(0.02, num_samples) + 0.01
        rf_snr = np.random.normal(18.0, 2.0, num_samples)
        
        X_train = np.column_stack([
            v_bus,
            i_solar,
            t_batt,
            t_payload,
            jitter,
            rf_snr,
        ])
        
        self.model.fit(X_train)
        self._is_trained = True

    def extract_features(self, frame: TelemetryFrame) -> np.ndarray:
        """Converts a TelemetryFrame into a 2D numpy feature array for inference."""
        return np.array([[
            frame.bus_voltage_v,
            frame.solar_current_a,
            frame.battery_temp_c,
            frame.payload_temp_c,
            frame.reaction_wheel_jitter_dps,
            frame.rf_snr_db,
        ]], dtype=float)

    def evaluate_telemetry(self, frame: TelemetryFrame) -> Tuple[float, HealthStatus]:
        """
        Evaluates incoming telemetry frame.
        Returns: (anomaly_score [0.0, 1.0], HealthStatus)
        """
        if not self._is_trained:
            self._train_baseline()
            
        features = self.extract_features(frame)
        
        # Isolation Forest decision_function returns negative values for anomalies
        raw_score = self.model.decision_function(features)[0]
        
        # Map raw decision function to [0.0, 1.0] anomaly score (higher = more anomalous)
        # Normal observations typically have raw_score in range [0.05, 0.25]
        # Anomalies have raw_score < 0
        anomaly_score = 1.0 / (1.0 + np.exp(raw_score * 12.0))
        anomaly_score = float(np.clip(anomaly_score, 0.0, 1.0))
        
        # Determine health status
        if anomaly_score > 0.78:
            status = HealthStatus.CRITICAL_FAULT
        elif anomaly_score > 0.52:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.NOMINAL
            
        return anomaly_score, status


# Global singleton instance
_HEALTH_AI_INSTANCE: SpacecraftHealthAI = None


def get_health_ai() -> SpacecraftHealthAI:
    global _HEALTH_AI_INSTANCE
    if _HEALTH_AI_INSTANCE is None:
        _HEALTH_AI_INSTANCE = SpacecraftHealthAI()
    return _HEALTH_AI_INSTANCE
