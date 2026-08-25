"""ORBIT-X Enterprise Machine Learning Package.

Modular, governed ML subsystem featuring:
1. Model Registry (`ml.registry`): Standardized model cards, SHA256 integrity, SLA gates, and governance lifecycle.
2. Candidate Ranking (`ml.models.ranking`): Multi-Head Cross-Attention (Champion), XGBoost, Neural Ranking MLP, Greedy EDF, Random, Ridge.
3. Telemetry Anomaly Detection (`ml.models.anomaly`): Multivariate Isolation Forest (Champion) with risk penalty feedback, Mahalanobis distance.
4. Lookahead Forecasting (`ml.models.forecasting`): Physics-Informed Battery SoC & Thermal forecaster, Linear decay.
5. Probability Calibration & Uncertainty (`ml.calibration`): Temperature Scaling, Conformal intervals, Epistemic/Aleatoric uncertainty.
6. Evaluation & Benchmarking (`ml.evaluation`): Rigorous 5-paradigm baseline comparisons and feature ablation.
"""

from ml.registry import (
    ModelRegistry,
    ModelCard,
    ModelStatus,
    TaskType,
    FeatureSchema,
    FeatureSpec,
    LatencyProfile,
    get_model_registry,
)
from ml.models.ranking import (
    CrossAttentionRanker,
    ConstellationCrossAttentionNet,
    CrossAttentionNeuralRanker,
    ResourceFeatureEncoder,
    RequestRequirementEncoder,
    SatelliteFeatureEncoder,
    MissionRequirementEncoder,
    XGBoostRanker,
    NeuralRankingMLP,
    BidValueMLPBaseline,
    GreedyEDFRanker,
    GreedyEDFBaseline,
    RandomRanker,
    RandomBaseline,
    RidgeRanker,
    RidgeBaseline,
)
from ml.models.anomaly import (
    IsolationForestAnomalyDetector,
    MahalanobisAnomalyDetector,
)
from ml.models.forecasting import (
    LookaheadBatteryForecaster,
    LinearDecayForecaster,
)
from ml.calibration import (
    TemperatureScalingCalibrator,
    UncertaintyEstimator,
)
from ml.evaluation.ranking_benchmarks import (
    RankingBaselineBenchmarkSuite,
    get_ranking_baseline_suite,
)

__all__ = [
    # Registry
    "ModelRegistry",
    "ModelCard",
    "ModelStatus",
    "TaskType",
    "FeatureSchema",
    "FeatureSpec",
    "LatencyProfile",
    "get_model_registry",
    # Ranking Models
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
    # Anomaly Detection
    "IsolationForestAnomalyDetector",
    "MahalanobisAnomalyDetector",
    # Forecasting
    "LookaheadBatteryForecaster",
    "LinearDecayForecaster",
    # Calibration & Uncertainty
    "TemperatureScalingCalibrator",
    "UncertaintyEstimator",
    # Evaluation
    "RankingBaselineBenchmarkSuite",
    "get_ranking_baseline_suite",
]
