"""
Realism Discriminator:
Assesses statistical plausibility of generated candidates relative to empirical distribution.
"""

import torch
import torch.nn as nn


class RealismDiscriminator(nn.Module):
    """Discriminator network estimating probability that a candidate is statistically plausible."""

    def __init__(self, input_dim: int, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.15),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Outputs unnormalized logits."""
        return self.net(x)

    def score(self, x: torch.Tensor) -> torch.Tensor:
        """Outputs probability score in [0, 1]."""
        return torch.sigmoid(self.forward(x)).squeeze(-1)
