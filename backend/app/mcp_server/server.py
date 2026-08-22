"""Model Context Protocol (MCP) Server for ORBIT-X.

Exposes ORBIT-X constellation telemetry, decision explainability trails,
neural bid previews, decision history RAG, and scenario injection as official MCP tools.
Usable directly from Claude Desktop, Claude Code, Antigravity, or any MCP client.
"""

import json
from typing import Dict, Any, Optional
from mcp.server.mcpserver import MCPServer

from app.core.schemas import ScenarioType
from app.simulation.simulator import get_simulator
from app.intelligence.shap_explainer import get_shap_explainer
from app.intelligence.bid_value_network import extract_features, get_bid_value_predictor
from app.intelligence.mission_qa import get_mission_qa_engine
from app.intelligence.multi_agent import MultiAgentCoordinator

# Initialize MCP Server
mcp = MCPServer("ORBIT-X Orbital Intelligence Server")


@mcp.tool()
def get_constellation_status() -> str:
    """
    Returns the real-time operational status of the ORBIT-X constellation,
    including satellite positions, battery State-of-Charge, health status,
    active missions, ISL mesh health, and collision alerts.
    """
    sim = get_simulator()
    sat_summary = [
        {
            "id": s.id,
            "name": s.name,
            "data_source": s.data_source,
            "lat": round(s.geodetic.lat, 2),
            "lon": round(s.geodetic.lon, 2),
            "alt_km": round(s.geodetic.alt, 1),
            "battery_soc_pct": round(s.battery.soc * 100, 1),
            "health": s.health_status.value,
            "active_mission": s.active_mission_id,
        }
        for s in sim.satellites
    ]
    
    status_payload = {
        "sim_time_s": sim.sim_time_s,
        "tick": sim.tick,
        "satellite_count": len(sim.satellites),
        "pending_missions_count": len(sim.pending_missions),
        "active_missions_count": len(sim.active_missions),
        "completed_missions_count": len(sim.completed_missions),
        "active_collision_alerts": len(sim.collision_alerts),
        "active_scenario": sim.active_scenario.title,
        "satellites": sat_summary,
    }
    return json.dumps(status_payload, indent=2)


@mcp.tool()
def explain_mission_assignment(mission_id: str) -> str:
    """
    Retrieves the decision explainability trail for a specific mission,
    detailing why a particular satellite was assigned and why alternative candidates were rejected.
    """
    sim = get_simulator()
    explanation = next((e for e in sim.recent_explanations if e.mission_id == mission_id), None)
    
    if not explanation:
        return json.dumps({
            "error": f"No recent explanation found for mission '{mission_id}'.",
            "available_mission_ids": [e.mission_id for e in sim.recent_explanations],
        }, indent=2)
        
    return json.dumps(explanation.model_dump(), indent=2)


@mcp.tool()
def ask_mission_history(query: str) -> str:
    """
    Runs a grounded RAG query over ORBIT-X's decision and telemetry history.
    Provides verifiable citations and strictly refuses to answer unsupported questions.
    """
    qa = get_mission_qa_engine()
    res = qa.ask(query)
    return json.dumps(res.model_dump(), indent=2)


@mcp.tool()
def preview_satellite_bid(
    satellite_id: str,
    mission_priority: int = 4,
    max_elevation_deg: float = 65.0,
    slew_penalty: float = 0.0,
    deadline_slack_s: float = 1800.0,
) -> str:
    """
    Executes a sub-millisecond neural network bid valuation preview for a candidate satellite
    using the BidValueMLP model and returns exact TreeSHAP feature attributions.
    """
    sim = get_simulator()
    sat = next((s for s in sim.satellites if s.id == satellite_id), None)
    if not sat:
        return json.dumps({"error": f"Satellite '{satellite_id}' not found."}, indent=2)
        
    preview = MultiAgentCoordinator.preview_neural_bid(
        satellite=sat,
        priority=mission_priority,
        max_elevation_deg=max_elevation_deg,
        slew_penalty=slew_penalty,
        deadline_slack_s=deadline_slack_s,
    )
    return json.dumps(preview.model_dump(), indent=2)


