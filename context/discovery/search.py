"""Data Discovery Engine.

Supports exact, schema-based, and natural language semantic queries over datasets and features:
- "Show me datasets containing battery telemetry."
- "Which dataset is freshest?"
- "Which datasets feed the Cross-Attention ranker?"
"""

from typing import List, Dict, Any, Optional
from context.metadata.catalog import SemanticMetadataCatalog, DatasetMetadataRecord


class DataDiscoveryEngine:
    """Discovers datasets based on metadata attributes, schemas, freshness, and NL queries."""

    def __init__(self, catalog: Optional[SemanticMetadataCatalog] = None):
        self.catalog = catalog or SemanticMetadataCatalog()

    def find_by_query(self, query: str) -> List[DatasetMetadataRecord]:
        """Resolves natural language / keyword discovery queries over the catalog."""
        q = query.lower()
        datasets = self.catalog.list_datasets()

        # Freshest dataset query
        if "fresh" in q or "recent" in q:
            return sorted(datasets, key=lambda d: d.freshness_s)

        results = []
        for ds in datasets:
            match_score = 0
            if ds.dataset_name.lower() in q:
                match_score += 5
            if any(word in ds.description.lower() for word in q.split()):
                match_score += 2
            if any(word in col["name"].lower() or word in col["desc"].lower() for col in ds.columns for word in q.split()):
                match_score += 3
            if any(model.lower() in q for model in ds.downstream_models):
                match_score += 4

            if match_score > 0:
                results.append((ds, match_score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results] if results else datasets[:2]
