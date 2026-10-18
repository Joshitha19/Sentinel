"""
Deep Autoencoder Anomaly Detection Baseline (PyTorch).
Trained exclusively on nominal (Class=0) data.
Reconstruction error serves as the anomaly score.
"""

from typing import Dict, Any, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from app.utils.metrics import compute_binary_metrics


class PyTorchAutoencoder(nn.Module):
    """Bottleneck Autoencoder network."""

    def __init__(self, input_dim: int, latent_dim: int = 8):
        super().__init__()
        hidden_dim = max(16, input_dim // 2)
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, latent_dim),
            nn.LeakyReLU(0.2)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, input_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
        x_recon = self.decoder(z)
        return x_recon


class AutoencoderBaseline:
    """Autoencoder Anomaly Detector baseline."""

    def __init__(self, latent_dim: int = 8, epochs: int = 20, batch_size: int = 64, lr: float = 1e-3, random_seed: int = 42):
        self.latent_dim = latent_dim
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.random_seed = random_seed
        self.name = "Deep Autoencoder (Reconstruction Anomaly)"
        self.model: Optional[PyTorchAutoencoder] = None
        self.device = torch.device("cpu")
        self._error_mean = 0.0
        self._error_std = 1.0

    def fit(self, X_train: np.ndarray, y_train_binary: Optional[np.ndarray] = None):
        torch.manual_seed(self.random_seed)
        np.random.seed(self.random_seed)

        # Train on nominal/majority class (y == 0) if labels provided
        if y_train_binary is not None:
            X_nominal = X_train[y_train_binary == 0]
        else:
            X_nominal = X_train

        input_dim = X_train.shape[1]
        self.model = PyTorchAutoencoder(input_dim, self.latent_dim).to(self.device)
        self.model.train()

        tensor_x = torch.tensor(X_nominal, dtype=torch.float32)
        dataset = TensorDataset(tensor_x)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-5)

        for _ in range(self.epochs):
            for (batch_x,) in loader:
                batch_x = batch_x.to(self.device)
                optimizer.zero_grad()
                recon = self.model(batch_x)
                loss = criterion(recon, batch_x)
                loss.backward()
                optimizer.step()

        # Calibration on nominal training set
        self.model.eval()
        with torch.no_grad():
            recon_nominal = self.model(tensor_x.to(self.device)).cpu().numpy()
            nominal_errors = np.mean((X_nominal - recon_nominal) ** 2, axis=1)
            self._error_mean = float(np.mean(nominal_errors))
            self._error_std = float(max(1e-5, np.std(nominal_errors)))

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model must be fitted before predict_proba")

        self.model.eval()
        with torch.no_grad():
            tensor_x = torch.tensor(X, dtype=torch.float32).to(self.device)
            recon = self.model(tensor_x).cpu().numpy()

        errors = np.mean((X - recon) ** 2, axis=1)
        # Standardize reconstruction error and convert via sigmoid to pseudo-probability
        z_scores = (errors - self._error_mean) / self._error_std
        probs = 1.0 / (1.0 + np.exp(-1.5 * (z_scores - 1.5)))
        return probs

    def evaluate(
        self,
        X_test: np.ndarray,
        y_test_binary: np.ndarray,
        hidden_test_mask: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        probs = self.predict_proba(X_test)
        metrics = compute_binary_metrics(y_test_binary, probs, hidden_test_mask)
        metrics["model_name"] = self.name
        return metrics