@mcp.tool()
def trigger_scenario(scenario_name: str) -> str:
    """
    Injects an extreme space mission scenario into the live constellation:
    Options: 'SOLAR_STORM', 'DEBRIS_CONJUNCTION', 'GROUND_BLACKOUT', 'DISASTER_SURGE', 'NOMINAL'.
    """
    sim = get_simulator()
    try:
        scen_enum = ScenarioType(scenario_name.upper())
    except ValueError:
        return json.dumps({
            "error": f"Invalid scenario '{scenario_name}'.",
            "valid_scenarios": [s.value for s in ScenarioType],
        }, indent=2)
        
    sim.trigger_scenario(scen_enum)
    return json.dumps({
        "status": "SCENARIO_INJECTED",
        "scenario": sim.active_scenario.title,
        "severity": sim.active_scenario.severity,
        "affected_satellites_count": len(sim.active_scenario.affected_satellite_ids),
    }, indent=2)


@mcp.tool()
def get_dataset_metadata(dataset_name: str) -> str:
    """
    Retrieves semantic metadata catalog details for a specific operational or ML dataset,
    including columns, types, owner, freshness, quality score, and downstream ML models.
    """
    from app.intelligence.context_graph import get_context_graph_engine
    engine = get_context_graph_engine()
    meta = engine.get_dataset_metadata(dataset_name)
    if not meta:
        return json.dumps({"error": f"Dataset '{dataset_name}' not found in catalog."}, indent=2)
    return json.dumps(meta.model_dump(), indent=2)


@mcp.tool()
def get_decision_lineage(mission_id: str) -> str:
    """
    Traverses and returns the full end-to-end Data Lineage Graph for a mission assignment:
    Raw Sensor Telemetry -> Cleaned Dataset -> Feature Table -> ML Prediction -> CP-SAT -> Decision -> Outcome.
    """
    from app.intelligence.context_graph import get_context_graph_engine
    engine = get_context_graph_engine()
    lineage = engine.trace_decision_lineage(mission_id=mission_id)
    return json.dumps(lineage.model_dump(), indent=2)


@mcp.tool()
def check_data_quality() -> str:
    """
    Audits live constellation telemetry against physical limits, checking for missing values,
    sensor degradation, and schema drift.
    """
    from app.intelligence.data_quality_agent import get_data_quality_agent
    sim = get_simulator()
    agent = get_data_quality_agent()
    frames = [s.telemetry for s in sim.satellites]
    report = agent.audit_telemetry_stream(frames)
    return json.dumps(report.model_dump(), indent=2)


@mcp.tool()
def get_model_baselines_report() -> str:
    """
    Returns comparative benchmark metrics across all 7 machine learning models
    (Random, Greedy, Ridge, Random Forest, MLP, Cross-Attention, Hybrid CP-SAT).
    """
    from app.intelligence.baselines import get_baseline_suite
    suite = get_baseline_suite()
    report = suite.run_full_comparison()
    return json.dumps(report.model_dump(), indent=2)


@mcp.tool()
def submit_human_feedback(
    decision_record_id: str,
    feedback_type: str = "APPROVE",
    operator_notes: str = "Operator verified constraint satisfaction.",
) -> str:
    """
    Submits human-in-the-loop operator review (APPROVE, REJECT, INVESTIGATE) for a decision record
    to be logged into the persistent feedback database for continuous AI alignment.
    """
    from app.intelligence.trust_layer import get_trust_layer_engine
    from app.core.schemas import HumanFeedbackRequest
    engine = get_trust_layer_engine()
    res = engine.record_feedback(
        HumanFeedbackRequest(
            decision_record_id=decision_record_id,
            feedback_type=feedback_type,
            operator_notes=operator_notes,
        )
    )
    return json.dumps(res.model_dump(), indent=2)


if __name__ == "__main__":
    mcp.run()

