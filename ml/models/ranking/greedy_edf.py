"""Greedy Earliest-Deadline-First / Priority Heuristic Baseline.

Deterministic rule-based baseline ranking candidate resources by urgent deadline,
elevation angle, and residual power margin.
"""

from typing import List, Dict, Any, Optional
import numpy as np


class GreedyEDFRanker:
    """Deterministic Greedy Earliest Deadline First + Priority ranking heuristic."""

    def __init__(self):
        self.model_id = "orbitx-ranking-greedy-edf-v1"
        self.version = "1.0.0"

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        """No-op for parameter-free heuristic."""
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Computes heuristic priority score from feature vectors.
        Feature indices:
        - X[:, 0]: Satellite Battery SoC [0.0, 1.0]
        - X[:, 1]: Satellite Temp / Power
        - X[:, 2]: Max elevation / Geometry [0.0, 1.0]
        - X[:, 7]: Mission Priority [1.0 - 5.0] or [0.0 - 1.0]
        - X[:, 10]: Deadline slack [0.0, 1.0]
        """
        if X.shape[1] >= 11:
            soc = np.clip(X[:, 0], 0.0, 1.0)
            elevation = np.clip(X[:, 2], 0.0, 1.0)
            prio_raw = X[:, 7]
            prio_norm = np.clip(prio_raw / 5.0 if np.max(prio_raw) > 1.0 else prio_raw, 0.0, 1.0)
            slack = np.clip(X[:, 10], 0.0, 1.0)

            # High priority (40 pts) + high elevation (25 pts) + high SoC (25 pts) + urgent deadline (10 pts)
            score = (prio_norm * 40.0) + (elevation * 25.0) + (soc * 25.0) + ((1.0 - slack) * 10.0)
            return score
        elif X.shape[1] >= 3:
            return np.clip(X[:, 0] * 40.0 + X[:, 1] * 30.0 + X[:, 2] * 30.0, 0.0, 100.0)
        return np.linspace(10.0, 90.0, len(X))

    def rank_candidates(self, X: np.ndarray, candidate_ids: List[str]) -> List[Dict[str, Any]]:
        """Ranks candidates by descending heuristic score."""
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
GreedyEDFBaseline = GreedyEDFRanker
