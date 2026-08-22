"""Simulation Orbital Physics and SGP4 Propagation Engine.

Underneath the AI platform, provides authentic orbital ephemeris calculations,
Keplerian orbit propagation, and J2 secular perturbations to generate realistic spatial constraints.
"""

from backend.app.physics.orbit_propagator import (
    solve_kepler,
    propagate_orbit,
    create_synthetic_constellation,
    load_real_constellation,
    create_initial_constellation,
    compute_orbital_period_minutes,
)
from backend.app.physics.tle_pipeline import TLEPipelineManager

# Compatibility aliases
generate_walker_delta_constellation = create_synthetic_constellation
load_celestrak_constellation = load_real_constellation

__all__ = [
    "solve_kepler",
    "propagate_orbit",
    "create_synthetic_constellation",
    "load_real_constellation",
    "create_initial_constellation",
    "compute_orbital_period_minutes",
    "generate_walker_delta_constellation",
    "load_celestrak_constellation",
    "TLEPipelineManager",
]
