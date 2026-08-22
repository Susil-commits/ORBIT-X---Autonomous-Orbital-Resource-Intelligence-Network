"""ORBIT-X Machine Learning Package.

Modular ML subsystem featuring:
- Neural Ranking: Multi-Head Cross-Attention Network (resource-task interactions)
- Classical Baselines: Random, Greedy EDF, Ridge, Random Forest, MLP
- Tree-based Ranking: Gradient Boosting / XGBoost
- Explainable AI (XAI): TreeSHAP feature attributions and Attention heatmaps
- Training, evaluation metrics, and fast sub-millisecond inference
"""

from ml.models.cross_attention.ranker import (
    CrossAttentionNeuralRanker,
    ResourceFeatureEncoder,
    RequestRequirementEncoder,
    ConstellationCrossAttentionNet,
    CrossAttentionRanker,
    SatelliteFeatureEncoder,
    MissionRequirementEncoder,
)
from ml.models.baselines.classical import (
    RandomBaseline,
    GreedyEDFBaseline,
    RidgeBaseline,
    RandomForestBaseline,
    BidValueMLPBaseline,
)
from ml.models.xgboost.ranker import XGBoostRanker
from ml.explainability.shap_xai import TreeSHAPExplainer, AttentionHeatmapGenerator

__all__ = [
    "CrossAttentionNeuralRanker",
    "ResourceFeatureEncoder",
    "RequestRequirementEncoder",
    "ConstellationCrossAttentionNet",
    "CrossAttentionRanker",
    "SatelliteFeatureEncoder",
    "MissionRequirementEncoder",
    "RandomBaseline",
    "GreedyEDFBaseline",
    "RidgeBaseline",
    "RandomForestBaseline",
    "BidValueMLPBaseline",
    "XGBoostRanker",
    "TreeSHAPExplainer",
    "AttentionHeatmapGenerator",
]
