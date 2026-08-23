"""Metadata Completeness Evaluator for ORBIT-X Context Layer.

Evaluates the ratio of populated required schema and trust/governance attributes
across all registered operational datasets and canonical context graph entities:
Formula: sum(populated_contract_fields) / sum(expected_contract_fields)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MetadataCompletenessResult(BaseModel):
    metric_name: str = "metadata_completeness"
    score: float = Field(..., ge=0.0, le=1.0)
    score_pct: float = Field(..., ge=0.0, le=100.0)
    total_expected_fields: int
    populated_fields: int
    evaluated_assets_count: int
    details: Dict[str, Any] = Field(default_factory=dict)


def evaluate_metadata_completeness(datasets: Optional[List[Any]] = None) -> MetadataCompletenessResult:
    """Computes deterministic metadata completeness score across datasets."""
    if datasets is None:
        from context.metadata.catalog import SemanticMetadataCatalog
        catalog = SemanticMetadataCatalog()
        datasets = catalog.list_datasets()

    expected_dataset_fields = 10  # dataset_name, owner, description, schema_version, freshness_s, quality_score, status, last_reviewed, columns, downstream_models
    expected_column_fields = 2   # name, type/desc
    total_expected = 0
    populated = 0

    for ds in datasets:
        total_expected += expected_dataset_fields
        # Dataset-level fields
        name = getattr(ds, "dataset_name", getattr(ds, "name", None))
        owner = getattr(ds, "owner", None)
        desc = getattr(ds, "description", None)
        schema_v = getattr(ds, "schema_version", None)
        freshness = getattr(ds, "freshness_s", getattr(ds, "freshness", None))
        quality = getattr(ds, "quality_score", None)
        status = getattr(ds, "status", getattr(ds, "asset_status", None))
        reviewed = getattr(ds, "last_reviewed", None)
        cols = getattr(ds, "columns", [])
        models = getattr(ds, "downstream_models", getattr(ds, "downstream_consumers", []))

        for f_val in [name, owner, desc, schema_v, freshness, quality, status, reviewed, cols, models]:
            if f_val is not None and f_val != "" and f_val != []:
                populated += 1

        for col in cols:
            total_expected += expected_column_fields
            col_name = col.get("name") if isinstance(col, dict) else getattr(col, "name", None)
            col_type = (col.get("type") or col.get("desc")) if isinstance(col, dict) else (getattr(col, "type", None) or getattr(col, "description", None))
            if col_name:
                populated += 1
            if col_type:
                populated += 1

    score = round(populated / max(1, total_expected), 4)
    return MetadataCompletenessResult(
        score=score,
        score_pct=round(score * 100.0, 1),
        total_expected_fields=total_expected,
        populated_fields=populated,
        evaluated_assets_count=len(datasets),
        details={"populated_ratio": f"{populated}/{total_expected}"},
    )
