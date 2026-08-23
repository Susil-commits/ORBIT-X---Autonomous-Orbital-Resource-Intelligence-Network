"""Data Discovery Engine with Trust & Governance Signals.

Supports exact, schema-based, and natural language semantic queries over datasets and features:
- "Show me datasets containing battery telemetry."
- "Which dataset is freshest?"
- "Which datasets feed the Cross-Attention ranker?"

Enforces trust-weighted retrieval: strictly prefers certified VERIFIED and fresh assets
over uncalibrated DRAFT or DEPRECATED assets.
"""

import re
from typing import List, Dict, Any, Optional
from context.metadata.catalog import SemanticMetadataCatalog, DatasetMetadataRecord


class DataDiscoveryEngine:
    """Discovers datasets based on semantic metadata, schemas, freshness SLAs, and governance status."""

    def __init__(self, catalog: Optional[SemanticMetadataCatalog] = None):
        self.catalog = catalog or SemanticMetadataCatalog()

    def find_by_query(self, query: str, prefer_verified: bool = True) -> List[DatasetMetadataRecord]:
        """Resolves natural language / keyword discovery queries over the catalog with trust weighting."""
        q = query.lower()
        datasets = self.catalog.list_datasets()

        # Freshest dataset query
        if "fresh" in q or "recent" in q:
            valid_candidates = datasets
            if prefer_verified:
                # Prioritize verified assets first, then by freshness
                status_priority = {"VERIFIED": 0, "DRAFT": 1, "DEPRECATED": 2}
                return sorted(valid_candidates, key=lambda d: (status_priority.get(d.status, 3), d.freshness_s))
            return sorted(valid_candidates, key=lambda d: d.freshness_s)

        results = []
        for ds in datasets:
            match_score = 0.0
            if ds.dataset_name.lower() in q:
                match_score += 10.0
            if any(word in ds.description.lower() for word in q.split()):
                match_score += 3.0
            if any(word in col["name"].lower() or word in col.get("desc", "").lower() for col in ds.columns for word in q.split()):
                match_score += 4.0
            if any(model.lower() in q for model in ds.downstream_models):
                match_score += 5.0
            if ds.owner.lower() in q:
                match_score += 4.0

            if match_score > 0:
                # Governance trust signal multipliers
                if prefer_verified:
                    status_mult = 1.5 if ds.status == "VERIFIED" else (0.7 if ds.status == "DRAFT" else 0.2)
                else:
                    status_mult = 1.0
                
                quality_mult = ds.quality_score  # [0.0, 1.0]
                # Freshness penalty if older than 1 hour (3600s)
                freshness_factor = 1.0 if ds.freshness_s <= 3600.0 else 0.8

                final_rank_score = match_score * status_mult * quality_mult * freshness_factor
                results.append((ds, final_rank_score, ds.status, ds.quality_score))

        if results:
            if prefer_verified:
                status_order = {"VERIFIED": 0, "DRAFT": 1, "DEPRECATED": 2}
                results.sort(key=lambda x: (status_order.get(x[2], 3), -x[1], -x[3]))
            else:
                results.sort(key=lambda x: x[1], reverse=True)
            return [r[0] for r in results]

        # Default fallback
        if prefer_verified:
            verified_only = [d for d in datasets if d.status == "VERIFIED"]
            return verified_only[:2] if verified_only else datasets[:2]
        return datasets[:2]

    def search(self, query: str, prefer_verified: bool = True, require_verified: bool = False) -> List[DatasetMetadataRecord]:
        """High-level search interface with strict verification gating options."""
        results = self.find_by_query(query, prefer_verified=prefer_verified)
        if require_verified:
            return [r for r in results if r.status == "VERIFIED"]
        return results
