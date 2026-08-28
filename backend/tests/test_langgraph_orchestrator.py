"""Unit Tests for LangGraph StateGraph Autonomous Agent Orchestrator."""

import pytest
from agents.agent_loop.orchestrator import AgentOrchestrator, AgentState
from agents.tools.mcp_tools import get_ai_tools_registry


def test_langgraph_orchestrator_initialization():
    """Validates LangGraph StateGraph compilation and initialization."""
    orchestrator = AgentOrchestrator()
    assert orchestrator.graph is not None
    assert orchestrator.tools is not None


def test_langgraph_orchestrator_risk_audit_branch():
    """Validates execution trace for queries requiring deep risk audit."""
    orchestrator = AgentOrchestrator()
    query = "Evaluate thermal collision risk and re-plan Mission M-204"
    result = orchestrator.process_query(query)

    assert result["status"] == "VERIFIED_TRUST_ENVELOPE"
    assert result["confidence_score"] >= 0.90
    assert len(result["evidence"]) >= 3
    assert result["recommendation"] is not None
    assert "SAT-01" in result["recommendation"]
    assert result["lineage"] is not None
    assert result["human_governance_actions"] == ["APPROVE", "REJECT", "INVESTIGATE"]

    # Verify execution trace contains anomaly detection node (conditional edge)
    trace_actions = [step["action"] for step in result["execution_trace"]]
    assert "INTENT_CLASSIFICATION" in trace_actions
    assert "RETRIEVE_METADATA" in trace_actions
    assert "SEARCH_TELEMETRY" in trace_actions
    assert "RUN_ANOMALY_DETECTION" in trace_actions
    assert "RUN_ML_RANKER" in trace_actions
    assert "CALCULATE_SHAP_XAI" in trace_actions
    assert "VERIFY_HARD_CONSTRAINTS_CPSAT" in trace_actions
    assert "TRACE_DATA_LINEAGE" in trace_actions
    assert "PACKAGE_TRUST_ENVELOPE" in trace_actions


def test_langgraph_orchestrator_general_operational_query():
    """Validates execution for standard general queries."""
    orchestrator = AgentOrchestrator()
    query = "What is the optimal satellite assignment for optical survey?"
    result = orchestrator.process_query(query)

    assert result["status"] == "VERIFIED_TRUST_ENVELOPE"
    assert result["confidence_score"] >= 0.90
    assert len(result["execution_trace"]) >= 8

    trace_actions = [step["action"] for step in result["execution_trace"]]
    assert "INTENT_CLASSIFICATION" in trace_actions
    assert "RUN_ML_RANKER" in trace_actions
    assert "VERIFY_HARD_CONSTRAINTS_CPSAT" in trace_actions
