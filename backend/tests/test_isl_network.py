"""Tests for Intersatellite Optical Laser Links (ISL) Mesh & Multi-Hop Routing."""

import numpy as np
from app.physics.isl_network import is_line_of_sight_occluded, build_isl_mesh
from app.physics.orbit_propagator import create_initial_constellation
from app.physics.access_model import get_default_ground_stations


def test_line_of_sight_occlusion():
    # 1. Two satellites on opposite sides of Earth (x = -7000 km and x = +7000 km) -> occluded
    r1 = np.array([-7000.0, 0.0, 0.0])
    r2 = np.array([7000.0, 0.0, 0.0])
    assert is_line_of_sight_occluded(r1, r2) is True

    # 2. Two adjacent satellites in same orbit plane (x = 7000 km, y = 0 vs x = 6500 km, y = 2000 km) -> clear
    r3 = np.array([7000.0, 0.0, 0.0])
    r4 = np.array([6500.0, 2500.0, 0.0])
    assert is_line_of_sight_occluded(r3, r4) is False


def test_build_isl_mesh():
    satellites = create_initial_constellation()
    ground_stations = get_default_ground_stations()

    mesh = build_isl_mesh(satellites, ground_stations, max_range_km=5000.0)

    assert mesh.max_links_possible == (12 * 11) // 2  # 66 total pairs
    assert mesh.active_links_count > 0
    assert len(mesh.links) == 66
    assert mesh.average_latency_ms > 0.0

    # Ensure routes exist to ground stations
    assert len(mesh.routes) > 0
    for r in mesh.routes:
        assert len(r.hops) >= 2
        assert r.source_sat_id.startswith("SAT-")
        assert r.target_gs_id.startswith("GS-")
