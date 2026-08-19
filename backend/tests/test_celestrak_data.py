"""Unit tests for Celestrak TLE parsing, orbital elements extraction & ISS physical verification."""

import pytest
import math
from app.data.fetch_real_constellation import parse_tle_to_keplerian
from app.physics.orbit_propagator import (
    create_initial_constellation,
    compute_orbital_period_minutes,
    load_real_constellation,
)


def test_parse_iss_tle_ground_truth():
    """Validates TLE parsing on standard ISS element set."""
    line1 = "1 25544U 98067A   24080.51888495  .00014389  00000+0  26388-3 0  9997"
    line2 = "2 25544  51.6425 208.6185 0005086  94.6181 265.5562 15.49842884444456"
    
    elem = parse_tle_to_keplerian(line1, line2)
    
    assert elem["norad_id"] == 25544
    assert abs(elem["inclination_deg"] - 51.6425) < 0.001
    assert abs(elem["raan_deg"] - 208.6185) < 0.001
    assert abs(elem["eccentricity"] - 0.0005086) < 0.00001
    # Mean motion ~15.498 rev/day corresponds to period ~92.9 min
    assert 91.5 <= elem["period_minutes"] <= 93.5
    # Altitude ~415-425 km
    assert 400.0 <= elem["perigee_alt_km"] <= 435.0


def test_malformed_tle_fails_loudly():
    """Ensures parser raises ValueError on truncated or malformed lines."""
    with pytest.raises(ValueError):
        parse_tle_to_keplerian("1 25544", "2 25544")


def test_real_constellation_loading():
    """Tests loading real constellation from real_constellation.json."""
    sats = create_initial_constellation(source="celestrak_real")
    assert len(sats) >= 12
    assert sats[0].data_source == "celestrak_real"
    assert sats[0].keplerian.semi_major_axis_km > 6500.0
    
    # Check physical period of first satellite (~90-100 min)
    period = compute_orbital_period_minutes(sats[0].keplerian.semi_major_axis_km)
    assert 90.0 <= period <= 105.0


def test_tle_pipeline_manager_caching_and_checksum(tmp_path):
    """Tests TLE pipeline manager local caching, SHA-256 calculation and fallback."""
    from app.physics.tle_pipeline import TLEPipelineManager
    
    manager = TLEPipelineManager(cache_dir=tmp_path)
    sample_tle = "1 25544U 98067A   24080.51888495  .00014389  00000+0  26388-3 0  9997\n2 25544  51.6425 208.6185 0005086  94.6181 265.5562 15.49842884444456"
    checksum = manager.compute_checksum(sample_tle)
    assert len(checksum) == 64  # SHA-256
    
    # Test packaging
    parsed = manager._parse_and_package(
        raw_tle=sample_tle,
        group="stations",
        source_url="https://celestrak.org",
        target_count=1,
        source_type="test_mock",
    )
    assert parsed["data_source"] == "celestrak_real"
    assert parsed["checksum_sha256"] == checksum
    assert len(parsed["satellites"]) == 1
    assert parsed["satellites"][0]["norad_id"] == 25544

