"""FastAPI Router for Mission Intake & Explainability Inspection."""

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.core.schemas import MissionRequest, DecisionExplanation, TargetDispatchRequest
from app.simulation.simulator import get_simulator
from app.simulation.scenarios import generate_random_mission


router = APIRouter(prefix="/api/missions", tags=["Missions"])


from app.core.redis_client import redis_manager

@router.get("", response_model=List[MissionRequest])
async def list_missions():
    """Lists all pending, active, and recent completed missions."""
    sim = get_simulator()
    missions = sim.pending_missions + sim.active_missions + sim.completed_missions[-15:]
    return missions


@router.post("", response_model=MissionRequest)
async def create_mission(mission: MissionRequest):
    """Submits a new mission request with distributed lock coordination and state caching."""
    async with redis_manager.distributed_lock(f"mission:{mission.id}", timeout_s=3.0, lease_s=10.0):
        sim = get_simulator()
        sim.add_mission(mission)
        await redis_manager.cache_mission_state(mission.id, mission.model_dump(), ttl_s=600)
    return mission


@router.post("/random", response_model=MissionRequest)
async def create_random_mission():
    """Spawns a new randomized observation target with distributed locking."""
    sim = get_simulator()
    m_count = len(sim.pending_missions) + len(sim.completed_missions) + 1
    m = generate_random_mission(sim.sim_time_s, m_count)
    async with redis_manager.distributed_lock(f"mission:{m.id}", timeout_s=3.0, lease_s=10.0):
        sim.add_mission(m)
        await redis_manager.cache_mission_state(m.id, m.model_dump(), ttl_s=600)
    return m


@router.post("/dispatch", response_model=MissionRequest)
async def dispatch_target(req: TargetDispatchRequest):
    """Spawns a custom point-and-click observation target and triggers optimization with locking."""
    sim = get_simulator()
    mission = sim.dispatch_custom_target(req)
    if mission:
        async with redis_manager.distributed_lock(f"mission:{mission.id}", timeout_s=3.0, lease_s=10.0):
            await redis_manager.cache_mission_state(mission.id, mission.model_dump(), ttl_s=600)
    return mission


@router.get("/explain/{mission_id}", response_model=DecisionExplanation)
async def get_mission_explanation_alias(mission_id: str):
    """Alias route for explainability (matches frontend path /api/missions/explain/{mission_id})."""
    sim = get_simulator()
    for exp in sim.recent_explanations:
        if exp.mission_id == mission_id:
            return exp
    raise HTTPException(status_code=404, detail=f"Explanation for mission {mission_id} not found")


@router.get("/{mission_id}/explanation", response_model=DecisionExplanation)
async def get_mission_explanation(mission_id: str):
    """Retrieves detailed explainability reasoning and candidate evaluations for a mission."""
    sim = get_simulator()
    for exp in sim.recent_explanations:
        if exp.mission_id == mission_id:
            return exp
    raise HTTPException(status_code=404, detail=f"Explanation for mission {mission_id} not found")
