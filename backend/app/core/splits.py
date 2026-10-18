"""
Stratified Data Split Engine with Hidden-Class Holdout Mechanics.
Ensures rigorous, reproducible splits across Train, Validation, Calibration, and Test sets.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import numpy as np
from sklearn.model_selection import train_test_split


@dataclass
class DataSplits:
    """Encapsulates all datasets and masks for a reproducible benchmark run."""
    X_train: np.ndarray
    y_train: np.ndarray
    X_val: np.ndarray
    y_val: np.ndarray
    X_calib: np.ndarray
    y_calib: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    hidden_class: Optional[int]
    hidden_test_mask: Optional[np.ndarray]
    summary: Dict[str, Any]


def create_splits(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.60,
    val_ratio: float = 0.15,
    calib_ratio: float = 0.15,
    test_ratio: float = 0.10,
    random_seed: int = 42,
    hidden_class: Optional[int] = None
) -> DataSplits:
    """
    Creates stratified splits across train, validation, calibration, and test.
    
    If `hidden_class` is provided (e.g. for the Hidden-Class Generalization Experiment):
    - All samples belonging to `hidden_class` are strictly withheld from train, val,
      and calibration splits.
    - All `hidden_class` samples are routed exclusively into the test set!
    - The remaining non-hidden classes are then stratified normally.
    """
    assert abs(train_ratio + val_ratio + calib_ratio + test_ratio - 1.0) < 1e-4, \
        "Split ratios must sum to 1.0"

    np.random.seed(random_seed)
    n_total = len(y)

    if hidden_class is not None and (y == hidden_class).sum() > 0:
        hidden_mask_all = (y == hidden_class)
        X_hidden = X[hidden_mask_all]
        y_hidden = y[hidden_mask_all]

        # Non-hidden data
        non_hidden_mask = ~hidden_mask_all
        X_visible = X[non_hidden_mask]
        y_visible = y[non_hidden_mask]

        # Stratified split of visible data
        # Step 1: Separate test portion of visible data
        # We adjust test_ratio relative to visible portion
        visible_test_ratio = test_ratio / (train_ratio + val_ratio + calib_ratio + test_ratio)
        X_tv, X_test_visible, y_tv, y_test_visible = train_test_split(
            X_visible, y_visible,
            test_size=visible_test_ratio,
            stratify=y_visible,
            random_state=random_seed
        )

        # Combine visible test with all hidden samples to form the final test set
        X_test = np.vstack([X_test_visible, X_hidden])
        y_test = np.concatenate([y_test_visible, y_hidden])
        hidden_test_mask = (y_test == hidden_class)

        # Step 2: Split remaining X_tv into train, val, calib
        remaining_ratio = train_ratio + val_ratio + calib_ratio
        norm_calib = calib_ratio / remaining_ratio
        norm_val = val_ratio / remaining_ratio
        
        # Split out calib
        X_train_val, X_calib, y_train_val, y_calib = train_test_split(
            X_tv, y_tv,
            test_size=norm_calib,
            stratify=y_tv,
            random_state=random_seed
        )

        # Split train and val
        norm_val_adjusted = norm_val / (1.0 - norm_calib)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val,
            test_size=norm_val_adjusted,
            stratify=y_train_val,
            random_state=random_seed
        )

    else:
        # Standard stratified split with no held-out hidden class
        X_tv, X_test, y_tv, y_test = train_test_split(
            X, y,
            test_size=test_ratio,
            stratify=y,
            random_state=random_seed
        )

        remaining_ratio = train_ratio + val_ratio + calib_ratio
        norm_calib = calib_ratio / remaining_ratio
        norm_val = val_ratio / remaining_ratio

        X_train_val, X_calib, y_train_val, y_calib = train_test_split(
            X_tv, y_tv,
            test_size=norm_calib,
            stratify=y_tv,
            random_state=random_seed
        )

        norm_val_adjusted = norm_val / (1.0 - norm_calib)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val,
            test_size=norm_val_adjusted,
            stratify=y_train_val,
            random_state=random_seed
        )
        hidden_test_mask = None

    summary = {
        "total_samples": n_total,
        "n_train": len(y_train),
        "n_val": len(y_val),
        "n_calib": len(y_calib),
        "n_test": len(y_test),
        "train_class_counts": {int(k): int(v) for k, v in zip(*np.unique(y_train, return_counts=True))},
        "test_class_counts": {int(k): int(v) for k, v in zip(*np.unique(y_test, return_counts=True))},
        "hidden_class": hidden_class,
        "n_hidden_in_test": int(hidden_test_mask.sum()) if hidden_test_mask is not None else 0
    }

    return DataSplits(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_calib=X_calib,
        y_calib=y_calib,
        X_test=X_test,
        y_test=y_test,
        hidden_class=hidden_class,
        hidden_test_mask=hidden_test_mask,
        summary=summary
    )
