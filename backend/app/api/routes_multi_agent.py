"""FastAPI Router for Multi-Agent Auction & Bidding Inspector."""

import sys
from pathlib import Path
from fastapi import APIRouter
from typing import List, Dict

# Ensure project root is in sys.path
_backend_dir = Path(__file__).resolve().parent.parent.parent
_root_dir = _backend_dir.parent
for _p in [str(_backend_dir), str(_root_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


from app.core.schemas import AccessWindow, WindowType
from app.simulation.simulator import get_simulator
from app.physics.access_model import find_access_windows
from benchmarks.legacy.multi_agent import MultiAgentCoordinator, AuctionResult

router = APIRouter(prefix="/api/multi-agent", tags=["Multi-Agent"])


@router.get("/auction", response_model=List[AuctionResult])
async def get_auction_ledger():
    """Runs and returns the latest multi-agent bidding and conflict resolution ledger."""
    sim = get_simulator()
    
    # Compute candidate windows
    candidate_windows_map: Dict[str, Dict[str, List[AccessWindow]]] = {}
    for m in sim.pending_missions:
        candidate_windows_map[m.id] = {}
        for sat in sim.satellites:
            wins = find_access_windows(
                satellite_id=sat.id,
                keplerian=sat.keplerian,
                target_or_station_id=m.id,
                location=m.target_location,
                window_type=WindowType.IMAGING,
                start_time_s=sim.sim_time_s,
                horizon_s=3600.0,
            )
            candidate_windows_map[m.id][sat.id] = wins
            
    results = MultiAgentCoordinator.run_auction(
        missions=sim.pending_missions,
        satellites=sim.satellites,
        candidate_windows_map=candidate_windows_map,
    )
    return results


@router.post("/swarm")
async def run_multi_agent_swarm_arbitration():
    """
    Executes collaborative LangGraph Multi-Agent Constellation Swarm deliberation
    across Thermal, ISL Mesh, Astrodynamics, and Flight Director specialist agents.
    """
    from agents.swarm.multi_agent_swarm import get_multi_agent_swarm_coordinator
    coordinator = get_multi_agent_swarm_coordinator()
    return coordinator.run_swarm_arbitration()

