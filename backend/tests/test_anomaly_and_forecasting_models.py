"""Unit tests for Anomaly Detection and Forecasting Models.

Tests:
1. IsolationForestAnomalyDetector nominal bootstrap, anomaly scoring, and risk penalty injection.
2. MahalanobisAnomalyDetector multivariate statistical outlier scoring.
3. LookaheadBatteryForecaster orbital solar & thermal trajectory simulation.
4. LinearDecayForecaster baseline extrapolation.
"""

import pytest
import numpy as np

from ml.models.anomaly.isolation_forest import IsolationForestAnomalyDetector
from ml.models.anomaly.mahalanobis import MahalanobisAnomalyDetector
from ml.models.forecasting.battery_forecaster import LookaheadBatteryForecaster
from ml.models.forecasting.linear_forecaster import LinearDecayForecaster


def test_isolation_forest_anomaly_detector():
    detector = IsolationForestAnomalyDetector()
    assert detector.is_fitted

    # Nominal vector: [soc=0.85, temp=22.0, volt=28.0, lat=45.0, snr=18.0, mem=35.0, pwr=35.0]
    nominal_vec = np.array([0.85, 22.0, 28.0, 45.0, 18.0, 35.0, 35.0])
    res_nominal = detector.score_telemetry(nominal_vec)
    assert res_nominal["severity"] in ["NOMINAL", "MEDIUM"]

    # Severe degraded anomalous vector
    anomalous_vec = np.array([0.05, 78.0, 16.0, 850.0, 2.0, 99.0, 150.0])
    res_anomalous = detector.score_telemetry(anomalous_vec)
    assert res_anomalous["is_anomaly"] is True
    assert res_anomalous["risk_penalty"] > 0.0


def test_mahalanobis_anomaly_detector():
    detector = MahalanobisAnomalyDetector()
    assert detector.is_fitted

    nominal_vec = np.zeros(7)
    res = detector.score_telemetry(nominal_vec)
    assert "mahalanobis_distance" in res
    assert res["anomaly_score"] >= 0.0


def test_battery_lookahead_forecaster():
    forecaster = LookaheadBatteryForecaster()
    traj = forecaster.forecast_trajectory(
        current_soc=0.80,
        current_temp_c=22.0,
        horizon_steps=30,
        step_duration_s=60.0,
    )
    assert "soc_profile" in traj
    assert len(traj["soc_profile"]) == 31
    assert "is_thermal_power_safe" in traj
    assert traj["min_projected_soc"] >= 0.05


def test_linear_decay_forecaster():
    forecaster = LinearDecayForecaster(default_decay_rate_per_min=0.005)
    traj = forecaster.forecast_trajectory(
        current_soc=0.90,
        horizon_steps=20,
        step_duration_s=60.0,
    )
    assert len(traj["soc_profile"]) == 21
    assert traj["min_projected_soc"] <= 0.90
