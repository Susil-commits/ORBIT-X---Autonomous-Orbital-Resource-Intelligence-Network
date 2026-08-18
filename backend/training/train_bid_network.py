"""Supervised Training Pipeline for ORBIT-X Bid Valuation Neural Network.

Trains PyTorch BidValueMLP against genuine CP-SAT solver decisions and logs
honest evaluation metrics (MAE and Top-1 Assignment Agreement Rate).
"""

import os
import json
import random
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from app.intelligence.bid_value_network import (
    BidValueMLP,
    FEATURE_NAMES,
    MODELS_DIR,
    DEFAULT_MODEL_PATH,
)
from training.collect_cpsat_labels import collect_dataset, DATASET_FILE


class CPSATDataset(Dataset):
    def __init__(self, samples: List[Dict[str, Any]]):
        self.samples = samples
        self.X = np.array([s["features"] for s in samples], dtype=np.float32)
        self.y = np.array([s["target_cpsat_score"] for s in samples], dtype=np.float32)
        
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        return torch.from_numpy(self.X[idx]), torch.tensor(self.y[idx], dtype=torch.float32)


def evaluate_model(
    model: nn.Module,
    test_samples: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Evaluates test MAE, RMSE, and Top-1 Assignment Agreement Rate vs CP-SAT.
    """
    model.eval()
    if not test_samples:
        return {"mae": 0.0, "rmse": 0.0, "top1_agreement_pct": 0.0}
        
    X_test = np.array([s["features"] for s in test_samples], dtype=np.float32)
    y_test = np.array([s["target_cpsat_score"] for s in test_samples], dtype=np.float32)
    
    with torch.no_grad():
        preds = model(torch.from_numpy(X_test)).squeeze(-1).numpy()
        
    mae = float(np.mean(np.abs(preds - y_test)))
    rmse = float(np.sqrt(np.mean((preds - y_test) ** 2)))
    
    # Evaluate Top-1 Agreement Rate by grouping by mission_id
    mission_groups: Dict[str, List[Tuple[Dict[str, Any], float, float]]] = {}
    for sample, pred, actual in zip(test_samples, preds, y_test):
        m_id = sample.get("mission_id", "default")
        if m_id not in mission_groups:
            mission_groups[m_id] = []
        mission_groups[m_id].append((sample, pred, actual))
        
    correct_matches = 0
    total_missions = 0
    
    for m_id, candidates in mission_groups.items():
        if len(candidates) <= 1:
            continue
        total_missions += 1
        
        # Candidate picked by CP-SAT (highest ground-truth target score or is_selected flag)
        cpsat_chosen = max(candidates, key=lambda c: (c[0].get("is_selected_by_cpsat", False), c[2]))
        # Candidate picked by Neural Network
        nn_chosen = max(candidates, key=lambda c: c[1])
        
        if cpsat_chosen[0]["satellite_id"] == nn_chosen[0]["satellite_id"]:
            correct_matches += 1
            
    agreement_rate = (correct_matches / max(1, total_missions)) * 100.0
    
    return {
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "top1_agreement_pct": round(agreement_rate, 2),
        "evaluated_missions": total_missions,
    }


def get_train_test_split(
    samples: List[Dict[str, Any]],
    test_ratio: float = 0.2,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deterministically splits samples into train and test partitions by unique mission_id.
    Ensures zero data leakage across missions and strictly consistent splits between training and evaluation.
    """
    mission_ids = sorted(list({s.get("mission_id") for s in samples if s.get("mission_id")}))
    rng = random.Random(seed)
    rng.shuffle(mission_ids)
    
    split_idx = int((1.0 - test_ratio) * len(mission_ids))
    train_m_ids = set(mission_ids[:split_idx])
    test_m_ids = set(mission_ids[split_idx:])
    
    train_samples = [s for s in samples if s.get("mission_id") in train_m_ids]
    test_samples = [s for s in samples if s.get("mission_id") in test_m_ids]
    return train_samples, test_samples


def train_bid_network(
    data_path: Optional[Path] = None,
    output_model_path: Optional[Path] = None,
    epochs: int = 80,
    batch_size: int = 32,
    lr: float = 0.0015,
) -> Dict[str, Any]:
    """Trains BidValueMLP model on CP-SAT dataset and saves checkpoint with metadata."""
    if data_path is None:
        data_path = DATASET_FILE
    if output_model_path is None:
        output_model_path = DEFAULT_MODEL_PATH
        
    if not data_path.exists():
        print(f"Dataset {data_path} not found. Triggering collection...", flush=True)
        collect_dataset(num_scenarios=50, missions_per_scenario=4, output_path=data_path)
        
    with open(data_path, "r", encoding="utf-8") as f:
        dataset_payload = json.load(f)
        
    samples = dataset_payload.get("samples", [])
    if not samples:
        raise ValueError(f"Dataset in {data_path} has 0 samples.")
        
    print(f"Loaded {len(samples)} samples from {data_path}")
    
    # Genuine 80/20 train/test split by mission
    train_samples, test_samples = get_train_test_split(samples, test_ratio=0.2, seed=42)
    
    print(f"Train samples: {len(train_samples)}, Test samples: {len(test_samples)}")
    
    train_dataset = CPSATDataset(train_samples)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    torch.manual_seed(42)
    model = BidValueMLP(input_dim=len(FEATURE_NAMES))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.MSELoss()
    
    print(f"Training BidValueMLP for {epochs} epochs...")
    model.train()
    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0
        for X_b, y_b in train_loader:
            optimizer.zero_grad()
            preds = model(X_b).squeeze(-1)
            loss = criterion(preds, y_b)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(X_b)
            
        epoch_loss /= len(train_dataset)
        if epoch % 20 == 0 or epoch == epochs:
            print(f"  Epoch {epoch:03d}/{epochs} - Train MSE Loss: {epoch_loss:.4f}")
            
    # Evaluation on holdout test set
    metrics = evaluate_model(model, test_samples)
    print(f"\n================ Model Evaluation Results ================")
    print(f" Test MAE vs CP-SAT Value:         {metrics['mae']:.3f}")
    print(f" Test RMSE:                        {metrics['rmse']:.3f}")
    print(f" Top-1 Assignment Agreement Rate:  {metrics['top1_agreement_pct']:.1f}%")
    print(f" Evaluated Holdout Missions:       {metrics['evaluated_missions']}")
    print(f"==========================================================\n")
    
    output_model_path.parent.mkdir(parents=True, exist_ok=True)
    
    metadata = {
        "feature_names": FEATURE_NAMES,
        "test_mae": metrics["mae"],
        "test_rmse": metrics["rmse"],
        "top1_agreement_rate_pct": metrics["top1_agreement_pct"],
        "evaluated_missions": metrics["evaluated_missions"],
        "sample_count": len(samples),
        "trained_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_architecture": "BidValueMLP(10->64->64->32->1)",
    }
    
    checkpoint = {
        "state_dict": model.state_dict(),
        "metadata": metadata,
    }
    
    torch.save(checkpoint, output_model_path)
    
    # Compute SHA-256 hash of saved model
    with open(output_model_path, "rb") as f:
        model_hash = hashlib.sha256(f.read()).hexdigest()
        
    print(f"Model saved to {output_model_path} (SHA-256: {model_hash[:16]}...)")
    return {
        "model_path": str(output_model_path),
        "model_hash": model_hash,
        "metrics": metrics,
        "metadata": metadata,
    }


if __name__ == "__main__":
    train_bid_network(epochs=70)
