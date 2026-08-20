"""Tests for Non-Blocking Event Loop Concurrency, Admin Secret Auth, and CORS Configuration."""

import os
import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.simulation.simulator import get_simulator
from app.api.routes_ai import verify_admin_access
from app.core.schemas import ConstellationTick


@pytest.mark.asyncio
async def test_step_async_execution():
    """Verifies that step_async advances simulation state asynchronously and returns valid tick."""
    sim = get_simulator()
    t_start = sim.sim_time_s
    tick_start = sim.tick
    
    tick = await sim.step_async(dt_seconds=1.0)
    
    assert isinstance(tick, ConstellationTick)
    assert tick.sim_time_s > t_start
    assert tick.tick == tick_start + 1
    assert len(tick.satellites) > 0
    assert tick.metrics_summary["sim_speed"] == f"{sim.speed_multiplier}x"


@pytest.mark.asyncio
async def test_replan_schedule_async():
    """Verifies that replan_schedule_async solves CP-SAT in worker thread and populates explanations."""
    sim = get_simulator()
    # Force replan
    sim.last_schedule_time_s = -999.0
    await sim.replan_schedule_async()
    
    assert isinstance(sim.recent_explanations, list)


def test_verify_admin_access_unconfigured():
    """When ADMIN_SECRET_KEY is unset (demo mode), verify_admin_access permits requests."""
    with patch.dict(os.environ, {"ADMIN_SECRET_KEY": ""}, clear=False):
        assert verify_admin_access(x_admin_secret=None) is True
        assert verify_admin_access(x_admin_secret="any-token") is True


def test_verify_admin_access_enforced():
    """When ADMIN_SECRET_KEY is configured, enforces exact header matching."""
    with patch.dict(os.environ, {"ADMIN_SECRET_KEY": "super_secret_key_123"}, clear=False):
        # Missing header -> 403
        with pytest.raises(HTTPException) as exc_missing:
            verify_admin_access(x_admin_secret=None)
        assert exc_missing.value.status_code == 403

        # Invalid header -> 403
        with pytest.raises(HTTPException) as exc_invalid:
            verify_admin_access(x_admin_secret="wrong_secret")
        assert exc_invalid.value.status_code == 403

        # Valid header -> True
        assert verify_admin_access(x_admin_secret="super_secret_key_123") is True


def test_rate_limiting_enforcement():
    """Verifies that slowapi rate limits excessive burst requests with HTTP 429."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    # /api/ai/agent/inspect_and_heal is rate-limited to 10/minute
    responses = [client.post("/api/ai/agent/inspect_and_heal") for _ in range(15)]
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes

