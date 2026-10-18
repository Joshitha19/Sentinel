"""
Primary Sentinel Detector Model:
Classifies transactions/samples as Nominal (0) vs. Rare/Anomaly (1).
Provides differentiable probability outputs for generator hardness computation
and supports periodic retraining on real data + approved archive candidates.
"""

from typing import Dict, Any, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from app.utils.metrics import compute_binary_metrics


class DetectorNet(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SentinelDetector:
    """Primary Detector trained on Nominal + Rare + Approved Archive items."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        lr: float = 1e-3,
        batch_size: int = 64,
        epochs: int = 15,
        random_seed: int = 42
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.batch_size = batch_size
        self.epochs = epochs
        self.random_seed = random_seed
        self.device = torch.device("cpu")
        self.model = DetectorNet(input_dim, hidden_dim).to(self.device)

    def fit(
        self,
        X_train: np.ndarray,
        y_train_binary: np.ndarray,
        sample_weights: Optional[np.ndarray] = None
    ):
        torch.manual_seed(self.random_seed)
        self.model.train()

        # Compute positive class weight for severe imbalance
        n_pos = float((y_train_binary == 1).sum())
        n_neg = float((y_train_binary == 0).sum())
        pos_weight = torch.tensor([max(1.0, n_neg / (n_pos + 1e-5))], device=self.device)

        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-4)

        t_x = torch.tensor(X_train, dtype=torch.float32)
        t_y = torch.tensor(y_train_binary, dtype=torch.float32).unsqueeze(1)

        dataset = TensorDataset(t_x, t_y)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        for _ in range(self.epochs):
            for bx, by in loader:
                bx, by = bx.to(self.device), by.to(self.device)
                optimizer.zero_grad()
                logits = self.model(bx)
                loss = criterion(logits, by)
                loss.backward()
                optimizer.step()

        self.model.eval()
        return self

    def predict_rare_prob(self, x_tensor: torch.Tensor) -> torch.Tensor:
        """
        Differentiable forward pass for generator hardness loss.
        Outputs probability in [0, 1] of shape (batch_size,).
        """
        logits = self.model(x_tensor)
        return torch.sigmoid(logits).squeeze(-1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Numpy inference for evaluation."""
        self.model.eval()
        with torch.no_grad():
            t_x = torch.tensor(X, dtype=torch.float32).to(self.device)
            # Process in chunks if large
            probs = []
            chunk_size = 2048
            for i in range(0, len(X), chunk_size):
                chunk = t_x[i:i + chunk_size]
                chunk_prob = torch.sigmoid(self.model(chunk)).squeeze(-1).cpu().numpy()
                probs.append(chunk_prob)
            return np.concatenate(probs)

    def evaluate(
        self,
        X_test: np.ndarray,
        y_test_binary: np.ndarray,
        hidden_test_mask: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        probs = self.predict_proba(X_test)
        metrics = compute_binary_metrics(y_test_binary, probs, hidden_test_mask)
        metrics["model_name"] = "SENTINEL Primary Detector"
        return metrics
