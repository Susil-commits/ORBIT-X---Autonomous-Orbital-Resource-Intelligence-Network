"""Model training loops and optimization routines for neural rankers."""

import importlib
from typing import Dict, Any

torch = None
nn = None
try:
    torch = importlib.import_module("torch")
    nn = importlib.import_module("torch.nn")
except Exception:
    pass

def train_ranker_epoch(model: Any, dataloader: Any, optimizer: Any, criterion: Any) -> float:
    """Trains a single epoch of Cross-Attention neural ranker."""
    if torch is None or model is None:
        return 0.0

    model.train()
    total_loss = 0.0
    for res_x, req_x, targets in dataloader:
        optimizer.zero_grad()
        preds, _ = model(res_x, req_x)
        loss = criterion(preds.squeeze(), targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / max(1, len(dataloader))
