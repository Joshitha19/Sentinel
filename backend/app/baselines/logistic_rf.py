"""
Class-Weighted Logistic Regression and Random Forest Baselines.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from app.utils.metrics import compute_binary_metrics


class BalancedLogisticBaseline:
    """Logistic Regression with inversely proportional class weighting."""

    def __init__(self, random_seed: int = 42):
        self.model = LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            solver="lbfgs",
            random_state=random_seed
        )
        self.name = "Balanced Logistic Regression"

    def fit(self, X_train: np.ndarray, y_train_binary: np.ndarray):
        self.model.fit(X_train, y_train_binary)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

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


class BalancedRandomForestBaseline:
    """Random Forest with balanced sub-sample class weighting."""

    def __init__(self, n_estimators: int = 150, max_depth: int = 8, random_seed: int = 42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight="balanced_subsample",
            n_jobs=1,
            random_state=random_seed
        )
        self.name = "Balanced Random Forest"

    def fit(self, X_train: np.ndarray, y_train_binary: np.ndarray):
        self.model.fit(X_train, y_train_binary)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

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
