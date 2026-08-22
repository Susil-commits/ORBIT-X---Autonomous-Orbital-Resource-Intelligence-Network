"""Processed and validated operational dataset storage."""

from typing import List, Dict, Any

def get_processed_dataset_index() -> List[str]:
    """Returns list of curated and normalized operational datasets."""
    return [
        "satellite_telemetry_curated",
        "mission_demands_normalized",
        "conjunction_events_historical",
    ]
