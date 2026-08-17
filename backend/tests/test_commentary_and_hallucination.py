"""Unit tests for Tactical Flight Director commentary & Fact-Consistency Verifier."""

import pytest
from app.intelligence.commentary_generator import (
    get_commentary_generator,
    FactConsistencyVerifier,
)


def test_fact_consistency_verifier():
    """Validates that verifier catches hallucinated satellite IDs."""
    source_event = {
        "satellite_id": "SAT-04",
        "mission_id": "MIS-WILDFIRE-09",
        "battery_soc": 0.85,
    }
    
    # Valid text
    valid_text = "FLIGHT-DIR: Reassigning SAT-04 to MIS-WILDFIRE-09 with 85% battery reserve."
    is_valid, reason = FactConsistencyVerifier.verify(valid_text, source_event)
    assert is_valid is True
    
    # Hallucinated satellite
    hallucinated_text = "FLIGHT-DIR: Reassigning SAT-99 to MIS-WILDFIRE-09."
    is_valid, reason = FactConsistencyVerifier.verify(hallucinated_text, source_event)
    assert is_valid is False
    assert "SAT-99" in reason


def test_deterministic_template_fallback():
    """Validates deterministic fallback commentary generation."""
    cg = get_commentary_generator()
    ev = {
        "satellite_id": "SAT-02",
        "mission_id": "TARGET-BRAVO",
        "max_elevation_deg": 72.0,
    }
    comment = cg.generate_commentary("MISSION_ASSIGNED", 30.0, ev)
    
    assert "SAT-02" in comment.commentary
    assert comment.verified_factual is True
