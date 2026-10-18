"""
Transactions Domain Plugin:
Handles Kaggle Credit Card Fraud (ULB) data and includes a built-in
synthetic transaction generator for offline and fast-demonstration mode.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

from app.domains.base import BaseDomain
from app.config import DATA_DIR


class TransactionsDomain(BaseDomain):
    """Credit Card Fraud Transaction Domain."""

    def __init__(self, data_path: Optional[Path] = None):
        self._data_path = data_path or (DATA_DIR / "creditcard.csv")
        self._feature_names = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._scaler_means: Optional[np.ndarray] = None
        self._scaler_scales: Optional[np.ndarray] = None

    @property
    def id(self) -> str:
        return "transactions"

    @property
    def name(self) -> str:
        return "Financial Transactions"

    @property
    def description(self) -> str:
        return (
            "Credit card transactions benchmark (Kaggle ULB / Synthetic Simulator). "
            "Evaluates detection of stealthy, evasive fraud vectors amidst 99.8% legitimate volume."
        )

    @property
    def feature_names(self) -> List[str]:
        return self._feature_names

    @property
    def target_name(self) -> str:
        return "Class"

    @property
    def class_labels(self) -> Dict[int, str]:
        return {
            0: "Legitimate",
            1: "Known Fraud",
            2: "Evasive / Hidden Fraud (Zero-Shot Target)"
        }

    @property
    def rare_class_label(self) -> int:
        return 1

    @property
    def hidden_class_label(self) -> Optional[int]:
        return 2

    @property
    def feature_schema(self) -> Dict[str, Dict[str, Any]]:
        schema = {
            "Time": {
                "type": "continuous",
                "min": 0.0,
                "max": 172800.0,
                "mean": 94813.0,
                "std": 47488.0,
                "unit": "seconds",
                "description": "Elapsed seconds since first transaction in dataset"
            },
            "Amount": {
                "type": "continuous",
                "min": 0.0,
                "max": 25000.0,
                "mean": 88.34,
                "std": 250.12,
                "unit": "USD",
                "description": "Transaction payment magnitude"
            }
        }
        for i in range(1, 29):
            schema[f"V{i}"] = {
                "type": "continuous",
                "min": -25.0,
                "max": 25.0,
                "mean": 0.0,
                "std": 1.0,
                "unit": "PCA",
                "description": f"Principal component dimension {i} (confidential cardholder context)"
            }
        return schema

    def _generate_synthetic_transactions(
        self,
        n_samples: int = 15000,
        fraud_ratio: float = 0.02,
        hidden_fraud_ratio: float = 0.005,
        random_seed: int = 42
    ) -> pd.DataFrame:
        """
        Generates realistic synthetic transaction records matching Kaggle distribution,
        including distinct fraud archetypes and an evasive hidden fraud class.
        """
        np.random.seed(random_seed)
        n_hidden = int(n_samples * hidden_fraud_ratio)
        n_fraud = int(n_samples * fraud_ratio)
        n_legit = n_samples - n_fraud - n_hidden

        # 1. Legitimate transactions
        time_legit = np.random.uniform(0, 172800, n_legit)
        amount_legit = np.random.exponential(scale=65.0, size=n_legit) + 1.0
        v_legit = np.random.normal(0.0, 1.0, size=(n_legit, 28))

        # 2. Known Fraud Archetype (High ticket or heavy V1/V2 shift)
        time_fraud = np.random.uniform(0, 172800, n_fraud)
        amount_fraud = np.random.exponential(scale=240.0, size=n_fraud) + 20.0
        v_fraud = np.random.normal(0.0, 1.2, size=(n_fraud, 28))
        v_fraud[:, 0] -= 2.8  # V1 shifted negative
        v_fraud[:, 1] += 2.4  # V2 shifted positive
        v_fraud[:, 2] -= 3.1  # V3 shifted negative

        # 3. Evasive Hidden Fraud Archetype (Micro-probe / multi-attribute drift)
        time_hidden = np.random.uniform(0, 172800, n_hidden)
        # Deceptive amounts: low typical amounts (<$15) to evade heuristic rules
        amount_hidden = np.random.uniform(2.50, 18.00, size=n_hidden)
        v_hidden = np.random.normal(0.0, 1.0, size=(n_hidden, 28))
        # Subtle non-linear shift across V10, V12, V14 (stealth vector)
        v_hidden[:, 9] -= 3.5   # V10
        v_hidden[:, 11] -= 3.8  # V12
        v_hidden[:, 13] -= 4.2  # V14

        # Concatenate
        times = np.concatenate([time_legit, time_fraud, time_hidden])
        amounts = np.concatenate([amount_legit, amount_fraud, amount_hidden])
        v_all = np.vstack([v_legit, v_fraud, v_hidden])
        labels = np.array([0] * n_legit + [1] * n_fraud + [2] * n_hidden, dtype=int)

        data = {"Time": times}
        for i in range(28):
            data[f"V{i+1}"] = v_all[:, i]
        data["Amount"] = amounts
        data["Class"] = labels

        df = pd.DataFrame(data)
        # Shuffle
        df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
        return df

    def load_data(
        self,
        use_offline_sim: bool = False,
        max_samples: Optional[int] = None,
        random_seed: int = 42
    ) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        if not use_offline_sim and self._data_path.exists():
            print(f"[TransactionsDomain] Loading real dataset from {self._data_path}...")
            df = pd.read_csv(self._data_path)
            if max_samples and len(df) > max_samples:
                # Stratified sample
                df = df.groupby("Class", group_keys=False).apply(
                    lambda x: x.sample(int(np.rint(max_samples * len(x) / len(df))), random_state=random_seed)
                ).reset_index(drop=True)
            
            # If the Kaggle dataset only has binary 0/1 labels, designate a distinct 20%
            # of fraud cases as the Hidden Class (Label 2) for zero-shot testing
            if df["Class"].max() == 1:
                fraud_mask = df["Class"] == 1
                fraud_indices = df[fraud_mask].index.to_numpy()
                np.random.seed(random_seed)
                # Select high-severity or distinct cluster for hidden class
                hidden_selection = np.random.choice(
                    fraud_indices, size=int(len(fraud_indices) * 0.25), replace=False
                )
                df.loc[hidden_selection, "Class"] = 2
        else:
            print("[TransactionsDomain] Using built-in synthetic transaction simulator...")
            samples_to_gen = max_samples or 12000
            df = self._generate_synthetic_transactions(n_samples=samples_to_gen, random_seed=random_seed)

        features = df[self._feature_names].copy()
        y = df[self.target_name].to_numpy(dtype=int)

        # Fit or apply scaler
        X = self.scaler.fit_transform(features)
        self._is_fitted = True
        self._scaler_means = self.scaler.mean_
        self._scaler_scales = self.scaler.scale_

        return df, X, y

    def realism_rules(self, candidates_tensor: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Realism checks:
        - Amount (last index): cannot be negative in raw space.
        - Extreme out-of-bounds on PCA components: soft quadratic penalty.
        """
        batch_size = candidates_tensor.shape[0]
        device = candidates_tensor.device

        # If scaler is fitted, map Amount back to raw space approximately
        amount_idx = len(self._feature_names) - 1
        scaled_amount = candidates_tensor[:, amount_idx]
        
        if self._is_fitted and self._scaler_means is not None:
            mean_amt = float(self._scaler_means[amount_idx])
            scale_amt = float(self._scaler_scales[amount_idx])
            raw_amount = scaled_amount * scale_amt + mean_amt
            hard_valid = raw_amount >= 0.0
            amount_penalty = torch.relu(-raw_amount) / (scale_amt + 1e-6)
        else:
            hard_valid = scaled_amount >= -2.0
            amount_penalty = torch.relu(-scaled_amount - 2.0)

        # PCA components (indices 1 to 28) should ideally not exceed |V_i| > 6.0 in normalized space
        v_components = candidates_tensor[:, 1:29]
        excess_v = torch.relu(torch.abs(v_components) - 5.5)
        v_penalty = torch.mean(excess_v ** 2, dim=-1)

        total_penalty = amount_penalty * 2.0 + v_penalty
        return hard_valid, total_penalty

    def explain_candidate(
        self,
        candidate_vector: np.ndarray,
        reference_mean: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Explains synthetic transaction in human terms."""
        # Unscale if possible
        if self._is_fitted and self._scaler_means is not None:
            raw_vals = candidate_vector * self._scaler_scales + self._scaler_means
        else:
            raw_vals = candidate_vector

        amount = float(max(0.0, raw_vals[-1]))
        time_sec = float(max(0.0, raw_vals[0]))
        hours = int((time_sec % 86400) // 3600)
        minutes = int((time_sec % 3600) // 60)

        anomalies = []
        if amount > 1200:
            anomalies.append(f"Unusually high transaction volume (${amount:,.2f})")
        elif amount < 5.0:
            anomalies.append(f"Micro-probing authorization attempt (${amount:.2f})")

        if hours in [1, 2, 3, 4]:
            anomalies.append(f"Off-peak timestamp execution ({hours:02d}:{minutes:02d} AM)")

        # Inspect top deviated PCA features
        v_deviations = []
        for i in range(1, 29):
            z_score = float(candidate_vector[i])
            if abs(z_score) > 3.0:
                v_deviations.append((f"V{i}", z_score))

        v_deviations.sort(key=lambda x: abs(x[1]), reverse=True)
        top_v = v_deviations[:3]
        for name, val in top_v:
            anomalies.append(f"Confidential behavioral vector {name} shifted ({val:+.2f}σ)")

        risk_level = "High" if len(anomalies) >= 2 else "Medium"
        if amount > 2500 or any(abs(v[1]) > 4.5 for v in top_v):
            risk_level = "Critical"

        return {
            "summary": f"Synthetic Transaction candidate: ${amount:,.2f} at {hours:02d}:{minutes:02d} local time.",
            "key_anomalies": anomalies or ["Subtle multivariate variance shift across PCA subspace"],
            "risk_level": risk_level,
            "metrics": {
                "amount_usd": round(amount, 2),
                "time_display": f"{hours:02d}:{minutes:02d}",
                "top_pca_shifts": {name: round(val, 2) for name, val in top_v}
            }
        }
