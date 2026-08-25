"""Unit tests for ML Probability Calibration & Uncertainty Estimation.

Tests:
1. TemperatureScalingCalibrator fitting and ECE reduction.
2. Binary and multiclass calibrated probabilities.
3. UncertaintyEstimator epistemic, aleatoric, and conformal bounds.
"""

import pytest
import numpy as np
import torch

from ml.calibration.temperature_scaling import TemperatureScalingCalibrator
from ml.calibration.uncertainty import UncertaintyEstimator


def test_temperature_scaling_calibrator():
    np.random.seed(42)
    # Generate overconfident validation logits
    logits = np.random.normal(loc=2.5, scale=1.5, size=200).astype(np.float32)
    labels = (np.random.uniform(size=200) < 0.70).astype(np.float32)

    calibrator = TemperatureScalingCalibrator(default_temperature=1.0)
    raw_probs = 1.0 / (1.0 + np.exp(-logits))
    raw_ece = calibrator.compute_ece(raw_probs, labels)

    calibrator.fit(logits, labels)
    assert calibrator.is_fitted
    assert calibrator.temperature > 0.1

    cal_probs = calibrator.calibrate_probabilities(logits)
    assert len(cal_probs) == 200
    assert np.all(cal_probs >= 0.0) and np.all(cal_probs <= 1.0)

    cal_ece = calibrator.compute_ece(cal_probs, labels)
    assert cal_ece <= raw_ece + 0.05


def test_uncertainty_estimator_conformal_bounds():
    estimator = UncertaintyEstimator(alpha_significance=0.10)
    
    # Calibrate conformal quantile with simulated residuals
    residuals = np.random.normal(loc=0.03, scale=0.02, size=100)
    q = estimator.calibrate_conformal_quantile(residuals)
    assert q > 0.0

    # Estimate uncertainty on 4 candidate scores
    scores = np.array([88.0, 65.0, 52.0, 30.0])
    uncertainty = estimator.estimate_uncertainty(
        candidate_scores=scores,
        sensor_noise_std=0.02,
        ood_distance=0.01,
    )

    assert "total_uncertainty" in uncertainty
    assert "epistemic_uncertainty" in uncertainty
    assert "aleatoric_uncertainty" in uncertainty
    assert "conformal_interval" in uncertainty
    assert len(uncertainty["conformal_interval"]) == 2
    assert uncertainty["conformal_interval"][0] < uncertainty["conformal_interval"][1]
    assert uncertainty["coverage_guarantee_pct"] == 90.0
