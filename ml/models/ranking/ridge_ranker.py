"""Regularized Linear Ridge Regression Ranker Baseline.

Provides the linear parametric baseline for candidate valuation scoring.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.linear_model import Ridge


class RidgeRanker:
    """Regularized Linear Ridge Regression baseline."""

    def __init__(self, alpha: float = 1.0):
        self.model_id = "orbitx-ranking-ridge-v1"
        self.version = "1.0.0"
        self.alpha = alpha
        self.model = Ridge(alpha=alpha)
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RidgeRanker":
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            return np.ones(len(X)) * 50.0
        return self.model.predict(X)

    def rank_candidates(self, X: np.ndarray, candidate_ids: List[str]) -> List[Dict[str, Any]]:
        scores = self.predict(X)
        ranked_indices = np.argsort(scores)[::-1]
        return [
            {
                "rank": rank + 1,
                "candidate_id": candidate_ids[idx],
                "score": float(round(scores[idx], 3)),
            }
            for rank, idx in enumerate(ranked_indices)
        ]


# Alias for backwards compatibility
RidgeBaseline = RidgeRanker
