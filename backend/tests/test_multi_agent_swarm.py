"""Unit tests for LangGraph Multi-Agent Constellation Swarm Coordinator."""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.swarm.multi_agent_swarm import (
    MultiAgentSwarmCoordinator,
    get_multi_agent_swarm_coordinator,
)


def test_multi_agent_swarm_initialization():
    coordinator = get_multi_agent_swarm_coordinator()
    assert coordinator is not None
    assert coordinator.graph is not None


def test_multi_agent_swarm_deliberation_and_consensus():
    coordinator = MultiAgentSwarmCoordinator()
    res = coordinator.run_swarm_arbitration(
        mission_id="M-TEST-01",
        target_lat=40.71,
        target_lon=-74.00,
    )

    assert res["mission_id"] == "M-TEST-01"
    assert res["consensus_status"] == "CONSENSUS_REACHED"
    assert res["decision"]["assigned_satellite_id"] == "SAT-01"

    # Verify thermal agent rejected SAT-03 due to thermal spike
    assert res["thermal_evaluations"]["SAT-03"]["verdict"] == "REJECTED_THERMAL_RISK"
    assert res["thermal_evaluations"]["SAT-01"]["verdict"] == "APPROVED"

    # Verify ISL mesh evaluation
    assert res["isl_evaluations"]["SAT-01"]["verdict"] == "FEASIBLE"
    assert res["isl_evaluations"]["SAT-01"]["hop_count"] == 1

    # Verify Astrodynamics pass evaluation
    assert res["astrodynamics_evaluations"]["SAT-01"]["verdict"] == "OPTIMAL_PASS"

    # Verify deliberation log contains logs from all 4 subagents
    agents_in_log = {entry["agent"] for entry in res["deliberation_log"]}
    assert "ThermalPowerSafetyAgent" in agents_in_log
    assert "ISLMeshRoutingAgent" in agents_in_log
    assert "AstrodynamicsAgent" in agents_in_log
    assert "FlightDirectorOrchestratorAgent" in agents_in_log


def test_multi_agent_swarm_refusal_when_all_disqualified():
    coordinator = MultiAgentSwarmCoordinator()
    bad_candidates = [
        {
            "satellite_id": "SAT-FAIL-1",
            "battery_soc": 0.10,  # Below 20% SoC limit
            "battery_temp_c": 48.0,  # Above 42C thermal limit
            "max_elevation_deg": 10.0,
            "slew_penalty_s": 50.0,
            "isl_peers_available": 0,
            "health_status": "DEGRADED",
        }
    ]

    res = coordinator.run_swarm_arbitration(
        mission_id="M-TEST-FAIL",
        candidates=bad_candidates,
    )

    assert res["consensus_status"] == "REFUSAL_ALL_DISQUALIFIED"
    assert res["decision"]["assigned_satellite_id"] is None
    assert len(res["decision"]["ranked_pool"]) == 0
