"""Unit tests for Distilled TreeSHAP explainability, feature attributions & drift detection."""

import pytest
import numpy as np
from app.intelligence.shap_explainer import get_shap_explainer


def test_shap_explainer_ready_and_distilled():
    """Validates that TreeSHAP surrogate explainer is initialized and marked as distilled."""
    explainer = get_shap_explainer()
    assert explainer.is_ready is True
    assert explainer.surrogate_model is not None
    assert explainer.tree_explainer is not None


def test_shap_local_attributions():
    """Validates local TreeSHAP feature attributions on a candidate sample."""
    explainer = get_shap_explainer()
    sample_feat = np.array([1.0, 0.95, 0.85, 0.0, 1.0, 0.9, 1.0, 0.8, 0.02, 0.5], dtype=np.float32)
    
    res = explainer.explain_features(sample_feat)
    
    assert res.is_distilled is True
    assert isinstance(res.predicted_bid_score, float)
    assert isinstance(res.base_value, float)
    assert len(res.feature_attributions) == 10
    
    # Priority should be a positive contributor for priority 5
    prio_attr = next(a for a in res.feature_attributions if a.feature_name == "priority_norm")
    assert prio_attr.contribution_direction == "POSITIVE"


def test_drift_detection():
    """Validates that check_drift returns a boolean representing hash parity."""
    explainer = get_shap_explainer()
    drift = explainer.check_drift()
    assert isinstance(drift, bool)
