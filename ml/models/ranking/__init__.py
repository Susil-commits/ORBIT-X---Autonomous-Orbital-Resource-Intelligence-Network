"""Candidate Ranking Models for ORBIT-X Autonomous Resource Systems.

Exports:
- CrossAttentionRanker (Production Champion neural ranker)
- XGBoostRanker (Gradient boosted decision tree ranker)
- NeuralRankingMLP / BidValueMLPBaseline (Deep feedforward neural ranker)
- GreedyEDFRanker (Deterministic priority + deadline heuristic)
- RandomRanker (Stochastic lower bound baseline)
- RidgeRanker (Linear regularized regression baseline)
"""

from ml.models.ranking.cross_attention import (
    CrossAttentionRanker,
    ConstellationCrossAttentionNet,
    CrossAttentionNeuralRanker,
    ResourceFeatureEncoder,
    RequestRequirementEncoder,
    SatelliteFeatureEncoder,
    MissionRequirementEncoder,
)
from ml.models.ranking.xgboost_ranker import XGBoostRanker
from ml.models.ranking.neural_ranker import NeuralRankingMLP, BidValueMLPBaseline
from ml.models.ranking.greedy_edf import GreedyEDFRanker, GreedyEDFBaseline
from ml.models.ranking.random_ranker import RandomRanker, RandomBaseline
from ml.models.ranking.ridge_ranker import RidgeRanker, RidgeBaseline

__all__ = [
    "CrossAttentionRanker",
    "ConstellationCrossAttentionNet",
    "CrossAttentionNeuralRanker",
    "ResourceFeatureEncoder",
    "RequestRequirementEncoder",
    "SatelliteFeatureEncoder",
    "MissionRequirementEncoder",
    "XGBoostRanker",
    "NeuralRankingMLP",
    "BidValueMLPBaseline",
    "GreedyEDFRanker",
    "GreedyEDFBaseline",
    "RandomRanker",
    "RandomBaseline",
    "RidgeRanker",
    "RidgeBaseline",
]
