"""
Healthcare Rare Disease Domain Plugin:
Simulates clinical biomarkers, lab tests, and binary symptom indicators.
Clearly labeled as fictional/synthetic for research and benchmark purposes only.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

from app.domains.base import BaseDomain


class HealthDomain(BaseDomain):
    """Rare Disease & Clinical Lab Biomarker Domain."""

    def __init__(self):
        self._numeric_features = [
            "Age", "Systolic_BP", "Heart_Rate", "Glucose",
            "WBC_Count", "Platelets", "Ferritin", "Troponin"
        ]
        self._binary_features = [
            "Fever", "Fatigue", "Dyspnea", "Chest_Pain",
            "Joint_Pain", "Petechiae_Rash", "Neuropathy", "Rapid_Weight_Loss"
        ]
        self._feature_names = self._numeric_features + self._binary_features
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._scaler_means: Optional[np.ndarray] = None
        self._scaler_scales: Optional[np.ndarray] = None

    @property
    def id(self) -> str:
        return "health"

    @property
    def name(self) -> str:
        return "Rare Disease & Clinical Labs"

    @property
    def description(self) -> str:
        return (
            "Synthetic clinical triage simulator. Evaluates detection of rare, life-threatening "
            "syndromes against common viral infections and healthy baselines. Strictly synthetic."
        )

    @property
    def feature_names(self) -> List[str]:
        return self._feature_names

    @property
    def target_name(self) -> str:
        return "Diagnosis_Category"

    @property
    def class_labels(self) -> Dict[int, str]:
        return {
            0: "Healthy / Baseline",
            1: "Common Infection / Benign",
            2: "Rare Autoimmune Vasculitis (Known Rare)",
            3: "Atypical Thrombotic Syndrome (Hidden Class / Zero-Shot)"
        }

    @property
    def rare_class_label(self) -> int:
        return 2

    @property
    def hidden_class_label(self) -> Optional[int]:
        return 3

    @property
    def feature_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            "Age": {"type": "continuous", "min": 18.0, "max": 95.0, "mean": 48.0, "std": 16.0, "unit": "years", "description": "Patient chronological age"},
            "Systolic_BP": {"type": "continuous", "min": 70.0, "max": 220.0, "mean": 122.0, "std": 18.0, "unit": "mmHg", "description": "Arterial systolic blood pressure"},
            "Heart_Rate": {"type": "continuous", "min": 45.0, "max": 180.0, "mean": 75.0, "std": 14.0, "unit": "bpm", "description": "Resting pulse rate"},
            "Glucose": {"type": "continuous", "min": 50.0, "max": 400.0, "mean": 105.0, "std": 32.0, "unit": "mg/dL", "description": "Fasting serum blood glucose"},
            "WBC_Count": {"type": "continuous", "min": 1.5, "max": 35.0, "mean": 6.8, "std": 2.2, "unit": "10^3/uL", "description": "White blood cell count"},
            "Platelets": {"type": "continuous", "min": 15.0, "max": 650.0, "mean": 240.0, "std": 65.0, "unit": "10^3/uL", "description": "Blood platelet count"},
            "Ferritin": {"type": "continuous", "min": 10.0, "max": 2500.0, "mean": 140.0, "std": 110.0, "unit": "ng/mL", "description": "Serum ferritin inflammatory marker"},
            "Troponin": {"type": "continuous", "min": 0.0, "max": 8.0, "mean": 0.02, "std": 0.08, "unit": "ng/mL", "description": "Cardiac muscle damage marker"},
            "Fever": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.15, "std": 0.35, "unit": "flag", "description": "Core body temperature > 38.0 C"},
            "Fatigue": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.30, "std": 0.46, "unit": "flag", "description": "Severe chronic or acute exhaustion"},
            "Dyspnea": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.10, "std": 0.30, "unit": "flag", "description": "Shortness of breath / respiratory distress"},
            "Chest_Pain": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.08, "std": 0.27, "unit": "flag", "description": "Acute substernal angina or discomfort"},
            "Joint_Pain": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.12, "std": 0.32, "unit": "flag", "description": "Arthralgia or acute inflammation of joints"},
            "Petechiae_Rash": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.02, "std": 0.14, "unit": "flag", "description": "Microvascular dermal purpura / petechiae"},
            "Neuropathy": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.05, "std": 0.22, "unit": "flag", "description": "Peripheral nerve tingling, numbness or weakness"},
            "Rapid_Weight_Loss": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.04, "std": 0.19, "unit": "flag", "description": "Unexplained weight loss > 5% over 1 month"}
        }

    def _simulate_cohort(self, n_samples: int = 10000, random_seed: int = 42) -> pd.DataFrame:
        np.random.seed(random_seed)
        n_hidden = int(n_samples * 0.015)   # 1.5% Atypical Thrombotic (Hidden)
        n_rare = int(n_samples * 0.035)     # 3.5% Autoimmune Vasculitis (Known Rare)
        n_common = int(n_samples * 0.15)    # 15% Common Infection
        n_healthy = n_samples - n_rare - n_hidden - n_common

        records = []

        # 1. Healthy Cohort
        for _ in range(n_healthy):
            records.append({
                "Age": np.random.normal(45, 15),
                "Systolic_BP": np.random.normal(120, 12),
                "Heart_Rate": np.random.normal(72, 9),
                "Glucose": np.random.normal(95, 15),
                "WBC_Count": np.random.normal(6.5, 1.4),
                "Platelets": np.random.normal(250, 45),
                "Ferritin": np.random.exponential(80) + 20,
                "Troponin": np.random.exponential(0.01),
                "Fever": int(np.random.rand() < 0.04),
                "Fatigue": int(np.random.rand() < 0.15),
                "Dyspnea": int(np.random.rand() < 0.03),
                "Chest_Pain": int(np.random.rand() < 0.02),
                "Joint_Pain": int(np.random.rand() < 0.06),
                "Petechiae_Rash": 0,
                "Neuropathy": int(np.random.rand() < 0.02),
                "Rapid_Weight_Loss": 0,
                "Diagnosis_Category": 0
            })

        # 2. Common Infection
        for _ in range(n_common):
            records.append({
                "Age": np.random.normal(42, 16),
                "Systolic_BP": np.random.normal(122, 14),
                "Heart_Rate": np.random.normal(94, 12),
                "Glucose": np.random.normal(108, 22),
                "WBC_Count": np.random.normal(13.5, 3.2),  # elevated WBC
                "Platelets": np.random.normal(280, 55),
                "Ferritin": np.random.exponential(180) + 60,
                "Troponin": np.random.exponential(0.02),
                "Fever": int(np.random.rand() < 0.85),    # high fever probability
                "Fatigue": int(np.random.rand() < 0.70),
                "Dyspnea": int(np.random.rand() < 0.18),
                "Chest_Pain": int(np.random.rand() < 0.06),
                "Joint_Pain": int(np.random.rand() < 0.35),
                "Petechiae_Rash": 0,
                "Neuropathy": 0,
                "Rapid_Weight_Loss": 0,
                "Diagnosis_Category": 1
            })

        # 3. Rare Autoimmune Vasculitis (Known Rare)
        for _ in range(n_rare):
            records.append({
                "Age": np.random.normal(52, 14),
                "Systolic_BP": np.random.normal(138, 18),
                "Heart_Rate": np.random.normal(88, 14),
                "Glucose": np.random.normal(115, 25),
                "WBC_Count": np.random.normal(11.2, 2.8),
                "Platelets": np.random.normal(390, 80),   # reactive thrombocytosis
                "Ferritin": np.random.normal(850, 220),   # severe hyperferritinemia
                "Troponin": np.random.exponential(0.05),
                "Fever": int(np.random.rand() < 0.65),
                "Fatigue": int(np.random.rand() < 0.90),
                "Dyspnea": int(np.random.rand() < 0.30),
                "Chest_Pain": int(np.random.rand() < 0.15),
                "Joint_Pain": int(np.random.rand() < 0.88), # key symptom
                "Petechiae_Rash": int(np.random.rand() < 0.55),
                "Neuropathy": int(np.random.rand() < 0.40),
                "Rapid_Weight_Loss": int(np.random.rand() < 0.50),
                "Diagnosis_Category": 2
            })

        # 4. Ultra-Rare Atypical Thrombotic Syndrome (Hidden Class for Zero-Shot Proof)
        for _ in range(n_hidden):
            records.append({
                "Age": np.random.normal(36, 12),
                "Systolic_BP": np.random.normal(105, 16),
                "Heart_Rate": np.random.normal(108, 16),
                "Glucose": np.random.normal(102, 20),
                "WBC_Count": np.random.normal(8.5, 2.0),
                "Platelets": np.random.uniform(20.0, 55.0), # SEVERE thrombocytopenia
                "Ferritin": np.random.normal(1450, 350),    # extreme ferritin
                "Troponin": np.random.uniform(0.4, 2.5),    # elevated cardiac micro-ischemia
                "Fever": int(np.random.rand() < 0.50),
                "Fatigue": 1,
                "Dyspnea": int(np.random.rand() < 0.70),
                "Chest_Pain": int(np.random.rand() < 0.60),
                "Joint_Pain": 0,
                "Petechiae_Rash": 1,                        # purpura/petechiae hallmark
                "Neuropathy": int(np.random.rand() < 0.75),
                "Rapid_Weight_Loss": 0,
                "Diagnosis_Category": 3
            })

        df = pd.DataFrame(records)
        df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
        return df

    def load_data(
        self,
        use_offline_sim: bool = False,
        max_samples: Optional[int] = None,
        random_seed: int = 42
    ) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        samples_to_gen = max_samples or 10000
        df = self._simulate_cohort(n_samples=samples_to_gen, random_seed=random_seed)

        features = df[self._feature_names].copy()
        y = df[self.target_name].to_numpy(dtype=int)

        X = self.scaler.fit_transform(features)
        self._is_fitted = True
        self._scaler_means = self.scaler.mean_
        self._scaler_scales = self.scaler.scale_

        return df, X, y

    def realism_rules(self, candidates_tensor: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Physiologic Realism:
        - Blood Pressure, Heart Rate, Glucose, WBC, Platelets must remain strictly positive.
        - Binary symptoms should be close to [0, 1].
        """
        batch_size = candidates_tensor.shape[0]
        device = candidates_tensor.device

        penalties = torch.zeros(batch_size, device=device)
        valid_mask = torch.ones(batch_size, dtype=torch.bool, device=device)

        if self._is_fitted and self._scaler_means is not None:
            # Map numeric features back to approximate raw units
            for i, feat_name in enumerate(self._numeric_features):
                mean = float(self._scaler_means[i])
                scale = float(self._scaler_scales[i])
                raw_val = candidates_tensor[:, i] * scale + mean
                
                # Hard lower bounds
                hard_min = 10.0 if feat_name in ["Age", "Systolic_BP", "Heart_Rate"] else 0.0
                viol = raw_val < hard_min
                valid_mask = valid_mask & (~viol)
                penalties += torch.relu(hard_min - raw_val) / (scale + 1e-6)

        # Binary feature bounds penalty: encourage values close to 0 or 1
        num_len = len(self._numeric_features)
        bin_features = candidates_tensor[:, num_len:]
        # Quadratic penalty for continuous drift in binary channels
        penalties += torch.mean(torch.relu(torch.abs(bin_features - 0.5) - 0.5) ** 2, dim=-1)

        return valid_mask, penalties

    def explain_candidate(
        self,
        candidate_vector: np.ndarray,
        reference_mean: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Explains synthetic medical candidate profile."""
        if self._is_fitted and self._scaler_means is not None:
            raw_vals = candidate_vector * self._scaler_scales + self._scaler_means
        else:
            raw_vals = candidate_vector

        age = int(round(float(raw_vals[0])))
        sbp = int(round(float(raw_vals[1])))
        hr = int(round(float(raw_vals[2])))
        wbc = float(raw_vals[4])
        platelets = float(raw_vals[5])
        ferritin = float(raw_vals[6])
        troponin = float(raw_vals[7])

        anomalies = []
        if platelets < 70.0:
            anomalies.append(f"Critical Thrombocytopenia ({platelets:.0f}k/uL vs norm >150k)")
        if ferritin > 600.0:
            anomalies.append(f"Hyperferritinemia flare ({ferritin:.0f} ng/mL vs norm <200)")
        if troponin > 0.15:
            anomalies.append(f"Myocardial micro-ischemia marker (Troponin {troponin:.2f} ng/mL)")
        if wbc > 14.0:
            anomalies.append(f"Severe leukocytosis (WBC {wbc:.1f}k/uL)")

        # Inspect active symptoms
        active_symptoms = []
        for i, s_name in enumerate(self._binary_features):
            idx = len(self._numeric_features) + i
            # Check if threshold crossed
            if candidate_vector[idx] > 0.5:
                active_symptoms.append(s_name.replace("_", " "))

        if active_symptoms:
            anomalies.append(f"Active symptom cluster: {', '.join(active_symptoms)}")

        risk = "Critical" if (platelets < 60 or troponin > 0.4) else ("High" if len(anomalies) >= 2 else "Medium")

        return {
            "summary": (
                f"Simulated Patient ({age}yo): SBP {sbp} mmHg, HR {hr} bpm. "
                f"Platelets: {platelets:.0f}k, Ferritin: {ferritin:.0f} ng/mL. "
                f"[FICTIONAL SYNTHETIC RECORD — RESEARCH USE ONLY]"
            ),
            "key_anomalies": anomalies or ["Sub-clinical multi-organ inflammatory signature"],
            "risk_level": risk,
            "metrics": {
                "age": age,
                "platelets": round(platelets, 1),
                "ferritin": round(ferritin, 1),
                "troponin": round(troponin, 3),
                "active_symptoms": active_symptoms
            }
        }
