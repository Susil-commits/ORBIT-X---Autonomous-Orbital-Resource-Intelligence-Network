"""ORBIT-X Anomaly Detection Package.

Unsupervised multivariate anomaly detection based on scikit-learn Isolation Forest
for operational telemetry health scoring, predictive maintenance, and risk penalty injection.
"""

from anomaly_detection.models.isolation_forest import IsolationForestAnomalyDetector
from backend.app.intelligence.health_ai import (
    SpacecraftHealthAI,
    get_health_ai,
)

# Compatibility alias
SatelliteHealthAI = SpacecraftHealthAI

__all__ = [
    "IsolationForestAnomalyDetector",
    "SpacecraftHealthAI",
    "SatelliteHealthAI",
    "get_health_ai",
]
