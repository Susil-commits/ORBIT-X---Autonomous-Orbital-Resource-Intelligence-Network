"""Context schema definitions for entities, metadata, lineage, and discovery."""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ContextEntity(BaseModel):
    entity_id: str
    entity_type: str = Field(..., description="Dataset | Feature | Model | Prediction | Anomaly | Decision | Mission | Tool | Scenario")
    name: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at_iso: str
