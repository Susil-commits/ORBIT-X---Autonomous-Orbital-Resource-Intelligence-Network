"""Tests for Keplerian Orbit Propagator & Constellation Generation."""

import math
import numpy as np
from app.core.schemas import KeplerianElements
from app.physics.orbit_propagator import (
    solve_kepler,
    propagate_orbit,
    create_initial_constellation,
    EARTH_RADIUS_KM,
    MU_EARTH,
)


def test_kepler_solver():
    """Verify Kepler equation solver on known eccentric anomaly values."""
    e = 0.1
    M = 0.5
    E = solve_kepler(M, e)
    # Check E - e*sin(E) == M
    residual = abs(E - e * math.sin(E) - M)
    assert residual < 1e-6


def test_orbit_propagation_circular():
    """Verify circular LEO orbit period and altitude consistency."""
    altitude_km = 550.0
    semi_major = EARTH_RADIUS_KM + altitude_km
    expected_period = 2.0 * math.pi * math.sqrt((semi_major ** 3) / MU_EARTH)
    
    keplerian = KeplerianElements(
        semi_major_axis_km=semi_major,
        eccentricity=0.0,
        inclination_deg=53.0,
        raan_deg=0.0,
        arg_perigee_deg=0.0,
        mean_anomaly_deg=0.0,
        epoch_time_s=0.0,
    )
    
    # At t=0
    r_eci_0, v_eci_0, r_ecef_0, geo_0, sun_0 = propagate_orbit(keplerian, 0.0)
    assert abs(geo_0.alt - altitude_km) < 5.0
    assert abs(np.linalg.norm(r_eci_0) - semi_major) < 1.0
    
    # At t=period (should return near start in ECI)
    r_eci_T, _, _, _, _ = propagate_orbit(keplerian, expected_period)
    dist_diff = np.linalg.norm(r_eci_T - r_eci_0)
    # Secular J2 causes minor nodal shift, but distance should be close
    assert dist_diff < 50.0


def test_constellation_generation():
    """Verify Walker constellation generation produces requested number of satellites."""
    sats = create_initial_constellation(num_planes=3, sats_per_plane=4)
    assert len(sats) == 12
    # Verify all satellites have valid coordinates and nominal health
    for sat in sats:
        assert sat.geodetic.alt > 500.0
        assert sat.battery.soc > 0.8
        assert sat.health_status.value == "NOMINAL"
