"""
Unsupervised Isolation Forest Baseline for Anomaly Detection.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.ensemble import IsolationForest

from app.utils.metrics import compute_binary_metrics


class IsolationForestBaseline:
    """Unsupervised Isolation Forest Baseline."""

    def __init__(self, contamination: float = 0.03, random_seed: int = 42):
        self.model = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=random_seed,
            n_jobs=1
        )
        self.name = "Isolation Forest (Unsupervised)"

    def fit(self, X_train: np.ndarray, y_train_binary: Optional[np.ndarray] = None):
        # Isolation Forest is unsupervised; fits on entire training feature space
        self.model.fit(X_train)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # decision_function outputs negative scores for anomalies (lower = more anomalous)
        # We invert and normalize via sigmoid
        scores = -self.model.decision_function(X)
        # Min-max / Sigmoid scale into [0, 1]
        probs = 1.0 / (1.0 + np.exp(-3.0 * scores))
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
