"""ORBIT-X Simulation & Evaluation Environment Package.

Provides an operational simulation testbed for the decision intelligence platform:
- Telemetry Generation
- Orbital SGP4 Mechanics & TLE Pipelines
- ISL Laser Mesh Topologies
- Thermal / Battery Physical Constraints
- Extreme Scenario Injection for Decision Stress-Testing
"""

from simulation.telemetry.generator import TelemetryStreamGenerator
from simulation.physics.orbit_propagator import (
    solve_kepler,
    propagate_orbit,
    create_synthetic_constellation,
    load_real_constellation,
    create_initial_constellation,
    compute_orbital_period_minutes,
    generate_walker_delta_constellation,
    load_celestrak_constellation,
    TLEPipelineManager,
)
from simulation.network.isl_mesh import (
    is_line_of_sight_occluded,
    build_isl_mesh,
    ISLMeshNetwork,
    ISLLink,
    ISLRoute,
    MeshRoute,
    ISLMeshState,
)
from simulation.constraints.battery_dynamics import (
    compute_step_battery_update,
    forecast_battery_profile,
    estimate_mission_energy_cost,
    BatteryThermalState,
    BatteryDegradationModel,
    PhysicsInformedBatteryThermalModel,
)
from simulation.scenarios.extreme_scenarios import (
    get_default_missions,
    generate_random_mission,
    ScenarioType,
    ScenarioState,
    ScenarioDirector,
    ScenarioEvent,
    get_scenario_director,
)

# Backward-compatible re-exports
from backend.app.simulation.simulator import (
    ConstellationSimulator,
    get_simulator,
)
from backend.app.core.schemas import ConstellationTick

# Compatibility alias
ConstellationState = ConstellationTick

__all__ = [
    "TelemetryStreamGenerator",
    "solve_kepler",
    "propagate_orbit",
    "create_synthetic_constellation",
    "load_real_constellation",
    "create_initial_constellation",
    "compute_orbital_period_minutes",
    "generate_walker_delta_constellation",
    "load_celestrak_constellation",
    "TLEPipelineManager",
    "is_line_of_sight_occluded",
    "build_isl_mesh",
    "ISLMeshNetwork",
    "ISLLink",
    "ISLRoute",
    "MeshRoute",
    "ISLMeshState",
    "compute_step_battery_update",
    "forecast_battery_profile",
    "estimate_mission_energy_cost",
    "BatteryThermalState",
    "BatteryDegradationModel",
    "PhysicsInformedBatteryThermalModel",
    "get_default_missions",
    "generate_random_mission",
    "ScenarioType",
    "ScenarioState",
    "ScenarioDirector",
    "ScenarioEvent",
    "get_scenario_director",
    "ConstellationSimulator",
    "ConstellationTick",
    "ConstellationState",
    "get_simulator",
]
