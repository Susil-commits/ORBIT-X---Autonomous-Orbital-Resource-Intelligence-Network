"""Multivariate Isolation Forest Anomaly Detection Model (Compatibility Module).

Re-exports IsolationForestAnomalyDetector from `ml.models.anomaly.isolation_forest`.
"""

from ml.models.anomaly.isolation_forest import IsolationForestAnomalyDetector

__all__ = ["IsolationForestAnomalyDetector"]
