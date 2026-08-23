"""Simulation Battery Degradation and Thermal Dynamics Constraints.

Models Stefan-Boltzmann radiative thermal exchange, solar panel illumination,
and non-linear battery degradation to generate physical constraints for the AI platform.
"""

from backend.app.simulation.battery_model import (
    compute_step_battery_update,
    forecast_battery_profile,
    estimate_mission_energy_cost,
)
from backend.app.simulation.pinn_battery_thermal import (
    PhysicsInformedBatteryThermalModel,
)

# Compatibility aliases
BatteryThermalState = compute_step_battery_update
BatteryDegradationModel = PhysicsInformedBatteryThermalModel

__all__ = [
    "compute_step_battery_update",
    "forecast_battery_profile",
    "estimate_mission_energy_cost",
    "BatteryThermalState",
    "BatteryDegradationModel",
    "PhysicsInformedBatteryThermalModel",
]
