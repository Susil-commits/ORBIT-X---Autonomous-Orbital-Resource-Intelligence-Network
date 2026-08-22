"""Classical Machine Learning and Heuristic Baselines.

Implements Random, Greedy EDF, Ridge Linear Regression, Random Forest,
and MLP baselines for rigorous held-out performance benchmarking.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


class RandomBaseline:
    """Randomly assigns tasks to candidate resources uniformly."""
    def fit(self, X: np.ndarray, y: np.ndarray):
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.random.uniform(0.0, 100.0, size=len(X))


class GreedyEDFBaseline:
    """Greedy Earliest-Deadline-First / Priority heuristic."""
    def fit(self, X: np.ndarray, y: np.ndarray):
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        # Assumes feature columns [priority_idx=7, slack_idx=10]
        # High priority + tight deadline = high heuristic valuation
        if X.shape[1] > 10:
            priority = X[:, 7]
            slack = X[:, 10]
            score = (priority * 60.0) + ((1.0 - slack) * 40.0)
            return np.clip(score, 0.0, 100.0)
        return np.linspace(10.0, 90.0, len(X))


class RidgeBaseline:
    """Regularized Linear Ridge Regression baseline."""
    def __init__(self, alpha: float = 1.0):
        self.model = Ridge(alpha=alpha)

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)


class RandomForestBaseline:
    """Random Forest / Gradient Boosted ensemble baseline."""
    def __init__(self, n_estimators: int = 100, max_depth: int = 8, random_state: int = 42):
        self.model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)


class BidValueMLPBaseline:
    """Multi-Layer Perceptron neural baseline."""
    def __init__(self):
        self.model = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        from sklearn.neural_network import MLPRegressor
        self.model = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            return np.random.uniform(20.0, 80.0, size=len(X))
        return self.model.predict(X)
