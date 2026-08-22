"""Simulation Extreme Failure Scenarios Director.

Provides 10 extreme failure injection scenarios (Solar Storm, Debris Conjunction,
Ground Blackout, Thermal Runaway, Cyber Spoofing) to evaluate AI decision resilience.
"""

from backend.app.simulation.scenarios import (
    get_default_missions,
    generate_random_mission,
)
from backend.app.core.schemas import (
    ScenarioType,
    ScenarioState,
)

# Compatibility aliases
ScenarioDirector = get_default_missions
ScenarioEvent = ScenarioState
get_scenario_director = get_default_missions

__all__ = [
    "get_default_missions",
    "generate_random_mission",
    "ScenarioType",
    "ScenarioState",
    "ScenarioDirector",
    "ScenarioEvent",
    "get_scenario_director",
]
