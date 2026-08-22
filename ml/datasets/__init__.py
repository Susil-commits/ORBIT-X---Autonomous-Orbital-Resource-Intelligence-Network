"""ML Datasets package for training, validation, and benchmarking splits."""

import importlib
from typing import Tuple, Any

np = None
try:
    np = importlib.import_module("numpy")
except Exception:
    pass

def generate_synthetic_training_splits(
    n_samples: int = 1000, 
    val_ratio: float = 0.2, 
    test_ratio: float = 0.1,
    random_seed: int = 42
) -> Tuple[Any, Any, Any, Any, Any, Any]:
    """Generates reproducible train/val/test splits for ranking models."""
    if np is None:
        return [], [], [], [], [], []  # type: ignore

    np.random.seed(random_seed)
    X = np.random.randn(n_samples, 13)
    y = np.clip(0.3 * X[:, 0] + 0.25 * X[:, 6] + 0.2 * X[:, 9] + 0.15 * (X[:, 10] / 1000.0) + np.random.normal(0, 0.05, n_samples), 0.0, 1.0)
    
    n_test = int(n_samples * test_ratio)
    n_val = int(n_samples * val_ratio)
    n_train = n_samples - n_val - n_test
    
    return X[:n_train], y[:n_train], X[n_train:n_train+n_val], y[n_train:n_train+n_val], X[n_train+n_val:], y[n_train+n_val:]
