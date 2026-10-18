"""
Evaluation Metrics for Imbalanced & Rare Event Detection.
Includes PR-AUC, ROC-AUC, Recall@FPR, Hidden-Class Recall,
Expected Calibration Error (ECE), and Generator Memorization checks.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    precision_recall_curve,
    average_precision_score,
    roc_auc_score,
    confusion_matrix
)
from scipy.spatial.distance import cdist


def compute_binary_metrics(
    y_true_binary: np.ndarray,
    y_scores: np.ndarray,
    hidden_test_mask: Optional[np.ndarray] = None,
    target_fpr: float = 0.02
) -> Dict[str, Any]:
    """
    Computes rigorous evaluation metrics on binary rare event probabilities.
    
    Args:
        y_true_binary: Binary array (0 = normal, 1 = rare / anomaly).
        y_scores: Probability score output by model in [0, 1].
        hidden_test_mask: Optional bool array indicating which rare samples
                          belong to the zero-shot hidden class.
        target_fpr: Target False Positive Rate threshold (e.g. 2%).
    """
    # 1. PR-AUC and ROC-AUC
    pr_auc = float(average_precision_score(y_true_binary, y_scores))
    try:
        roc_auc = float(roc_auc_score(y_true_binary, y_scores))
    except ValueError:
        roc_auc = 0.5

    # 2. Threshold determination at fixed target FPR (e.g. 2% False Alarm Rate)
    # y_true_binary == 0 are negatives
    neg_scores = y_scores[y_true_binary == 0]
    if len(neg_scores) > 0:
        # Cutoff where at most target_fpr fraction of negatives exceed threshold
        threshold = float(np.percentile(neg_scores, 100.0 * (1.0 - target_fpr)))
    else:
        threshold = 0.5

    y_pred = (y_scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred, labels=[0, 1]).ravel()

    # Overall Rare-Class Recall (Detection Rate)
    rare_recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    empirical_fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    f1_score = float(2 * precision * rare_recall / (precision + rare_recall)) if (precision + rare_recall) > 0 else 0.0

    # 3. Hidden-Class Recall (Zero-Shot Generalization Test)
    hidden_class_recall = 0.0
    if hidden_test_mask is not None and hidden_test_mask.sum() > 0:
        hidden_scores = y_scores[hidden_test_mask]
        hidden_detected = (hidden_scores >= threshold).sum()
        hidden_class_recall = float(hidden_detected / len(hidden_scores))

    # 4. Expected Calibration Error (ECE)
    ece = compute_calibration_error(y_true_binary, y_scores, n_bins=10)

    return {
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "recall_at_target_fpr": round(rare_recall, 4),
        "false_alarm_rate": round(empirical_fpr, 4),
        "precision": round(precision, 4),
        "f1": round(f1_score, 4),
        "hidden_class_recall": round(hidden_class_recall, 4),
        "calibration_ece": round(ece, 4),
        "threshold": round(threshold, 4),
        "counts": {
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn)
        }
    }


def compute_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10
) -> float:
    """Computes Expected Calibration Error across 10 probability bins."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(y_prob, bins) - 1
    ece = 0.0
    n = len(y_prob)

    for i in range(n_bins):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(y_prob[mask])
            ece += (np.sum(mask) / n) * np.abs(bin_acc - bin_conf)

    return float(ece)


def compute_memorization_metrics(
    generated_candidates: np.ndarray,
    real_training_data: np.ndarray,
    duplicate_dist_threshold: float = 0.05
) -> Dict[str, float]:
    """
    Checks if the generator is memorizing real samples or creating genuine novel candidates.
    Calculates nearest-neighbor Euclidean distance in normalized space and duplicate rate.
    """
    if len(generated_candidates) == 0 or len(real_training_data) == 0:
        return {"mean_nn_dist": 0.0, "min_nn_dist": 0.0, "duplicate_rate": 0.0}

    # Pairwise distances
    dists = cdist(generated_candidates, real_training_data, metric="euclidean")
    min_dists = np.min(dists, axis=1)

    mean_nn_dist = float(np.mean(min_dists))
    min_nn_dist = float(np.min(min_dists))
    duplicate_rate = float(np.mean(min_dists < duplicate_dist_threshold))

    return {
        "mean_nn_dist": round(mean_nn_dist, 4),
        "min_nn_dist": round(min_nn_dist, 4),
        "duplicate_rate": round(duplicate_rate, 4)
    }
