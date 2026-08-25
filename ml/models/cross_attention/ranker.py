"""Multi-Head Cross-Attention Neural Ranking Model (Compatibility Module).

Re-exports core classes from `ml.models.ranking.cross_attention`.
"""

from ml.models.ranking.cross_attention import (
    ResourceFeatureEncoder,
    RequestRequirementEncoder,
    CrossAttentionRanker,
    ConstellationCrossAttentionNet,
    CrossAttentionNeuralRanker,
    SatelliteFeatureEncoder,
    MissionRequirementEncoder,
)

__all__ = [
    "ResourceFeatureEncoder",
    "RequestRequirementEncoder",
    "CrossAttentionRanker",
    "ConstellationCrossAttentionNet",
    "CrossAttentionNeuralRanker",
    "SatelliteFeatureEncoder",
    "MissionRequirementEncoder",
]
