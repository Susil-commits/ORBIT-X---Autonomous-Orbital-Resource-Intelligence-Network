"""FastAPI Router for ORBIT-X Neural Intelligence, TreeSHAP Explainability & RAG QA."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from app.core.schemas import (
    MissionQARequest,
    MissionQAResponse,
    NeuralBidPreviewRequest,
    NeuralBidPreviewResponse,
    FlightDirectorCommentary,
    AgentHealingAction,
    EvalRunSummary,
)
from app.simulation.simulator import get_simulator
from app.intelligence.mission_qa import get_mission_qa_engine
from app.intelligence.shap_explainer import get_shap_explainer
from app.intelligence.multi_agent import MultiAgentCoordinator
from app.intelligence.agent_loop import get_self_healing_agent
from app.intelligence.commentary_generator import get_commentary_generator

router = APIRouter(prefix="/api/ai", tags=["AI & Intelligence"])


@router.post("/mission/ask", response_model=MissionQAResponse)
async def ask_mission_decision_history(req: MissionQARequest):
    """
    RAG QA over ORBIT-X logged mission assignments, solver rationale, and anomaly telemetry.
    Answers are grounded strictly in verifiable operational logs with source citations.
    """
    qa = get_mission_qa_engine()
    return qa.ask(req.query, top_k=req.top_k)


@router.post("/preview_bid", response_model=NeuralBidPreviewResponse)
async def preview_neural_satellite_bid(req: NeuralBidPreviewRequest):
    """
    Executes sub-millisecond neural network bid valuation using the PyTorch BidValueMLP
    and returns exact TreeSHAP local feature importance explanations.
    """
    sim = get_simulator()
    sat = next((s for s in sim.satellites if s.id == req.satellite_id), None)
    if not sat:
        raise HTTPException(status_code=404, detail=f"Satellite '{req.satellite_id}' not found.")
        
    return MultiAgentCoordinator.preview_neural_bid(
        satellite=sat,
        priority=req.priority,
        max_elevation_deg=req.max_elevation_deg,
        slew_penalty=req.slew_penalty,
    )


@router.get("/shap/status")
async def get_shap_explainer_status():
    """
    Returns TreeSHAP surrogate status, expected base value, active neural network
    model hash, and drift detection flag.
    """
    explainer = get_shap_explainer()
    drift_detected = explainer.check_drift()
    return {
        "is_ready": explainer.is_ready,
        "is_distilled": True,
        "base_value": explainer.base_value,
        "trained_nn_hash": explainer.trained_nn_hash,
        "active_nn_hash": explainer.predictor.model_hash,
        "drift_detected": drift_detected,
    }


@router.post("/agent/inspect_and_heal", response_model=Dict[str, Any])
async def trigger_agent_self_healing():
    """
    Runs the self-healing agent loop: checks drift and eval regressions,
    and automatically triggers surrogate re-distillation if needed.
    """
    agent = get_self_healing_agent()
    status, action = agent.inspect_and_heal()
    return {
        "status": status,
        "action": action.model_dump() if action else None,
    }


@router.get("/commentary/sample", response_model=FlightDirectorCommentary)
async def get_sample_commentary():
    """Returns sample tactical Flight Director commentary."""
    cg = get_commentary_generator()
    sim = get_simulator()
    sat = sim.satellites[0] if sim.satellites else None
    return cg.generate_commentary(
        "CONSTELLATION_STATE",
        sim.sim_time_s,
        {"satellite_id": sat.id if sat else "SAT-01", "status": "NOMINAL"},
    )
