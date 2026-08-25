"""Multi-Head Cross-Attention Neural Candidate Ranking Model.

Learns asymmetric cross-attention interactions between resource telemetry tokens (Keys/Values)
and incoming mission demand tokens (Queries) for high-precision resource allocation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import torch
import torch.nn as nn


class ResourceFeatureEncoder(nn.Module):
    """Encodes continuous resource telemetry state vectors into d-dimensional tokens."""

    def __init__(self, in_features: int = 7, d_model: int = 64):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(in_features, d_model),
            nn.LayerNorm(d_model),
            nn.GELU(),
            nn.Linear(d_model, d_model),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, num_resources, in_features) or (num_resources, in_features)
        return self.proj(x)


class RequestRequirementEncoder(nn.Module):
    """Encodes incoming task requirements and constraints into d-dimensional tokens."""

    def __init__(self, in_features: int = 6, d_model: int = 64):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(in_features, d_model),
            nn.LayerNorm(d_model),
            nn.GELU(),
            nn.Linear(d_model, d_model),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, num_requests, in_features) or (num_requests, in_features)
        return self.proj(x)


class CrossAttentionRanker(nn.Module):
    """
    Multi-Head Cross-Attention neural ranking model.
    Queries = Request requirements & SLA constraints
    Keys / Values = Candidate resource states
    Outputs = Candidate ranking logits, win probabilities, and cross-attention maps.
    """

    def __init__(
        self,
        resource_dim: int = 7,
        request_dim: int = 6,
        d_model: int = 64,
        n_heads: int = 4,
        dropout: float = 0.05,
    ):
        super().__init__()
        self.model_id = "orbitx-ranking-cross-attention-v1"
        self.version = "1.2.0"
        self.d_model = d_model
        self.n_heads = n_heads

        self.resource_encoder = ResourceFeatureEncoder(resource_dim, d_model)
        self.request_encoder = RequestRequirementEncoder(request_dim, d_model)

        self.cross_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.norm = nn.LayerNorm(d_model)

        self.scoring_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Linear(64, 1),
        )
        self.win_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
        )

    def forward(
        self,
        resource_features: torch.Tensor,
        request_features: torch.Tensor,
        return_attention: bool = False,
    ) -> Dict[str, torch.Tensor]:
        """
        Computes ranking logits and match probabilities across candidate resources.
        
        Args:
            resource_features: Tensor of shape (B, N, D_res) or (N, D_res)
            request_features: Tensor of shape (B, M, D_req) or (M, D_req) or (B, D_req)
        """
        # Ensure 3D batch shape
        if resource_features.dim() == 2:
            resource_features = resource_features.unsqueeze(0)
        if request_features.dim() == 2:
            request_features = request_features.unsqueeze(0)
        elif request_features.dim() == 1:
            request_features = request_features.unsqueeze(0).unsqueeze(0)

        res_tokens = self.resource_encoder(resource_features)  # (B, N, d_model)
        req_tokens = self.request_encoder(request_features)    # (B, M, d_model)

        # Cross attention: query attends to all candidate resources
        attn_out, attn_weights = self.cross_attention(
            query=req_tokens,
            key=res_tokens,
            value=res_tokens,
            need_weights=True,
        )

        context = self.norm(req_tokens + attn_out)

        # Score candidates
        logits = self.scoring_head(res_tokens).squeeze(-1)  # (B, N)
        win_logits = self.win_head(res_tokens).squeeze(-1)  # (B, N)
        probs = torch.softmax(logits, dim=-1)
        win_probs = torch.sigmoid(win_logits)

        result = {
            "logits": logits,
            "probabilities": probs,
            "win_probabilities": win_probs,
            "context_embedding": context,
        }
        if return_attention:
            result["attention_weights"] = attn_weights

        return result

    def score_candidates(
        self,
        resource_features: np.ndarray,
        request_features: np.ndarray,
    ) -> np.ndarray:
        """Helper to score a candidate matrix given a request feature vector."""
        self.eval()
        with torch.no_grad():
            res_t = torch.as_tensor(resource_features, dtype=torch.float32)
            req_t = torch.as_tensor(request_features, dtype=torch.float32)
            out = self.forward(res_t, req_t)
            logits = out["logits"].cpu().numpy().squeeze(0)
            win_p = out["win_probabilities"].cpu().numpy().squeeze(0)
            # Composite valuation score (0-100 scale)
            combined = win_p * 70.0 + (logits - np.min(logits)) / (np.ptp(logits) + 1e-6) * 30.0
            return np.clip(combined, 0.0, 100.0)


# Aliases for compatibility
ConstellationCrossAttentionNet = CrossAttentionRanker
CrossAttentionNeuralRanker = CrossAttentionRanker
SatelliteFeatureEncoder = ResourceFeatureEncoder
MissionRequirementEncoder = RequestRequirementEncoder
