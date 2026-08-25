"""Uniform Random Candidate Selection Baseline.

Provides the empirical lower bound for candidate ranking accuracy and MAE.
"""

from typing import List, Dict, Any, Optional
import numpy as np


class RandomRanker:
    """Randomly assigns scores to candidate resources uniformly."""

    def __init__(self, random_state: int = 42):
        self.model_id = "orbitx-ranking-random-v1"
        self.version = "1.0.0"
        self.random_state = random_state
        self.rng = np.random.RandomState(random_state)

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        """No-op for random selector."""
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Returns uniform random numbers in [0.0, 100.0]."""
        return self.rng.uniform(0.0, 100.0, size=len(X))

    def rank_candidates(self, X: np.ndarray, candidate_ids: List[str]) -> List[Dict[str, Any]]:
        """Ranks candidates randomly."""
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
RandomBaseline = RandomRanker
