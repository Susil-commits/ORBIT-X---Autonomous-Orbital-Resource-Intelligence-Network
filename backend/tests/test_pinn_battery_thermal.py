"""Tests for High-Fidelity Physics ODE Battery and Thermal Dynamics."""

import pytest
from app.intelligence.pinn_battery_thermal import (
    ThermalPhysicsSimulator,
    get_thermal_physics_simulator,
    get_pinn_model,
)
from app.core.schemas import PINNBatteryThermalRequest


def test_thermal_physics_step():
    sim = ThermalPhysicsSimulator()

    # Step in sunlight with payload active
    soc, temp, p_solar, q_rad, deg, dq = sim.step_physics(
        soc=0.85,
        temp_c=22.0,
        is_sunlit=True,
        payload_active=True,
        solar_flux_w_m2=1361.0,
        dt_s=30.0,
    )

    assert 0.0 <= soc <= 1.0
    assert temp > -100.0 and temp < 150.0
    assert p_solar > 0.0
    assert q_rad > 0.0
    assert deg >= 0.0


def test_thermal_trajectory_simulation():
    sim = get_thermal_physics_simulator()
    req = PINNBatteryThermalRequest(
        initial_soc=0.85,
        battery_temp_c=20.0,
        payload_active=True,
        is_sunlit=True,
        duration_minutes=45.0,
        time_step_s=30.0,
    )

    res = sim.simulate_trajectory(req)

    assert res.duration_minutes == 45.0
    assert 0.0 <= res.min_projected_soc <= 1.0
    assert 0.0 <= res.final_soc <= 1.0
    assert len(res.trajectory) == int((45.0 * 60.0) / 30.0) + 1
    assert 0.75 <= res.confidence_score <= 1.0
    assert res.physics_residual_norm < 0.05

    # Test alias compatibility
    pinn_alias = get_pinn_model()
    res_alias = pinn_alias.simulate_trajectory(req)
    assert res_alias.final_soc == res.final_soc
