"""ORBIT-X Context Layer Package.

Provides semantic metadata cataloging, natural language data discovery,
bidirectional data lineage DAG tracking, and multi-modal context retrieval.
"""

from context.metadata.catalog import SemanticMetadataCatalog, DatasetMetadataRecord
from context.discovery.search import DataDiscoveryEngine
from context.lineage.graph import DataLineageGraph, LineageNode, LineageEdge

# Backward-compatible re-exports
from backend.app.intelligence.context_graph import (
    ContextGraphEngine,
    get_context_graph_engine,
)
from backend.app.intelligence.data_quality_agent import (
    DataQualityAgent,
    get_data_quality_agent,
)

# Compatibility aliases
ContextGraph = ContextGraphEngine

__all__ = [
    "SemanticMetadataCatalog",
    "DatasetMetadataRecord",
    "DataDiscoveryEngine",
    "DataLineageGraph",
    "LineageNode",
    "LineageEdge",
    "ContextGraphEngine",
    "ContextGraph",
    "get_context_graph_engine",
    "DataQualityAgent",
    "get_data_quality_agent",
]
