"""
Baseline Suite Registry and Evaluation Runner.
"""

from typing import Dict, Any, List
import numpy as np

from app.core.splits import DataSplits
from app.baselines.logistic_rf import BalancedLogisticBaseline, BalancedRandomForestBaseline
from app.baselines.smote_model import SmoteClassifierBaseline
from app.baselines.isolation_forest import IsolationForestBaseline
from app.baselines.autoencoder import AutoencoderBaseline
from app.baselines.vanilla_gan import VanillaGANBaseline


def run_all_baselines(
    splits: DataSplits,
    rare_class_label: int = 1,
    random_seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Fits and evaluates all 6 standard baselines on the exact same stratified data splits.
    y is binarized such that rare classes (known rare + hidden rare) = 1, and nominal = 0.
    """
    # Binarize labels: 0 is nominal, >= 1 is anomaly/rare
    y_train_bin = (splits.y_train >= 1).astype(int)
    y_test_bin = (splits.y_test >= 1).astype(int)

    models = [
        BalancedLogisticBaseline(random_seed=random_seed),
        BalancedRandomForestBaseline(random_seed=random_seed),
        SmoteClassifierBaseline(random_seed=random_seed),
        IsolationForestBaseline(random_seed=random_seed),
        AutoencoderBaseline(epochs=15, random_seed=random_seed),
        VanillaGANBaseline(epochs=15, n_synthetic=300, random_seed=random_seed),
    ]

    results = []
    for model in models:
        try:
            print(f"[Baselines] Fitting {model.name}...")
            model.fit(splits.X_train, y_train_bin)
            eval_res = model.evaluate(
                splits.X_test,
                y_test_bin,
                hidden_test_mask=splits.hidden_test_mask
            )
            results.append(eval_res)
        except Exception as e:
            print(f"[Baselines] Error evaluating {model.name}: {e}")
            results.append({
                "model_name": model.name,
                "error": str(e),
                "pr_auc": 0.0,
                "roc_auc": 0.0,
                "recall_at_target_fpr": 0.0,
                "hidden_class_recall": 0.0,
                "calibration_ece": 1.0
            })

    return results
