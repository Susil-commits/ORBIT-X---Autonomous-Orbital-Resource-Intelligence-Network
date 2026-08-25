"""Classical Machine Learning and Heuristic Baselines (Compatibility Module).

Re-exports baseline rankers from `ml.models.ranking`.
"""

from ml.models.ranking.random_ranker import RandomRanker, RandomBaseline
from ml.models.ranking.greedy_edf import GreedyEDFRanker, GreedyEDFBaseline
from ml.models.ranking.ridge_ranker import RidgeRanker, RidgeBaseline
from ml.models.ranking.neural_ranker import NeuralRankingMLP, BidValueMLPBaseline

# Additional Random Forest baseline for compatibility
from sklearn.ensemble import RandomForestRegressor
import numpy as np


class RandomForestBaseline:
    """Random Forest regressor baseline."""
    def __init__(self, n_estimators: int = 100, max_depth: int = 8, random_state: int = 42):
        self.model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)


__all__ = [
    "RandomRanker",
    "RandomBaseline",
    "GreedyEDFRanker",
    "GreedyEDFBaseline",
    "RidgeRanker",
    "RidgeBaseline",
    "RandomForestBaseline",
    "NeuralRankingMLP",
    "BidValueMLPBaseline",
]
