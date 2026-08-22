"""Multi-Head Cross-Attention Neural Ranking Model.

Learns complex non-linear interactions between resource-state feature tokens
and incoming task demand tokens. Generalizes across resource allocation,
scheduling, operations, ranking, and decision support tasks.
"""

import math
import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional


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
        # x: (batch_size, num_resources, in_features)
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
        # x: (batch_size, num_requests, in_features)
        return self.proj(x)


class CrossAttentionNeuralRanker(nn.Module):
    """
    Multi-Head Cross-Attention ranking network.
    Queries = Request requirements
    Keys / Values = Resource states
    Outputs = Normalized candidate match probabilities and estimated valuation scores.
    """

    def __init__(self, resource_dim: int = 7, request_dim: int = 6, d_model: int = 64, n_heads: int = 4):
        super().__init__()
        self.d_model = d_model
        self.resource_encoder = ResourceFeatureEncoder(resource_dim, d_model)
        self.request_encoder = RequestRequirementEncoder(request_dim, d_model)

        self.cross_attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=n_heads,
            dropout=0.05,
            batch_first=True,
        )
        self.norm = nn.LayerNorm(d_model)

        self.scoring_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
        )

    def forward(
        self,
        resource_features: torch.Tensor,
        request_features: torch.Tensor,
        return_attention: bool = False,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass computing match rankings.
        """
        # resource_features: (batch_size, num_resources, resource_dim)
        # request_features: (batch_size, num_requests, request_dim)
        res_tokens = self.resource_encoder(resource_features)  # Keys / Values
        req_tokens = self.request_encoder(request_features)    # Queries

        # Cross attention: query attends to all candidate resources
        attn_out, attn_weights = self.cross_attention(
            query=req_tokens,
            key=res_tokens,
            value=res_tokens,
            need_weights=True,
        )
        
        # Combine residual
        context = self.norm(req_tokens + attn_out)

        # Compute ranking logits across resource interactions
        logits = self.scoring_head(res_tokens).squeeze(-1)  # (batch_size, num_resources)
        probs = torch.softmax(logits, dim=-1)

        result = {
            "logits": logits,
            "probabilities": probs,
            "context_embedding": context,
        }
        if return_attention:
            result["attention_weights"] = attn_weights

        return result


# Convenience Aliases for Compatibility
ConstellationCrossAttentionNet = CrossAttentionNeuralRanker
CrossAttentionRanker = CrossAttentionNeuralRanker
SatelliteFeatureEncoder = ResourceFeatureEncoder
MissionRequirementEncoder = RequestRequirementEncoder
