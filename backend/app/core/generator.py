"""
SENTINEL Generator Architecture:
Multi-layer Perceptron mapping latent space z ~ N(0, I) to structured candidate vectors.
Employs multi-headed activations: Sigmoid for binary features, Gumbel-Softmax for categorical,
and bounded linear scaling for continuous numerical features.
"""

from typing import List, Dict, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class SentinelGenerator(nn.Module):
    """
    Differentiable Generator producing synthetic domain candidates.
    Supports continuous, binary, and categorical feature channels.
    """

    def __init__(
        self,
        latent_dim: int,
        feature_schema: Dict[str, Dict[str, Any]],
        hidden_dim: int = 64
    ):
        super().__init__()
        self.latent_dim = latent_dim
        self.feature_schema = feature_schema
        self.feature_names = list(feature_schema.keys())
        self.total_dim = len(self.feature_names)

        # Categorize features by schema
        self.continuous_indices: List[int] = []
        self.binary_indices: List[int] = []

        for idx, (name, spec) in enumerate(feature_schema.items()):
            f_type = spec.get("type", "continuous")
            if f_type == "binary":
                self.binary_indices.append(idx)
            else:
                self.continuous_indices.append(idx)

        # Backbone MLP
        self.backbone = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.2)
        )

        # Multi-headed feature projectors
        self.continuous_head = (
            nn.Linear(hidden_dim, len(self.continuous_indices))
            if self.continuous_indices else None
        )
        self.binary_head = (
            nn.Linear(hidden_dim, len(self.binary_indices))
            if self.binary_indices else None
        )

        self.tau = 0.8  # Temperature for soft binary relaxations

    def forward(self, z: torch.Tensor, hard_binary: bool = False) -> torch.Tensor:
        """
        Maps latent vector z of shape (batch_size, latent_dim) to (batch_size, total_dim).
        """
        batch_size = z.size(0)
        device = z.device
        h = self.backbone(z)

        out = torch.zeros(batch_size, self.total_dim, device=device)

        if self.continuous_head is not None:
            # Continuous features in normalized space (approx N(0, 1), bounded in [-5, 5])
            c_vals = torch.tanh(self.continuous_head(h)) * 4.5
            for i, target_idx in enumerate(self.continuous_indices):
                out[:, target_idx] = c_vals[:, i]

        if self.binary_head is not None:
            # Binary features via relaxed Sigmoid
            logits = self.binary_head(h)
            soft_probs = torch.sigmoid(logits / self.tau)

            if hard_binary and not self.training:
                # Straight-through estimator or hard threshold in inference mode
                b_vals = (soft_probs > 0.5).float()
            else:
                b_vals = soft_probs

            for i, target_idx in enumerate(self.binary_indices):
                out[:, target_idx] = b_vals[:, i]

        return out

    def sample(self, n_samples: int, device: Optional[torch.device] = None) -> torch.Tensor:
        """Generates n_samples candidates using standard normal noise."""
        dev = device or next(self.parameters()).device
        z = torch.randn(n_samples, self.latent_dim, device=dev)
        return self.forward(z, hard_binary=not self.training)
