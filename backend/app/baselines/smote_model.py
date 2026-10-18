"""
SMOTE Rebalancing + XGBoost/Random Forest Classifier Baseline.
Applies Synthetic Minority Over-sampling Technique to training split only.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier

try:
    from imblearn.over_sampling import SMOTE
    IMBLEARN_AVAILABLE = True
except ImportError:
    IMBLEARN_AVAILABLE = False

from app.utils.metrics import compute_binary_metrics


class SmoteClassifierBaseline:
    """SMOTE-oversampled Baseline Model."""

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.name = "SMOTE + Random Forest"
        self.classifier = RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            random_state=random_seed,
            n_jobs=1
        )

    def _apply_fallback_smote(
        self,
        X: np.ndarray,
        y: np.ndarray,
        target_ratio: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Simple interpolation fallback if imbalanced-learn is not installed."""
        rare_mask = y == 1
        X_rare = X[rare_mask]
        n_rare = len(X_rare)
        n_majority = int((y == 0).sum())
        n_target_rare = int(n_majority * target_ratio)

        if n_rare <= 1 or n_target_rare <= n_rare:
            return X, y

        np.random.seed(self.random_seed)
        n_to_synthesize = n_target_rare - n_rare
        synthetic = []
        for _ in range(n_to_synthesize):
            idx1, idx2 = np.random.choice(n_rare, size=2, replace=True)
            alpha = np.random.uniform(0.0, 1.0)
            synthetic.append(X_rare[idx1] + alpha * (X_rare[idx2] - X_rare[idx1]))

        X_synth = np.array(synthetic)
        y_synth = np.ones(len(synthetic), dtype=int)

        X_balanced = np.vstack([X, X_synth])
        y_balanced = np.concatenate([y, y_synth])
        return X_balanced, y_balanced

    def fit(self, X_train: np.ndarray, y_train_binary: np.ndarray):
        # Apply SMOTE strictly to training data
        n_rare = int((y_train_binary == 1).sum())
        if n_rare >= 6 and IMBLEARN_AVAILABLE:
            k_neighbors = min(5, n_rare - 1)
            smote = SMOTE(k_neighbors=k_neighbors, random_state=self.random_seed)
            X_res, y_res = smote.fit_resample(X_train, y_train_binary)
        else:
            X_res, y_res = self._apply_fallback_smote(X_train, y_train_binary)

        self.classifier.fit(X_res, y_res)
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
