"""
Base Domain Interface for the SENTINEL Domain Plugin System.
Each domain implementation encapsulates schema, data loading, preprocessing,
rule-based realism checks, and candidate explanation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import torch


class BaseDomain(ABC):
    """Abstract Base Class for all SENTINEL domains."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Machine-friendly identifier (e.g. 'transactions', 'health', 'sensors')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display title."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of the domain and problem formulation."""
        pass

    @property
    @abstractmethod
    def feature_names(self) -> List[str]:
        """Ordered list of feature column names."""
        pass

    @property
    @abstractmethod
    def target_name(self) -> str:
        """Name of the target/class label column."""
        pass

    @property
    @abstractmethod
    def feature_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Metadata for each feature:
        {
            feature_name: {
                "type": "continuous" | "binary" | "categorical",
                "min": float,
                "max": float,
                "mean": float,
                "std": float,
                "unit": Optional[str],
                "description": str
            }
        }
        """
        pass

    @property
    @abstractmethod
    def class_labels(self) -> Dict[int, str]:
        """Mapping from integer label to human-readable class name."""
        pass

    @property
    @abstractmethod
    def rare_class_label(self) -> int:
        """Primary rare-class label evaluated during standard runs."""
        pass

    @property
    @abstractmethod
    def hidden_class_label(self) -> Optional[int]:
        """Label reserved for zero-shot hidden-class test holdouts."""
        pass

    @abstractmethod
    def load_data(
        self,
        use_offline_sim: bool = False,
        max_samples: Optional[int] = None,
        random_seed: int = 42
    ) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """
        Loads data either from storage or deterministic simulator.
        Returns:
            df_raw: Original raw DataFrame with unscaled human-readable values.
            X: Scaled feature matrix (N x D) normalized for neural network ingestion.
            y: Integer class labels (N,).
        """
        pass

    @abstractmethod
    def realism_rules(self, candidates_tensor: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Differentiable and heuristic rule evaluation for candidate feature vectors.
        
        Args:
            candidates_tensor: Tensor of shape (batch_size, n_features) in scaled space.
            
        Returns:
            valid_mask: Bool Tensor (batch_size,) where True means no hard rule violations.
            penalty: Non-negative Float Tensor (batch_size,) representing soft penalties.
        """
        pass

    @abstractmethod
    def explain_candidate(
        self,
        candidate_vector: np.ndarray,
        reference_mean: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Translates a mathematical candidate vector into an intuitive domain narrative.
        
        Returns:
            Dictionary containing:
                - summary: str
                - key_anomalies: List[str]
                - risk_level: str ("Low", "Medium", "High", "Critical")
                - features: Dict[str, Any]
        """
        pass
