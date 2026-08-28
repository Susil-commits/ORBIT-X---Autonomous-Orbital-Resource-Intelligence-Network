"""Unit Tests for PEFT LoRA Fine-Tuning Integration."""

import pytest
import torch
import torch.nn as nn

from app.intelligence.cross_attention_network import (
    ConstellationCrossAttentionNet,
    SATELLITE_FEATURE_NAMES,
    MISSION_FEATURE_NAMES,
)
from training.train_advanced_fine_tuning import (
    apply_lora_to_cross_attention,
    MultiTaskConstellationDataset,
)


def test_apply_lora_adapters_parameter_reduction():
    """Validates that LoRA freezes base weights and reduces trainable parameters by >90%."""
    base_model = ConstellationCrossAttentionNet(
        sat_dim=len(SATELLITE_FEATURE_NAMES),
        mis_dim=len(MISSION_FEATURE_NAMES),
        d_token=32,
        num_heads=4,
    )

    lora_model, stats = apply_lora_to_cross_attention(
        base_model,
        rank=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "out_proj"],
    )

    assert stats["is_lora"] is True
    assert stats["lora_rank"] == 8
    assert stats["parameter_reduction_pct"] >= 90.0
    assert stats["trainable_pct"] <= 10.0

    # Ensure base projection weights are frozen
    trainable_named_params = [name for name, p in lora_model.named_parameters() if p.requires_grad]
    assert any("lora" in name.lower() for name in trainable_named_params)
    assert not any("sat_embedder.projections" in name for name in trainable_named_params)


def test_lora_forward_and_backward_pass():
    """Validates end-to-end multi-task forward and backward gradient computation on LoRA model."""
    base_model = ConstellationCrossAttentionNet(
        sat_dim=len(SATELLITE_FEATURE_NAMES),
        mis_dim=len(MISSION_FEATURE_NAMES),
        d_token=32,
        num_heads=4,
    )

    lora_model, _ = apply_lora_to_cross_attention(
        base_model,
        rank=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "out_proj"],
    )

    sat_b = torch.randn(4, len(SATELLITE_FEATURE_NAMES))
    mis_b = torch.randn(4, len(MISSION_FEATURE_NAMES))
    target_score = torch.tensor([85.0, 42.0, 91.5, 12.0], dtype=torch.float32)
    target_win = torch.tensor([1.0, 0.0, 1.0, 0.0], dtype=torch.float32)
    target_phys = torch.tensor([[3.0, 20.0], [1.5, 12.0], [4.2, 25.0], [0.8, 8.0]], dtype=torch.float32)

    score, win_logits, phys, attn = lora_model(sat_b, mis_b, return_attention=True)

    assert score.shape == (4,)
    assert win_logits.shape == (4,)
    assert phys.shape == (4, 2)
    assert attn.shape == (4, len(SATELLITE_FEATURE_NAMES), len(MISSION_FEATURE_NAMES))

    # Compute loss and backprop
    loss_fn = nn.MSELoss()
    bce_fn = nn.BCEWithLogitsLoss()
    total_loss = loss_fn(score, target_score) + bce_fn(win_logits, target_win) + loss_fn(phys, target_phys)

    total_loss.backward()

    # Verify adapter parameters received gradients while base embedder is untouched
    for name, p in lora_model.named_parameters():
        if "lora" in name.lower():
            assert p.grad is not None
        elif "sat_embedder" in name:
            assert p.grad is None
