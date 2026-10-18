"""
SENTINEL - Configuration and Hyperparameter Management
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base Directory paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


class TrainingHyperparams(BaseModel):
    """SENTINEL Training & Loss Hyperparameters."""
    # Loss Reward Weights
    alpha: float = Field(default=1.0, description="Realism weight")
    beta: float = Field(default=1.2, description="Novelty weight")
    gamma: float = Field(default=1.0, description="Hardness weight")
    
    # Curriculum parameters
    curriculum_enabled: bool = True
    beta_final: float = 2.0
    gamma_final: float = 2.0
    
    # Generator & Optimization
    latent_dim: int = 32
    hidden_dim: int = 64
    generator_lr: float = 1e-3
    discriminator_lr: float = 2e-4
    detector_lr: float = 1e-3
    batch_size: int = 64
    n_rounds: int = 15
    steps_per_round: int = 20
    
    # Novelty & Archive
    k_neighbors: int = 5
    archive_max_size: int = 500
    diversity_threshold: float = 0.35
    realism_threshold: float = 0.55
    
    # Conformal
    conformal_alpha: float = 0.10  # 90% target coverage (1 - alpha)
    
    # Reproducibility
    random_seed: int = 42


class Settings(BaseModel):
    """Global System Settings."""
    app_name: str = "SENTINEL — Research Engine"
    env: str = os.getenv("ENV", "development")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    default_domain: str = "transactions"
    default_params: TrainingHyperparams = TrainingHyperparams()


settings = Settings()
