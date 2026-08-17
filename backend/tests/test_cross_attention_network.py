"""Tests for ConstellationCrossAttentionNet and CrossAttentionPredictor."""

import pytest
import numpy as np
import torch

from app.intelligence.cross_attention_network import (
    ConstellationCrossAttentionNet,
    CrossAttentionPredictor,
    get_cross_attention_predictor,
    SATELLITE_FEATURE_NAMES,
    MISSION_FEATURE_NAMES,
)


def test_cross_attention_forward_pass():
    model = ConstellationCrossAttentionNet(
        sat_dim=len(SATELLITE_FEATURE_NAMES),
        mis_dim=len(MISSION_FEATURE_NAMES),
        d_token=32,
        num_heads=4,
    )
    model.eval()

    batch_size = 3
    sat_x = torch.rand(batch_size, len(SATELLITE_FEATURE_NAMES))
    mis_x = torch.rand(batch_size, len(MISSION_FEATURE_NAMES))

    scores, win_logits, phys, attn = model(sat_x, mis_x, return_attention=True)

    assert scores.shape == (batch_size,)
    assert win_logits.shape == (batch_size,)
    assert phys.shape == (batch_size, 2)
    assert attn.shape == (batch_size, len(SATELLITE_FEATURE_NAMES), len(MISSION_FEATURE_NAMES))


def test_cross_attention_predictor_inference():
    predictor = get_cross_attention_predictor()

    sat_feat = np.array([0.8, 0.85, 0.72, 0.05, 1.0, 0.88, 1.0, 0.65, 0.03, 0.50], dtype=np.float32)
    mis_feat = np.array([0.8, 0.65, 0.50, 0.30, 0.64, 0.62, 0.10, 1.0], dtype=np.float32)

    res = predictor.predict(
        sat_features=sat_feat,
        mis_features=mis_feat,
        satellite_id="SAT-01",
        mission_id="M-TEST-01",
    )

    assert res.satellite_id == "SAT-01"
    assert res.mission_id == "M-TEST-01"
    assert res.predictions.valuation_score >= 0.0
    assert 0.0 <= res.predictions.win_probability <= 1.0
    assert res.predictions.estimated_latency_s >= 0.0
    assert res.predictions.estimated_energy_wh >= 0.0
    assert len(res.attention_matrix) == len(SATELLITE_FEATURE_NAMES)
    assert len(res.attention_matrix[0]) == len(MISSION_FEATURE_NAMES)
    assert len(res.top_attended_features) > 0
    assert res.inference_time_ms < 50.0  # Fast sub-50ms inference
