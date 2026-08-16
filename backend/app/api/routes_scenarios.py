"""FastAPI Router for Extreme Space Scenarios & Scenario Director."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.schemas import ScenarioType, ScenarioState
from app.simulation.simulator import get_simulator

router = APIRouter(prefix="/api/scenarios", tags=["Scenario Director"])


class TriggerScenarioRequest(BaseModel):
    scenario_type: ScenarioType


@router.get("/status", response_model=ScenarioState)
async def get_scenario_status():
    """Fetches active scenario state, AI actions taken, and telemetry impacts."""
    sim = get_simulator()
    return sim.active_scenario


@router.post("/trigger", response_model=ScenarioState)
async def trigger_scenario(req: TriggerScenarioRequest):
    """Triggers an extreme space scenario and engages autonomous recovery AI."""
    sim = get_simulator()
    sim.trigger_scenario(req.scenario_type)
    return sim.active_scenario


@router.post("/reset", response_model=ScenarioState)
async def reset_scenario():
    """Resets the active scenario and restores nominal constellation baseline."""
    sim = get_simulator()
    sim.reset_scenario()
    return sim.active_scenario
