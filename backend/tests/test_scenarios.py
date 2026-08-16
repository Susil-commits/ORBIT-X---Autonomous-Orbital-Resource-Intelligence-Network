"""Tests for Space Scenario Director & Interactive Target Dispatch."""

from app.core.schemas import ScenarioType, TargetDispatchRequest, SensorType
from app.simulation.simulator import ConstellationSimulator


def test_scenario_director_lifecycle():
    sim = ConstellationSimulator()

    # 1. Trigger Solar Storm
    sim.trigger_scenario(ScenarioType.SOLAR_STORM)
    assert sim.active_scenario.is_active is True
    assert sim.active_scenario.scenario_type == ScenarioType.SOLAR_STORM
    assert sim.active_scenario.severity == "CRITICAL"
    assert len(sim.active_scenario.ai_actions_taken) > 0

    # Step simulation under solar storm
    tick = sim.step(dt_seconds=1.0)
    assert tick.active_scenario.is_active is True
    assert tick.metrics_summary["sim_speed"] == "5.0x"

    # 2. Trigger Ground Blackout
    sim.trigger_scenario(ScenarioType.GROUND_BLACKOUT)
    assert sim.active_scenario.scenario_type == ScenarioType.GROUND_BLACKOUT
    svalbard = next(gs for gs in sim.ground_stations if gs.id == "GS-SVALBARD")
    assert svalbard.is_active is False

    # 3. Reset scenario
    sim.reset_scenario()
    assert sim.active_scenario.is_active is False
    assert sim.active_scenario.scenario_type == ScenarioType.NOMINAL
    assert svalbard.is_active is True


def test_custom_target_dispatch():
    sim = ConstellationSimulator()
    initial_count = len(sim.pending_missions)

    req = TargetDispatchRequest(
        name="Gibraltar Strait Reconnaissance",
        lat=36.1408,
        lon=-5.3536,
        priority=5,
        sensor_type=SensorType.SAR_RADAR,
        data_size_gb=18.0,
        deadline_offset_s=1800.0,
    )
    m = sim.dispatch_custom_target(req)

    assert m.id.startswith("MIS-DISPATCH-")
    assert "Gibraltar" in m.name
    assert m.priority == 5
    assert len(sim.pending_missions) == initial_count + 1
