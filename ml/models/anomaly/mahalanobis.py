"""Multivariate Mahalanobis Distance Anomaly Detector Baseline.

Statistical baseline for multivariate telemetry anomaly detection using covariance inversion.
"""

from typing import Dict, Any, Optional
import numpy as np


class MahalanobisAnomalyDetector:
    """Multivariate Mahalanobis distance baseline detector."""

    def __init__(self, threshold: float = 3.0):
        self.model_id = "orbitx-anomaly-mahalanobis-v1"
        self.version = "1.0.0"
        self.threshold = threshold
        self.mean: Optional[np.ndarray] = None
        self.inv_cov: Optional[np.ndarray] = None
        self.is_fitted = False
        self._bootstrap_nominal()

    def _bootstrap_nominal(self):
        """Initializes with nominal parameters."""
        np.random.seed(42)
        nominal_data = np.random.randn(500, 7)
        self.fit(nominal_data)

    def fit(self, X: np.ndarray) -> "MahalanobisAnomalyDetector":
        """Fits empirical mean and inverse regularized covariance matrix."""
        self.mean = np.mean(X, axis=0)
        cov = np.cov(X, rowvar=False) + np.eye(X.shape[1]) * 1e-4
        self.inv_cov = np.linalg.pinv(cov)
        self.is_fitted = True
        return self

    def score_telemetry(self, telemetry_vector: np.ndarray) -> Dict[str, Any]:
        """Calculates Mahalanobis distance and flags anomalies."""
        x = np.asarray(telemetry_vector, dtype=np.float64).flatten()
        diff = x - self.mean
        dist = float(np.sqrt(np.dot(np.dot(diff, self.inv_cov), diff)))
        is_anomaly = bool(dist > self.threshold)
        score = float(np.clip(dist / (self.threshold * 2.0), 0.0, 1.0))

        return {
            "mahalanobis_distance": round(dist, 4),
            "anomaly_score": round(score, 4),
            "is_anomaly": is_anomaly,
            "severity": "CRITICAL" if score > 0.85 else ("MEDIUM" if is_anomaly else "NOMINAL"),
            "threshold": self.threshold,
        }
