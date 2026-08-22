"""Anomaly detection telemetry normalization and outlier filtering."""

import importlib
from typing import Any

np = None
try:
    np = importlib.import_module("numpy")
except Exception:
    pass

class TelemetryScaler:
    """Robust scaler for sensor telemetry channels."""
    def __init__(self):
        self.median = None
        self.iqr = None

    def fit_transform(self, X: Any) -> Any:
        if np is None:
            return X
        self.median = np.median(X, axis=0)
        q75, q25 = np.percentile(X, [75, 25], axis=0)
        self.iqr = q75 - q25 + 1e-6
        return (X - self.median) / self.iqr
