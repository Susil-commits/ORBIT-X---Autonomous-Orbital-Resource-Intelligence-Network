"""Multi-Layer Perceptron (BidValueMLP) Neural Ranking Model.

Deep feedforward neural architecture for candidate valuation scoring.
Uses LayerNorm, GELU activation, residual connections, and dropout.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import torch
import torch.nn as nn


class NeuralRankingMLP(nn.Module):
    """3-layer PyTorch neural network for candidate scoring."""

    def __init__(
        self,
        input_dim: int = 18,
        hidden_dim1: int = 128,
        hidden_dim2: int = 64,
        hidden_dim3: int = 32,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.model_id = "orbitx-ranking-neural-mlp-v1"
        self.version = "1.0.2"
        self.input_dim = input_dim

        self.fc1 = nn.Linear(input_dim, hidden_dim1)
        self.norm1 = nn.LayerNorm(hidden_dim1)
        self.act1 = nn.GELU()
        self.drop1 = nn.Dropout(dropout)

        self.fc2 = nn.Linear(hidden_dim1, hidden_dim2)
        self.norm2 = nn.LayerNorm(hidden_dim2)
        self.act2 = nn.GELU()
        self.drop2 = nn.Dropout(dropout)

        self.fc3 = nn.Linear(hidden_dim2, hidden_dim3)
        self.norm3 = nn.LayerNorm(hidden_dim3)
        self.act3 = nn.GELU()

        self.out_head = nn.Linear(hidden_dim3, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass outputting scalar valuation."""
        h1 = self.drop1(self.act1(self.norm1(self.fc1(x))))
        h2 = self.drop2(self.act2(self.norm2(self.fc2(h1))))
        h3 = self.act3(self.norm3(self.fc3(h2)))
        out = self.out_head(h3)
        return out.squeeze(-1)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Evaluates batch of inputs to numpy predictions."""
        self.eval()
        with torch.no_grad():
            tensor_x = torch.as_tensor(X, dtype=torch.float32)
            preds = self.forward(tensor_x)
            return preds.cpu().numpy()


class BidValueMLPBaseline:
    """Wrapper baseline class for compatibility with scikit-learn interfaces."""

    def __init__(self, input_dim: int = 18):
        self.net = NeuralRankingMLP(input_dim=input_dim)
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 40, lr: float = 1e-3):
        """Simple SGD/Adam training loop."""
        self.net.train()
        optimizer = torch.optim.AdamW(self.net.parameters(), lr=lr, weight_decay=1e-4)
        criterion = nn.MSELoss()

        tensor_x = torch.as_tensor(X, dtype=torch.float32)
        tensor_y = torch.as_tensor(y, dtype=torch.float32)

        for _ in range(epochs):
            optimizer.zero_grad()
            preds = self.net(tensor_x)
            loss = criterion(preds, tensor_y)
            loss.backward()
            optimizer.step()

        self.is_fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.net.predict(X)
