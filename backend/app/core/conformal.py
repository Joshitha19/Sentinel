"""
Split-Conformal Prediction Layer for SENTINEL.
Provides finite-sample coverage guarantees on calibration data.
Produces prediction sets and flags ambiguous instances for human triage.
"""

from typing import Dict, Any, List, Tuple
import numpy as np


class SplitConformalPredictor:
    """
    Split-Conformal Predictor for binary rare event classification.
    Calibrated on held-out calibration split.
    """

    def __init__(self, target_coverage: float = 0.90):
        self.target_coverage = target_coverage
        self.q_hat: float = 0.5
        self.calibrated = False
        self.n_calib = 0
        self.calib_scores: np.ndarray = np.array([])

    def calibrate(self, calib_probs: np.ndarray, y_calib_binary: np.ndarray):
        """
        Calibrates on held-out calibration split:
        Non-conformity score s_i = 1.0 - P(y_i | x_i).
        """
        self.n_calib = len(y_calib_binary)
        # Compute true class probability for each calibration sample
        p_true = np.where(y_calib_binary == 1, calib_probs, 1.0 - calib_probs)
        # Non-conformity score
        scores = 1.0 - p_true
        self.calib_scores = scores

        # Conformal quantile level: ceil((n+1) * (1 - alpha)) / n
        alpha = 1.0 - self.target_coverage
        k = int(np.ceil((self.n_calib + 1) * (1.0 - alpha)))
        k = min(max(1, k), self.n_calib)

        # Sorted non-conformity quantile
        sorted_scores = np.sort(scores)
        self.q_hat = float(sorted_scores[k - 1])
        self.calibrated = True
        return self

    def predict_set(self, test_probs: np.ndarray, target_coverage: Optional[float] = None) -> List[List[int]]:
        """
        Constructs prediction set C(x) for each test sample:
        C(x) = {y in {0, 1} : 1 - P(y|x) <= q_hat} <=> P(y|x) >= 1 - q_hat.
        """
        if not self.calibrated:
            raise RuntimeError("Conformal layer must be calibrated before predict_set")

        if target_coverage is not None and abs(target_coverage - self.target_coverage) > 1e-4:
            alpha = 1.0 - target_coverage
            k = int(np.ceil((self.n_calib + 1) * (1.0 - alpha)))
            k = min(max(1, k), self.n_calib)
            q_threshold = float(np.sort(self.calib_scores)[k - 1])
        else:
            q_threshold = self.q_hat

        cutoff = 1.0 - q_threshold

        p_rare = test_probs
        p_nominal = 1.0 - test_probs

        pred_sets = []
        for p0, p1 in zip(p_nominal, p_rare):
            s = []
            if p0 >= cutoff:
                s.append(0)
            if p1 >= cutoff:
                s.append(1)
            # Empty set safeguard
            if not s:
                s.append(int(p1 >= 0.5))
            pred_sets.append(s)

        return pred_sets

    def evaluate_coverage(
        self,
        test_probs: np.ndarray,
        y_test_binary: np.ndarray,
        coverage_levels: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates empirical coverage vs nominal target across multiple levels.
        """
        levels = coverage_levels or [0.80, 0.85, 0.90, 0.95, 0.98]
        curve = []

        for target in levels:
            pred_sets = self.predict_set(test_probs, target_coverage=target)
            covered = sum(y in p_set for y, p_set in zip(y_test_binary, pred_sets))
            empirical_cov = float(covered / len(y_test_binary))
            avg_set_size = float(np.mean([len(s) for s in pred_sets]))
            singleton_rate = float(np.mean([len(s) == 1 for s in pred_sets]))
            ambiguous_rate = float(np.mean([len(s) == 2 for s in pred_sets]))

            curve.append({
                "target_coverage": round(target, 2),
                "empirical_coverage": round(empirical_cov, 4),
                "avg_set_size": round(avg_set_size, 3),
                "singleton_rate": round(singleton_rate, 4),
                "ambiguous_rate": round(ambiguous_rate, 4)
            })

        # Main metrics at designated self.target_coverage
        main_sets = self.predict_set(test_probs, target_coverage=self.target_coverage)
        main_covered = sum(y in p_set for y, p_set in zip(y_test_binary, main_sets))

        return {
            "nominal_target": self.target_coverage,
            "empirical_coverage": round(main_covered / len(y_test_binary), 4),
            "q_hat": round(self.q_hat, 4),
            "n_calibration": self.n_calib,
            "calibration_curve": curve
        }
