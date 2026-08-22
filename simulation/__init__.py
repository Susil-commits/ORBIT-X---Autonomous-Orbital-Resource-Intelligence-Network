"""
ORBIT-X Simulation Package
==========================
Operational domain simulation environment providing realistic telemetry,
SGP4 orbital propagation, thermal/battery state dynamics, and stress scenarios
for evaluating the AI-native decision intelligence platform.
"""

from backend.app.simulation.constellation_simulator import (
    ConstellationSimulator,
    ConstellationState,
)
from backend.app.physics.orbit_propagator import (
    OrbitPropagator,
    SatellitePosition,
)
from backend.app.intelligence.battery_model import (
    BatteryThermalState,
    BatteryDegradationModel,
)

__all__ = [
    "ConstellationSimulator",
    "ConstellationState",
    "OrbitPropagator",
    "SatellitePosition",
    "BatteryThermalState",
    "BatteryDegradationModel",
]
