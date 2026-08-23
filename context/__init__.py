"""ORBIT-X Context Layer Package.

Provides semantic metadata cataloging, natural language data discovery,
10-entity bidirectional data lineage DAG tracking, multi-modal context retrieval,
and formal context quality evaluation across 5 canonical dimensions.
"""

from context.schemas import (
    AssetStatus,
    GovernedAsset,
    ContextEntity,
    Dataset,
    Mission,
    Satellite,
    TelemetryStream,
    Feature,
    Model,
    Prediction,
    Anomaly,
    Decision,
    Tool,
    DatasetAsset,
    MissionAsset,
    SatelliteAsset,
    TelemetryStreamAsset,
    FeatureAsset,
    ModelAsset,
    PredictionAsset,
    AnomalyAsset,
    DecisionAsset,
    ToolAsset,
)
from context.metadata.catalog import SemanticMetadataCatalog, DatasetMetadataRecord
from context.discovery.search import DataDiscoveryEngine
from context.lineage.graph import DataLineageGraph, LineageNode, LineageEdge
from context.evaluation import (
    evaluate_metadata_completeness,
    MetadataCompletenessResult,
    evaluate_lineage_coverage,
    LineageCoverageResult,
    evaluate_freshness,
    FreshnessEvaluationResult,
    evaluate_retrieval_groundedness,
    RetrievalGroundednessResult,
    evaluate_stale_context_rate,
    StaleContextRateResult,
    ComprehensiveContextEvaluationReport,
    evaluate_all_context_metrics,
)

# Backward-compatible re-exports
try:
    from backend.app.intelligence.context_graph import (
        ContextGraphEngine,
        get_context_graph_engine,
    )
    from backend.app.intelligence.data_quality_agent import (
        DataQualityAgent,
        get_data_quality_agent,
    )
    ContextGraph = ContextGraphEngine
except Exception:
    ContextGraphEngine = None  # type: ignore
    get_context_graph_engine = None  # type: ignore
    DataQualityAgent = None  # type: ignore
    get_data_quality_agent = None  # type: ignore
    ContextGraph = None  # type: ignore

__all__ = [
    # 10 Canonical Context Entities
    "Dataset",
    "Mission",
    "Satellite",
    "TelemetryStream",
    "Feature",
    "Model",
    "Prediction",
    "Anomaly",
    "Decision",
    "Tool",
    # Asset Schemas & Governance
    "AssetStatus",
    "GovernedAsset",
    "ContextEntity",
    "DatasetAsset",
    "MissionAsset",
    "SatelliteAsset",
    "TelemetryStreamAsset",
    "FeatureAsset",
    "ModelAsset",
    "PredictionAsset",
    "AnomalyAsset",
    "DecisionAsset",
    "ToolAsset",
    # Catalog, Discovery, Lineage
    "SemanticMetadataCatalog",
    "DatasetMetadataRecord",
    "DataDiscoveryEngine",
    "DataLineageGraph",
    "LineageNode",
    "LineageEdge",
    # Evaluation Package
    "evaluate_metadata_completeness",
    "MetadataCompletenessResult",
    "evaluate_lineage_coverage",
    "LineageCoverageResult",
    "evaluate_freshness",
    "FreshnessEvaluationResult",
    "evaluate_retrieval_groundedness",
    "RetrievalGroundednessResult",
    "evaluate_stale_context_rate",
    "StaleContextRateResult",
    "ComprehensiveContextEvaluationReport",
    "evaluate_all_context_metrics",
    # Backward Compatibility
    "ContextGraphEngine",
    "ContextGraph",
    "get_context_graph_engine",
    "DataQualityAgent",
    "get_data_quality_agent",
]
