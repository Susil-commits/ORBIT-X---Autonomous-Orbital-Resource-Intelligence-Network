"""Tests for Physics-Informed Neural Network (PINN) Battery and Thermal Dynamics."""

import pytest
from app.intelligence.pinn_battery_thermal import (
    PhysicsInformedBatteryThermalModel,
    get_pinn_model,
)
from app.core.schemas import PINNBatteryThermalRequest


def test_pinn_physics_step():
    pinn = PhysicsInformedBatteryThermalModel()

    # Step in sunlight with payload active
    soc, temp, p_solar, q_rad, deg, dq = pinn.step_physics(
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


def test_pinn_trajectory_simulation():
    pinn = get_pinn_model()
    req = PINNBatteryThermalRequest(
        initial_soc=0.85,
        battery_temp_c=20.0,
        payload_active=True,
        is_sunlit=True,
        duration_minutes=45.0,
        time_step_s=30.0,
    )

    res = pinn.simulate_trajectory(req)

    assert res.duration_minutes == 45.0
    assert 0.0 <= res.min_projected_soc <= 1.0
    assert 0.0 <= res.final_soc <= 1.0
    assert len(res.trajectory) == int((45.0 * 60.0) / 30.0) + 1
    assert res.confidence_score > 0.90
    assert res.physics_residual_norm < 0.1
