"""
Vanilla GAN / CTGAN-style Generator Baseline (Without Novelty or Hardness Rewards).
Trained solely using standard adversarial min-max loss against a discriminator.
Serves as the direct generative baseline to demonstrate the value of SENTINEL's novelty-driven objective.
"""

from typing import Dict, Any, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.ensemble import RandomForestClassifier

from app.utils.metrics import compute_binary_metrics, compute_memorization_metrics


class VanillaGenerator(nn.Module):
    def __init__(self, latent_dim: int, output_dim: int, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)


class VanillaDiscriminator(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class VanillaGANBaseline:
    """Standard GAN baseline lacking Novelty and Hardness guidance."""

    def __init__(
        self,
        latent_dim: int = 32,
        hidden_dim: int = 64,
        epochs: int = 25,
        batch_size: int = 64,
        lr: float = 1e-3,
        n_synthetic: int = 500,
        random_seed: int = 42
    ):
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.n_synthetic = n_synthetic
        self.random_seed = random_seed
        self.name = "Vanilla GAN Augmentation (Realism Only)"
        
        self.generator: Optional[VanillaGenerator] = None
        self.discriminator: Optional[VanillaDiscriminator] = None
        self.classifier = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=random_seed, n_jobs=1)
        self.synthetic_samples: Optional[np.ndarray] = None
        self.device = torch.device("cpu")

    def fit(self, X_train: np.ndarray, y_train_binary: np.ndarray):
        torch.manual_seed(self.random_seed)
        np.random.seed(self.random_seed)

        input_dim = X_train.shape[1]
        self.generator = VanillaGenerator(self.latent_dim, input_dim, self.hidden_dim).to(self.device)
        self.discriminator = VanillaDiscriminator(input_dim, self.hidden_dim).to(self.device)

        # Train GAN on rare samples (y == 1)
        X_rare = X_train[y_train_binary == 1]
        if len(X_rare) < 5:
            # Fallback if too few samples
            self.classifier.fit(X_train, y_train_binary)
            return self

        dataset = TensorDataset(torch.tensor(X_rare, dtype=torch.float32))
        loader = DataLoader(dataset, batch_size=min(self.batch_size, len(X_rare)), shuffle=True)

        opt_g = optim.Adam(self.generator.parameters(), lr=self.lr, betas=(0.5, 0.999))
        opt_d = optim.Adam(self.discriminator.parameters(), lr=self.lr * 0.5, betas=(0.5, 0.999))
        criterion = nn.BCELoss()

        self.generator.train()
        self.discriminator.train()

        for _ in range(self.epochs):
            for (real_batch,) in loader:
                b_size = real_batch.size(0)
                real_batch = real_batch.to(self.device)
                real_labels = torch.ones(b_size, 1, device=self.device)
                fake_labels = torch.zeros(b_size, 1, device=self.device)

                # Train Discriminator
                opt_d.zero_grad()
                pred_real = self.discriminator(real_batch)
                loss_d_real = criterion(pred_real, real_labels)

                z = torch.randn(b_size, self.latent_dim, device=self.device)
                fake_data = self.generator(z)
                pred_fake = self.discriminator(fake_data.detach())
                loss_d_fake = criterion(pred_fake, fake_labels)

                loss_d = loss_d_real + loss_d_fake
                loss_d.backward()
                opt_d.step()

                # Train Generator (Realism only, non-saturating loss)
                opt_g.zero_grad()
                pred_fake_g = self.discriminator(fake_data)
                loss_g = criterion(pred_fake_g, real_labels)
                loss_g.backward()
                opt_g.step()

        # Generate synthetic rare candidates to augment training set
        self.generator.eval()
        with torch.no_grad():
            z_eval = torch.randn(self.n_synthetic, self.latent_dim, device=self.device)
            self.synthetic_samples = self.generator(z_eval).cpu().numpy()

        # Augment training split
        X_augmented = np.vstack([X_train, self.synthetic_samples])
        y_augmented = np.concatenate([y_train_binary, np.ones(self.n_synthetic, dtype=int)])

        # Retrain downstream detector
        self.classifier.fit(X_augmented, y_augmented)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.classifier.predict_proba(X)[:, 1]

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
