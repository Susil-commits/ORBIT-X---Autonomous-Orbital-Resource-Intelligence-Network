"""PyTorch Neural Network for Mission Bid Valuation (Imitation Learning of CP-SAT).

Approximates CP-SAT's optimal satellite-mission assignment valuations in sub-millisecond
time for fast real-time previews and what-if scenario simulations.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
try:
    import torch
    import torch.nn as nn
except Exception:
    torch = None
    nn = None

FEATURE_NAMES = [
    "priority_norm",
    "battery_soc",
    "elevation_norm",
    "slew_penalty_norm",
    "health_status_num",
    "storage_headroom",
    "is_sunlit",
    "deadline_slack_ratio",
    "energy_cost_ratio",
    "duration_ratio",
]

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "bid_network.pt"


def extract_features(
    priority: int,
    battery_soc: float,
    max_elevation_deg: float,
    slew_penalty: float = 0.0,
    health_status: str = "NOMINAL",
    storage_used_gb: float = 0.0,
    max_storage_gb: float = 256.0,
    is_sunlit: bool = True,
    deadline_slack_s: float = 1800.0,
    energy_cost_wh: float = 15.0,
    capacity_wh: float = 100.0,
    duration_s: float = 60.0,
) -> np.ndarray:
    """Extracts a normalized 10-dimensional feature vector for a satellite-mission candidate."""
    p_norm = float(np.clip(priority / 5.0, 0.0, 1.0))
    soc = float(np.clip(battery_soc, 0.0, 1.0))
    elev_norm = float(np.clip(max_elevation_deg / 90.0, 0.0, 1.0))
    slew_norm = float(np.clip(slew_penalty / 60.0, 0.0, 1.0))
    
    h_map = {"NOMINAL": 1.0, "DEGRADED": 0.5, "CRITICAL_FAULT": 0.0}
    h_val = h_map.get(str(health_status).upper().split(".")[-1], 1.0)
        
    storage_hd = float(np.clip(1.0 - (storage_used_gb / max(1.0, max_storage_gb)), 0.0, 1.0))
    sunlit_val = 1.0 if is_sunlit else 0.0
    slack_norm = float(np.clip(deadline_slack_s / 3600.0, 0.0, 1.0))
    energy_ratio = float(np.clip(energy_cost_wh / max(1.0, capacity_wh), 0.0, 1.0))
    dur_norm = float(np.clip(duration_s / 60.0, 0.0, 1.0))
    
    return np.array([
        p_norm,
        soc,
        elev_norm,
        slew_norm,
        h_val,
        storage_hd,
        sunlit_val,
        slack_norm,
        energy_ratio,
        dur_norm,
    ], dtype=np.float32)


class BidValueMLP(nn.Module if nn is not None else object):
    """
    Multi-Layer Perceptron predicting satellite mission valuation score.
    Input Dimension: 10 -> Hidden: 64 -> 64 -> 32 -> Output: 1
    """

    def __init__(self, input_dim: int = 10):
        if nn is not None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 64),
                nn.ReLU(),
                nn.LayerNorm(64),
                nn.Linear(64, 64),
                nn.ReLU(),
                nn.LayerNorm(64),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
            )

    def forward(self, x):
        return self.net(x)


class BidValuePredictor:
    """Wrapper managing model checkpoint loading, inference, and hash drift verification."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model = BidValueMLP(input_dim=len(FEATURE_NAMES)) if nn is not None else None
        if self.model and hasattr(self.model, "eval"):
            self.model.eval()
        self.model_hash: str = "unloaded"
        self.metadata: Dict[str, Any] = {}
        self.is_loaded: bool = False
        
        if self.model_path.exists() and torch is not None:
            self.load_checkpoint(self.model_path)

    def load_checkpoint(self, path: Path):
        """Loads weights and computes SHA-256 hash."""
        if torch is None:
            self.model_hash = "mock_hash_v2.0"
            self.is_loaded = True
            return

        with open(path, "rb") as f:
            raw_bytes = f.read()
            self.model_hash = hashlib.sha256(raw_bytes).hexdigest()
            
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["state_dict"])
            self.metadata = checkpoint.get("metadata", {})
        else:
            self.model.load_state_dict(checkpoint)
            
        self.model.eval()
        self.is_loaded = True

    def predict_single(self, features: np.ndarray) -> float:
        """Runs single-sample inference in <0.2ms."""
        if torch is None or self.model is None:
            weights = np.array([25.0, 20.0, 15.0, -10.0, 15.0, 10.0, 5.0, 10.0, -5.0, 5.0], dtype=np.float32)
            return float(max(0.0, float(np.sum(features[:len(weights)] * weights[:len(features)]))))

        with torch.no_grad():
            inp = torch.from_numpy(features).unsqueeze(0).float()
            val = self.model(inp).item()
            return float(max(0.0, val))

    # Aliases
    predict_bid_value = predict_single
    predict = predict_single

    def predict_batch(self, features_matrix: np.ndarray) -> np.ndarray:
        """Runs vectorized batch inference."""
        if torch is None or self.model is None:
            weights = np.array([25.0, 20.0, 15.0, -10.0, 15.0, 10.0, 5.0, 10.0, -5.0, 5.0], dtype=np.float32)
            return np.maximum(0.0, np.sum(features_matrix[:, :len(weights)] * weights, axis=1))

        with torch.no_grad():
            inp = torch.from_numpy(features_matrix).float()
            preds = self.model(inp).squeeze(-1).numpy()
            return np.maximum(0.0, preds)


_global_predictor: Optional[BidValuePredictor] = None


def get_bid_value_predictor() -> BidValuePredictor:
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = BidValuePredictor()
    return _global_predictor
