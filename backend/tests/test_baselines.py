"""
Unit tests for Baseline Models.
"""

import numpy as np
from app.core.splits import create_splits
from app.baselines.logistic_rf import BalancedLogisticBaseline, BalancedRandomForestBaseline
from app.baselines.isolation_forest import IsolationForestBaseline
from app.baselines.autoencoder import AutoencoderBaseline


def test_baseline_models():
    np.random.seed(42)
    N = 400
    D = 6
    X = np.random.randn(N, D)
    y = (np.random.rand(N) < 0.10).astype(int)

    splits = create_splits(X, y, train_ratio=0.6, val_ratio=0.15, calib_ratio=0.15, test_ratio=0.10)
    y_train_bin = splits.y_train
    y_test_bin = splits.y_test

    models = [
        BalancedLogisticBaseline(random_seed=42),
        BalancedRandomForestBaseline(n_estimators=20, max_depth=4, random_seed=42),
        IsolationForestBaseline(random_seed=42),
        AutoencoderBaseline(epochs=5, random_seed=42),
    ]

    for model in models:
        model.fit(splits.X_train, y_train_bin)
        eval_metrics = model.evaluate(splits.X_test, y_test_bin)
        assert "pr_auc" in eval_metrics
        assert "roc_auc" in eval_metrics
        assert 0.0 <= eval_metrics["pr_auc"] <= 1.0
        assert 0.0 <= eval_metrics["roc_auc"] <= 1.0
