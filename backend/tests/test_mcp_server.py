"""Unit tests for Model Context Protocol (MCP) tool execution."""

import pytest
import json
from app.mcp_server.server import (
    get_constellation_status,
    explain_mission_assignment,
    ask_mission_history,
    preview_satellite_bid,
    trigger_scenario,
)


def test_mcp_get_constellation_status():
    """Validates get_constellation_status returns valid JSON with satellites."""
    res_str = get_constellation_status()
    data = json.loads(res_str)
    
    assert "satellite_count" in data
    assert data["satellite_count"] >= 12
    assert "satellites" in data


def test_mcp_preview_satellite_bid():
    """Validates preview_satellite_bid returns neural score and TreeSHAP explanation."""
    res_str = preview_satellite_bid("SAT-01", mission_priority=5, max_elevation_deg=80.0)
    data = json.loads(res_str)
    
    assert data["satellite_id"] == "SAT-01"
    assert "predicted_bid_score" in data
    assert "explanation" in data
    assert data["explanation"]["is_distilled"] is True


def test_mcp_ask_mission_history():
    """Validates ask_mission_history tool returns grounded answer."""
    res_str = ask_mission_history("What happened during the thermal anomaly?")
    data = json.loads(res_str)
    
    assert "answer" in data
    assert "grounded" in data


def test_mcp_trigger_scenario():
    """Validates trigger_scenario tool injects scenario."""
    res_str = trigger_scenario("SOLAR_STORM")
    data = json.loads(res_str)
    
    assert data["status"] == "SCENARIO_INJECTED"
    assert "Geomagnetic Storm" in data["scenario"] or "CME" in data["scenario"]
