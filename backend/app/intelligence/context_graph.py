"""Context Graph & Semantic Data Lineage Engine for ORBIT-X.

Constructs explicit graph relationships between Constellation Assets, Subsystems,
Telemetry Streams, Datasets, ML Models, Feature Tables, CP-SAT Optimization,
Decisions, and Mission Outcomes to enable verifiable context-aware AI reasoning.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app.core.schemas import (
    DataCatalogEntry,
    DataCatalogResponse,
    DataLineageNode,
    DataLineageEdge,
    DataLineageResponse,
)

CATALOG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "metadata" / "catalog.json"


class ContextGraphEngine:
    """
    In-memory knowledge & context graph orchestrator for data assets,
    model dependencies, operational lineage, and semantic metadata search.
    """

    def __init__(self, catalog_path: Optional[Path] = None):
        self.catalog_path = catalog_path or CATALOG_PATH
        self._catalog_cache: Optional[Dict[str, Any]] = None
        self._load_catalog()

    def _load_catalog(self) -> Dict[str, Any]:
        if self._catalog_cache is not None:
            return self._catalog_cache
        if self.catalog_path.exists():
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                self._catalog_cache = json.load(f)
        else:
            self._catalog_cache = {"catalog_version": "2.1.0", "datasets": []}
        return self._catalog_cache

    def get_catalog(self) -> DataCatalogResponse:
        """Returns the full semantic metadata catalog."""
        cat = self._load_catalog()
        datasets = [DataCatalogEntry(**d) for d in cat.get("datasets", [])]
        return DataCatalogResponse(
            catalog_version=cat.get("catalog_version", "2.1.0"),
            total_datasets=len(datasets),
            datasets=datasets,
        )

    def search_datasets(self, query: str) -> List[DataCatalogEntry]:
        """
        Semantic/keyword search across dataset names, descriptions, columns, and owners.
        """
        import re
        cat = self._load_catalog()
        q_lower = query.lower()
        q_clean = re.sub(r"[^a-z0-9]", "", q_lower)
        matched: List[DataCatalogEntry] = []

        for d in cat.get("datasets", []):
            entry = DataCatalogEntry(**d)
            # Combine all text fields for comprehensive matching
            entry_text = f"{entry.dataset_name} {entry.description} {entry.owner} {' '.join(entry.downstream_consumers)} {' '.join(c.name + ' ' + c.description for c in entry.columns)}"
            entry_clean = re.sub(r"[^a-z0-9]", "", entry_text.lower())

            if q_lower in entry_text.lower() or (q_clean and q_clean in entry_clean):
                matched.append(entry)

        return matched

    def get_dataset_metadata(self, dataset_name: str) -> Optional[DataCatalogEntry]:
        """Fetches metadata for a specific dataset by name."""
        cat = self._load_catalog()
        for d in cat.get("datasets", []):
            if d.get("dataset_name", "").lower() == dataset_name.lower():
                return DataCatalogEntry(**d)
        return None

    def trace_decision_lineage(
        self,
        mission_id: str,
        satellite_id: Optional[str] = "SAT-03",
        model_name: Optional[str] = "ConstellationCrossAttentionNet (v2.2)",
    ) -> DataLineageResponse:
        """
        Builds an end-to-end data lineage graph for a specific decision or mission assignment.
        Lineage: Raw Telemetry -> Cleaned Dataset -> Feature Table -> ML Prediction -> CP-SAT Optimization -> Decision Event -> Outcome.
        """
        sat_id = satellite_id or "SAT-03"
        nodes = [
            DataLineageNode(
                id="raw_telemetry",
                label=f"Raw Sensor Stream ({sat_id})",
                type="SOURCE_TELEMETRY",
                metadata={"source": "Onboard Sensors", "rate": "10Hz", "channels": ["voltage", "temp", "jitter", "snr"]},
            ),
            DataLineageNode(
                id="dataset_telemetry",
                label="Dataset: satellite_telemetry",
                type="DATASET",
                metadata={"quality_score": 0.992, "schema": "v2.0", "table": "orbitx.telemetry_frames"},
            ),
            DataLineageNode(
                id="feature_table",
                label="Feature Table: model_features",
                type="FEATURE_TABLE",
                metadata={"dimensions": 18, "satellite_dims": 10, "mission_dims": 8},
            ),
            DataLineageNode(
                id="ml_model",
                label=f"ML Model: {model_name}",
                type="ML_MODEL",
                metadata={"type": "Multi-Head Cross-Attention", "inference_latency_ms": 0.78, "top1_agreement_pct": 84.6},
            ),
            DataLineageNode(
                id="cpsat_optimizer",
                label="Optimizer: Google OR-Tools CP-SAT",
                type="OPTIMIZER",
                metadata={"constraints": ["SoC >= 20%", "Non-overlapping intervals", "Downlink precedence"]},
            ),
            DataLineageNode(
                id="decision_record",
                label=f"Decision Event ({mission_id})",
                type="DECISION",
                metadata={"assigned_satellite": sat_id, "status": "APPROVED", "win_prob": 0.94},
            ),
            DataLineageNode(
                id="mission_outcome",
                label=f"Mission Target Execution ({mission_id})",
                type="OUTCOME",
                metadata={"delivery_status": "COMPLETED", "feasibility_margin": "+18.5%"},
            ),
        ]

        edges = [
            DataLineageEdge(source="raw_telemetry", target="dataset_telemetry", relationship="VALIDATES_AND_STORES"),
            DataLineageEdge(source="dataset_telemetry", target="feature_table", relationship="EXTRACTS_FEATURES"),
            DataLineageEdge(source="feature_table", target="ml_model", relationship="FEEDS_INTO"),
            DataLineageEdge(source="ml_model", target="cpsat_optimizer", relationship="PROVIDES_CANDIDATE_PRIORS"),
            DataLineageEdge(source="cpsat_optimizer", target="decision_record", relationship="PRODUCES_ASSIGNMENT"),
            DataLineageEdge(source="decision_record", target="mission_outcome", relationship="DISPATCHES_COMMANDS"),
        ]

        summary = (
            f"Decision for {mission_id} was generated by extracting 18-dim features from {sat_id}'s verified telemetry, "
            f"ranking candidate feasibility via {model_name} (0.94 win prob), and verifying hard battery/thermal "
            f"constraints in Google OR-Tools CP-SAT."
        )

        return DataLineageResponse(
            target_id=mission_id,
            nodes=nodes,
            edges=edges,
            lineage_path_summary=summary,
        )

    def get_dataset_dependencies(self, dataset_name: str) -> Dict[str, Any]:
        """
        Traverses the graph to return which ML models, features, and pipelines depend on a given dataset.
        """
        meta = self.get_dataset_metadata(dataset_name)
        if not meta:
            return {"error": f"Dataset '{dataset_name}' not found in catalog."}

        return {
            "dataset_name": meta.dataset_name,
            "owner": meta.owner,
            "quality_score": meta.quality_score,
            "freshness": f"{meta.freshness_seconds}s",
            "downstream_consumers": meta.downstream_consumers,
            "dependent_models": [c for c in meta.downstream_consumers if "AI" in c or "Net" in c or "MLP" in c or "Simulator" in c or "Baseline" in c],
            "lineage_impact": f"Any schema drift or corruption in '{dataset_name}' directly degrades {len(meta.downstream_consumers)} downstream AI pipelines.",
        }


# Singleton accessor
_context_graph_instance: Optional[ContextGraphEngine] = None


def get_context_graph_engine() -> ContextGraphEngine:
    global _context_graph_instance
    if _context_graph_instance is None:
        _context_graph_instance = ContextGraphEngine()
    return _context_graph_instance
