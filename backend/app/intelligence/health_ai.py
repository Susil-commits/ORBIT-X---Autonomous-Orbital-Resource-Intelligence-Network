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


    def evaluate_synthetic_faults(
        self,
        num_nominal: int = 1000,
        num_anomalies_per_type: int = 40,
        threshold: float = 0.52,
    ) -> Dict[str, Any]:
        """
        Generates labeled synthetic faults across 5 distinct space anomaly classes
        and computes comprehensive evaluation metrics: Precision, Recall, F1, False Alarm Rate.
        """
        if not self._is_trained:
            self._train_baseline()

        np.random.seed(101)
        # 1. Nominal Samples (Label 0)
        v_bus = np.random.normal(28.2, 0.4, num_nominal)
        i_solar = np.random.uniform(0.0, 7.5, num_nominal)
        t_batt = np.random.normal(20.0, 3.0, num_nominal)
        t_payload = np.random.normal(23.0, 4.0, num_nominal)
        jitter = np.random.exponential(0.02, num_nominal) + 0.01
        rf_snr = np.random.normal(18.0, 2.0, num_nominal)

        nominal_feats = np.column_stack([v_bus, i_solar, t_batt, t_payload, jitter, rf_snr])
        labels = [0] * num_nominal
        classes = ["NOMINAL"] * num_nominal

        # 2. Anomaly Class 1: Thermal Overheat
        t_hot = np.random.normal(68.0, 5.0, num_anomalies_per_type)
        t_pay_hot = np.random.normal(72.0, 6.0, num_anomalies_per_type)
        thermal_feats = np.column_stack([
            np.random.normal(28.0, 0.4, num_anomalies_per_type),
            np.random.uniform(2.0, 6.0, num_anomalies_per_type),
            t_hot,
            t_pay_hot,
            np.random.exponential(0.03, num_anomalies_per_type) + 0.01,
            np.random.normal(18.0, 2.0, num_anomalies_per_type),
        ])
        labels.extend([1] * num_anomalies_per_type)
        classes.extend(["THERMAL_RUNAWAY"] * num_anomalies_per_type)

        # 3. Anomaly Class 2: Battery Brownout / Voltage Sag
        v_sag = np.random.normal(19.5, 1.2, num_anomalies_per_type)
        voltage_feats = np.column_stack([
            v_sag,
            np.random.uniform(0.0, 1.0, num_anomalies_per_type),
            np.random.normal(12.0, 4.0, num_anomalies_per_type),
            np.random.normal(18.0, 3.0, num_anomalies_per_type),
            np.random.exponential(0.02, num_anomalies_per_type) + 0.01,
            np.random.normal(16.0, 2.5, num_anomalies_per_type),
        ])
        labels.extend([1] * num_anomalies_per_type)
        classes.extend(["VOLTAGE_BROWNOUT"] * num_anomalies_per_type)

        # 4. Anomaly Class 3: Reaction Wheel Attitude Jitter Anomaly
        jit_spike = np.random.normal(0.45, 0.08, num_anomalies_per_type)
        jitter_feats = np.column_stack([
            np.random.normal(28.2, 0.4, num_anomalies_per_type),
            np.random.uniform(2.0, 7.0, num_anomalies_per_type),
            np.random.normal(21.0, 3.0, num_anomalies_per_type),
            np.random.normal(24.0, 4.0, num_anomalies_per_type),
            jit_spike,
            np.random.normal(17.5, 2.0, num_anomalies_per_type),
        ])
        labels.extend([1] * num_anomalies_per_type)
        classes.extend(["ATTITUDE_JITTER"] * num_anomalies_per_type)

        # 5. Anomaly Class 4: RF Link Transponder Degradation
        rf_drop = np.random.normal(4.2, 1.0, num_anomalies_per_type)
        rf_feats = np.column_stack([
            np.random.normal(28.1, 0.4, num_anomalies_per_type),
            np.random.uniform(2.0, 7.0, num_anomalies_per_type),
            np.random.normal(20.0, 3.0, num_anomalies_per_type),
            np.random.normal(22.0, 4.0, num_anomalies_per_type),
            np.random.exponential(0.02, num_anomalies_per_type) + 0.01,
            rf_drop,
        ])
        labels.extend([1] * num_anomalies_per_type)
        classes.extend(["RF_TRANSPONDER_DROP"] * num_anomalies_per_type)

        X_eval = np.vstack([nominal_feats, thermal_feats, voltage_feats, jitter_feats, rf_feats])
        raw_scores = self.model.decision_function(X_eval)
        anomaly_scores = 1.0 / (1.0 + np.exp(raw_scores * 12.0))
        preds = (anomaly_scores >= threshold).astype(int)

        y_true = np.array(labels)
        tp = int(np.sum((preds == 1) & (y_true == 1)))
        fp = int(np.sum((preds == 1) & (y_true == 0)))
        tn = int(np.sum((preds == 0) & (y_true == 0)))
        fn = int(np.sum((preds == 0) & (y_true == 1)))

        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * (precision * recall) / max(1e-6, precision + recall)
        false_alarm_rate = fp / max(1, fp + tn)

        # Per-class recall breakdown
        per_class_recall = {}
        for c in set(classes):
            if c == "NOMINAL":
                continue
            mask = np.array([cl == c for cl in classes])
            rec_c = float(np.sum(preds[mask] == 1) / np.sum(mask))
            per_class_recall[c] = round(rec_c * 100.0, 1)

        return {
            "total_test_samples": len(y_true),
            "nominal_samples": num_nominal,
            "anomaly_samples": int(np.sum(y_true == 1)),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "false_alarm_rate_pct": round(float(false_alarm_rate * 100.0), 2),
            "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
            "per_fault_recall_pct": per_class_recall,
        }


# Global singleton instance
_HEALTH_AI_INSTANCE: SpacecraftHealthAI = None


def get_health_ai() -> SpacecraftHealthAI:
    global _HEALTH_AI_INSTANCE
    if _HEALTH_AI_INSTANCE is None:
        _HEALTH_AI_INSTANCE = SpacecraftHealthAI()
    return _HEALTH_AI_INSTANCE

