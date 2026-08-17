"""Tests for Advanced Multi-Distribution Dataset Generator."""

import pytest
import numpy as np
from training.advanced_dataset_generator import (
    generate_advanced_scenario,
    extract_mission_features,
    MISSION_FEATURE_NAMES,
)


def test_extract_mission_features():
    feat = extract_mission_features(
        priority=5,
        deadline_s=3600.0,
        duration_s=30.0,
        data_size_gb=15.0,
        lat=35.0,
        lon=139.0,
        cloud_cover_prob=0.2,
        solar_flux_index=1.2,
    )

    assert len(feat) == len(MISSION_FEATURE_NAMES)
    assert np.all(feat >= 0.0) and np.all(feat <= 1.0)


def test_generate_advanced_scenario():
    satellites, ground_stations, missions, env_meta = generate_advanced_scenario(
        scenario_id=99,
        num_missions=3,
        constellation_source="synthetic",
        augment_geomagnetic=True,
        augment_cloud_cover=True,
    )

    assert len(satellites) > 0
    assert len(ground_stations) > 0
    assert len(missions) == 3
    assert "solar_flux_index" in env_meta
    assert env_meta["solar_flux_index"] > 0.0
