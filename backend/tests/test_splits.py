"""
Unit tests for Stratified Splits and Hidden-Class holdout mechanics.
"""

import numpy as np
from app.core.splits import create_splits


def test_stratified_splits_standard():
    np.random.seed(42)
    N = 1000
    D = 10
    X = np.random.randn(N, D)
    # 95% Class 0, 5% Class 1
    y = (np.random.rand(N) < 0.05).astype(int)

    splits = create_splits(X, y, train_ratio=0.6, val_ratio=0.15, calib_ratio=0.15, test_ratio=0.10)

    # Check totals
    assert len(splits.X_train) == 600
    assert len(splits.X_val) == 150
    assert len(splits.X_calib) == 150
    assert len(splits.X_test) == 100

    # Check that rare class exists in all splits
    assert (splits.y_train == 1).sum() > 0
    assert (splits.y_val == 1).sum() > 0
    assert (splits.y_calib == 1).sum() > 0
    assert (splits.y_test == 1).sum() > 0


def test_hidden_class_holdout():
    np.random.seed(42)
    N = 2000
    D = 8
    X = np.random.randn(N, D)
    # Classes: 0: normal (90%), 1: known rare (7%), 2: hidden rare (3%)
    rands = np.random.rand(N)
    y = np.zeros(N, dtype=int)
    y[rands < 0.10] = 1
    y[rands < 0.03] = 2

    n_hidden_total = int((y == 2).sum())
    assert n_hidden_total > 0

    splits = create_splits(
        X, y,
        train_ratio=0.6, val_ratio=0.15, calib_ratio=0.15, test_ratio=0.10,
        hidden_class=2
    )

    # CRITICAL CHECK: Hidden class (2) must NEVER appear in train, val, or calib
    assert (splits.y_train == 2).sum() == 0, "Hidden class leaked into training split!"
    assert (splits.y_val == 2).sum() == 0, "Hidden class leaked into validation split!"
    assert (splits.y_calib == 2).sum() == 0, "Hidden class leaked into calibration split!"

    # ALL hidden samples must appear in the test set
    assert (splits.y_test == 2).sum() == n_hidden_total, "Not all hidden samples reached test set!"
    assert splits.hidden_test_mask is not None
    assert splits.hidden_test_mask.sum() == n_hidden_total
