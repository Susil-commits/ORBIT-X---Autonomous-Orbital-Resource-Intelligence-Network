"""Unit tests for newly added LangGraph, LoRA, and Multi-Agent Swarm API endpoints."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend and project root to sys.path
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
for p in [str(backend_dir), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import app

client = TestClient(app)


def test_api_agent_graph_topology():
    response = client.get("/api/ai/agent/graph")
    assert response.status_code == 200
    data = response.json()
    assert data["graph_name"] == "ORBITX_AgentOrchestrator_StateGraph"
    assert len(data["nodes"]) == 10
    assert len(data["conditional_edges"]) >= 1


def test_api_agent_orchestrate_query():
    response = client.post(
        "/api/ai/agent/orchestrate",
        json={
            "query": "Why is SAT-03 at risk and how should we reassign?",
            "user_id": "flight-director",
            "prefer_verified": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Why is SAT-03 at risk and how should we reassign?"
    assert data["intent"] == "RISK_AUDIT_AND_TASK_REPLANNING"
    assert len(data["execution_steps"]) >= 5
    assert "trust_envelope" in data
    assert data["confidence_score"] > 0.0


def test_api_finetune_lora_trigger():
    response = client.post(
        "/api/ai/finetune/lora",
        json={
            "epochs": 2,
            "learning_rate": 0.001,
            "lora_rank": 8,
            "lora_alpha": 16,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "LORA_TRAINING_INITIALIZED"
    assert data["parameter_reduction_pct"] >= 90.0
    assert "q_proj" in data["adapter_target_modules"]


def test_api_multi_agent_swarm():
    response = client.post("/api/multi-agent/swarm")
    assert response.status_code == 200
    data = response.json()
    assert data["consensus_status"] == "CONSENSUS_REACHED"
    assert "thermal_evaluations" in data
    assert "isl_evaluations" in data
    assert "astrodynamics_evaluations" in data
    assert "deliberation_log" in data
    assert len(data["deliberation_log"]) >= 4
