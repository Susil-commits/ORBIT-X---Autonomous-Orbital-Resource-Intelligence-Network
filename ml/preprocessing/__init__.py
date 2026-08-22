"""Feature normalization and standardization preprocessors for neural rankers."""

import importlib
from typing import Any

np = None
try:
    np = importlib.import_module("numpy")
except Exception:
    pass

class FeatureStandardizer:
    """Standardizes 13-dim resource and requirement feature vectors."""
    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, X: Any):
        if np is not None:
            self.mean = np.mean(X, axis=0)
            self.std = np.std(X, axis=0) + 1e-8

    def transform(self, X: Any) -> Any:
        if self.mean is None or np is None:
            return X
        return (X - self.mean) / self.std

    def fit_transform(self, X: Any) -> Any:
        self.fit(X)
        return self.transform(X)
