"""
ORBIT-X ML Package
==================
Modular Machine Learning subsystem for candidate ranking, bid value estimation,
classical baselines, deep learning cross-attention models, and TreeSHAP explainability.
"""

from backend.app.intelligence.baselines import (
    BaselineComparisonSuite,
    RandomBaseline,
    GreedyEDFBaseline,
    RidgeBaseline,
    RandomForestBaseline,
    BidValueMLPBaseline,
)
from backend.app.intelligence.cross_attention_network import (
    ConstellationCrossAttentionNet,
    CrossAttentionRanker,
    SatelliteFeatureEncoder,
    MissionRequirementEncoder,
)
from backend.app.intelligence.shap_explainer import (
    TreeSHAPExplainer,
    AttentionHeatmapGenerator,
)
from backend.app.intelligence.bid_value_network import (
    NeuralBidNetwork,
    MissionBidPredictor,
)

__all__ = [
    "BaselineComparisonSuite",
    "RandomBaseline",
    "GreedyEDFBaseline",
    "RidgeBaseline",
    "RandomForestBaseline",
    "BidValueMLPBaseline",
    "ConstellationCrossAttentionNet",
    "CrossAttentionRanker",
    "SatelliteFeatureEncoder",
    "MissionRequirementEncoder",
    "TreeSHAPExplainer",
    "AttentionHeatmapGenerator",
    "NeuralBidNetwork",
    "MissionBidPredictor",
]
