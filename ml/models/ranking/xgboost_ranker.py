"""XGBoost / Gradient Boosted Decision Tree Candidate Ranker.

Provides fast, high-accuracy tree-based decision valuation and candidate scoring for tabular features.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score


class XGBoostRanker:
    """Gradient Boosted Decision Tree ranker for candidate scoring."""

    def __init__(
        self,
        n_estimators: int = 120,
        learning_rate: float = 0.08,
        max_depth: int = 6,
        random_state: int = 42,
    ):
        self.model_id = "orbitx-ranking-xgboost-v1"
        self.version = "1.1.0"
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = GradientBoostingRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            random_state=self.random_state,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "XGBoostRanker":
        """Fits the gradient boosted ensemble on candidate-request tabular features."""
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts continuous match valuation scores."""
        if not self.is_fitted:
            # Fallback heuristic calculation if not yet explicitly trained
            if X.shape[1] >= 8:
                return np.clip(X[:, 0] * 50.0 + X[:, 7] * 50.0, 0.0, 100.0)
            return np.ones(len(X)) * 50.0
        return self.model.predict(X)

    def rank_candidates(self, X: np.ndarray, candidate_ids: List[str]) -> List[Dict[str, Any]]:
        """Ranks candidates by descending estimated score."""
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

    @property
    def feature_importances_(self) -> Optional[np.ndarray]:
        """Returns Gini feature importance array if fitted."""
        if self.is_fitted and hasattr(self.model, "feature_importances_"):
            return self.model.feature_importances_
        return None
