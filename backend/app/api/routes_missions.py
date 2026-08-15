"""FastAPI Router for Mission Intake & Explainability Inspection."""

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.core.schemas import MissionRequest, DecisionExplanation
from app.simulation.simulator import get_simulator
from app.simulation.scenarios import generate_random_mission

router = APIRouter(prefix="/api/missions", tags=["Missions"])


@router.get("", response_model=List[MissionRequest])
async def list_missions():
    """Lists all pending, active, and recent completed missions."""
    sim = get_simulator()
    return sim.pending_missions + sim.active_missions + sim.completed_missions[-15:]


@router.post("", response_model=MissionRequest)
async def create_mission(mission: MissionRequest):
    """Submits a new mission request into the constellation intake."""
    sim = get_simulator()
    sim.add_mission(mission)
    return mission


@router.post("/random", response_model=MissionRequest)
async def create_random_mission():
    """Spawns a new randomized observation target and triggers optimization."""
    sim = get_simulator()
    m_count = len(sim.pending_missions) + len(sim.completed_missions) + 1
    m = generate_random_mission(sim.sim_time_s, m_count)
    sim.add_mission(m)
    return m


@router.get("/{mission_id}/explanation", response_model=DecisionExplanation)
async def get_mission_explanation(mission_id: str):
    """Retrieves detailed explainability reasoning and candidate evaluations for a mission."""
    sim = get_simulator()
    for exp in sim.recent_explanations:
        if exp.mission_id == mission_id:
            return exp
    raise HTTPException(status_code=404, detail=f"Explanation for mission {mission_id} not found")
