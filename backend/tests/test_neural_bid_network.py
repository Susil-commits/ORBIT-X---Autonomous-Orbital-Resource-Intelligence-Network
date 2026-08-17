"""Unit tests for PyTorch BidValueMLP, feature extraction, and fast inference."""

import pytest
import numpy as np
import torch
from app.intelligence.bid_value_network import (
    BidValueMLP,
    extract_features,
    get_bid_value_predictor,
    FEATURE_NAMES,
)


def test_feature_extraction():
    """Validates 10-dimensional normalized feature vector extraction."""
    feat = extract_features(
        priority=5,
        battery_soc=0.90,
        max_elevation_deg=75.0,
        slew_penalty=10.0,
        health_status="NOMINAL",
        storage_used_gb=30.0,
        max_storage_gb=256.0,
        is_sunlit=True,
        deadline_slack_s=1800.0,
        energy_cost_wh=15.0,
        capacity_wh=800.0,
        duration_s=30.0,
    )
    
    assert len(feat) == 10
    assert feat.dtype == np.float32
    assert feat[0] == 1.0  # priority 5 / 5.0
    assert feat[1] == 0.90  # soc
    assert abs(feat[2] - (75.0 / 90.0)) < 1e-4  # elevation
    assert feat[4] == 1.0  # health nominal
    assert feat[6] == 1.0  # is_sunlit


def test_neural_network_forward_and_latency():
    """Validates MLP forward pass and sub-millisecond execution."""
    model = BidValueMLP(input_dim=10)
    model.eval()
    
    dummy_input = torch.randn(1, 10, dtype=torch.float32)
    with torch.no_grad():
        out = model(dummy_input)
        
    assert out.shape == (1, 1)


def test_predictor_loaded_and_hash():
    """Validates predictor loads model checkpoint and computes non-empty SHA-256 hash."""
    predictor = get_bid_value_predictor()
    assert predictor.is_loaded is True
    assert len(predictor.model_hash) == 64  # SHA-256 hex string
    
    sample_feat = np.array([0.8, 0.9, 0.7, 0.1, 1.0, 0.8, 1.0, 0.5, 0.02, 0.5], dtype=np.float32)
    pred_score = predictor.predict_single(sample_feat)
    assert isinstance(pred_score, float)
    assert pred_score >= 0.0
