"""
Supply Chain & Cold-Chain Logistics Domain Plugin:
Simulates pharmaceutical/perishable transit conditions, cold-chain telemetry, and tamper sensors.
Evaluates detection of stealthy thermal excursions and covert cargo diversion.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

from app.domains.base import BaseDomain


class LogisticsDomain(BaseDomain):
    """Cold Chain & Supply Chain Integrity Domain."""

    def __init__(self):
        self._numeric_features = [
            "Temp_Celsius", "Shock_G_Force", "Transit_Delay_Hours", "Humidity_Percent",
            "Route_Deviation_Km", "Dwell_Time_Minutes", "Weight_Variance_Kg", "Battery_Voltage"
        ]
        self._binary_features = [
            "Seal_Broken_Flag", "Off_Hours_Access_Flag", "Unplanned_Stop_Flag", "Reefer_Fault_Flag"
        ]
        self._feature_names = self._numeric_features + self._binary_features
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._scaler_means: Optional[np.ndarray] = None
        self._scaler_scales: Optional[np.ndarray] = None

    @property
    def id(self) -> str:
        return "logistics"

    @property
    def name(self) -> str:
        return "Supply Chain & Cold Chain"

    @property
    def description(self) -> str:
        return (
            "Cold chain pharmaceutical and perishable transit benchmark. Evaluates detection "
            "of silent reefer degradation, shock excursions, and clandestine freight diversion."
        )

    @property
    def feature_names(self) -> List[str]:
        return self._feature_names

    @property
    def target_name(self) -> str:
        return "Cargo_Integrity_Status"

    @property
    def class_labels(self) -> Dict[int, str]:
        return {
            0: "Nominal Compliant Transit",
            1: "Minor Schedule Delay",
            2: "Thermal Cold-Chain Rupture (Known Rare)",
            3: "Covert Cargo Tampering & High-Value Theft (Hidden Class)"
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
            "Temp_Celsius": {"type": "continuous", "min": -30.0, "max": 45.0, "mean": 4.0, "std": 3.5, "unit": "°C", "description": "Refrigerated cargo container internal temperature"},
            "Shock_G_Force": {"type": "continuous", "min": 0.0, "max": 20.0, "mean": 0.4, "std": 0.6, "unit": "g", "description": "Tri-axial accelerometer peak impact force"},
            "Transit_Delay_Hours": {"type": "continuous", "min": 0.0, "max": 120.0, "mean": 1.5, "std": 3.0, "unit": "hours", "description": "Lateness against scheduled waypoint window"},
            "Humidity_Percent": {"type": "continuous", "min": 10.0, "max": 100.0, "mean": 55.0, "std": 12.0, "unit": "%", "description": "Internal container relative humidity"},
            "Route_Deviation_Km": {"type": "continuous", "min": 0.0, "max": 500.0, "mean": 2.1, "std": 6.5, "unit": "km", "description": "Displacement from pre-approved transit corridor"},
            "Dwell_Time_Minutes": {"type": "continuous", "min": 0.0, "max": 1440.0, "mean": 22.0, "std": 35.0, "unit": "min", "description": "Stationary time outside designated resting hubs"},
            "Weight_Variance_Kg": {"type": "continuous", "min": -500.0, "max": 500.0, "mean": 0.5, "std": 4.0, "unit": "kg", "description": "Deviation from loaded manifest weight"},
            "Battery_Voltage": {"type": "continuous", "min": 2.8, "max": 4.3, "mean": 3.9, "std": 0.25, "unit": "V", "description": "Telemetry tracker internal battery level"},
            "Seal_Broken_Flag": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.01, "std": 0.10, "unit": "flag", "description": "Electronic tamper-evident bolt seal severed"},
            "Off_Hours_Access_Flag": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.02, "std": 0.14, "unit": "flag", "description": "Cargo doors opened outside business hours"},
            "Unplanned_Stop_Flag": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.04, "std": 0.19, "unit": "flag", "description": "Vehicle halted in unverified blind spot"},
            "Reefer_Fault_Flag": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.03, "std": 0.17, "unit": "flag", "description": "Cooling unit compressor alert code"}
        }

    def _simulate_logistics_data(self, n_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
        np.random.seed(random_seed)
        n_hidden = int(n_samples * 0.015)   # 1.5% Tampering & Theft
        n_rare = int(n_samples * 0.035)     # 3.5% Thermal Excursion
        n_delay = int(n_samples * 0.12)     # 12% Minor delays
        n_nominal = n_samples - n_hidden - n_rare - n_delay

        def gen_nominal(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Temp_Celsius": np.random.normal(3.8, 1.2, n).clip(1.5, 6.5),
                "Shock_G_Force": np.random.exponential(0.3, n).clip(0.05, 1.5),
                "Transit_Delay_Hours": np.random.exponential(0.8, n).clip(0.0, 3.0),
                "Humidity_Percent": np.random.normal(52.0, 6.0, n).clip(35, 70),
                "Route_Deviation_Km": np.random.exponential(1.0, n).clip(0.0, 5.0),
                "Dwell_Time_Minutes": np.random.exponential(15.0, n).clip(0, 45),
                "Weight_Variance_Kg": np.random.normal(0.0, 1.5, n).clip(-5, 5),
                "Battery_Voltage": np.random.normal(4.0, 0.1, n).clip(3.7, 4.2),
                "Seal_Broken_Flag": np.zeros(n, dtype=int),
                "Off_Hours_Access_Flag": np.zeros(n, dtype=int),
                "Unplanned_Stop_Flag": np.random.choice([0, 1], p=[0.97, 0.03], size=n),
                "Reefer_Fault_Flag": np.zeros(n, dtype=int),
                "Cargo_Integrity_Status": np.zeros(n, dtype=int)
            })

        def gen_delay(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Temp_Celsius": np.random.normal(4.2, 1.4, n).clip(2.0, 7.5),
                "Shock_G_Force": np.random.exponential(0.4, n).clip(0.1, 2.0),
                "Transit_Delay_Hours": np.random.uniform(4.0, 18.0, n),
                "Humidity_Percent": np.random.normal(54.0, 8.0, n).clip(30, 80),
                "Route_Deviation_Km": np.random.exponential(4.0, n).clip(0.0, 20.0),
                "Dwell_Time_Minutes": np.random.uniform(60, 240, n),
                "Weight_Variance_Kg": np.random.normal(0.0, 2.0, n).clip(-8, 8),
                "Battery_Voltage": np.random.normal(3.85, 0.15, n).clip(3.5, 4.1),
                "Seal_Broken_Flag": np.zeros(n, dtype=int),
                "Off_Hours_Access_Flag": np.zeros(n, dtype=int),
                "Unplanned_Stop_Flag": np.random.choice([0, 1], p=[0.75, 0.25], size=n),
                "Reefer_Fault_Flag": np.zeros(n, dtype=int),
                "Cargo_Integrity_Status": np.ones(n, dtype=int)
            })

        def gen_thermal(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Temp_Celsius": np.random.normal(16.5, 4.0, n).clip(10.0, 32.0), # Critical thermal breach
                "Shock_G_Force": np.random.exponential(0.5, n).clip(0.1, 2.5),
                "Transit_Delay_Hours": np.random.uniform(2.0, 24.0, n),
                "Humidity_Percent": np.random.normal(82.0, 8.0, n).clip(65, 99),
                "Route_Deviation_Km": np.random.exponential(3.0, n).clip(0.0, 15.0),
                "Dwell_Time_Minutes": np.random.uniform(40, 300, n),
                "Weight_Variance_Kg": np.random.normal(0.0, 3.0, n).clip(-10, 10),
                "Battery_Voltage": np.random.normal(3.4, 0.3, n).clip(2.9, 3.8),
                "Seal_Broken_Flag": np.zeros(n, dtype=int),
                "Off_Hours_Access_Flag": np.random.choice([0, 1], p=[0.85, 0.15], size=n),
                "Unplanned_Stop_Flag": np.random.choice([0, 1], p=[0.6, 0.4], size=n),
                "Reefer_Fault_Flag": np.ones(n, dtype=int),
                "Cargo_Integrity_Status": np.full(n, 2, dtype=int)
            })

        def gen_theft(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Temp_Celsius": np.random.normal(6.5, 2.5, n).clip(2.0, 14.0),
                "Shock_G_Force": np.random.normal(4.2, 1.8, n).clip(1.5, 12.0), # Heavy handling
                "Transit_Delay_Hours": np.random.uniform(6.0, 48.0, n),
                "Humidity_Percent": np.random.normal(60.0, 10.0, n).clip(40, 85),
                "Route_Deviation_Km": np.random.uniform(45.0, 280.0, n), # Off-grid diversion
                "Dwell_Time_Minutes": np.random.uniform(180, 720, n),
                "Weight_Variance_Kg": np.random.normal(-120.0, 45.0, n).clip(-450, -25), # High weight loss!
                "Battery_Voltage": np.random.normal(3.6, 0.2, n).clip(3.1, 4.0),
                "Seal_Broken_Flag": np.ones(n, dtype=int),
                "Off_Hours_Access_Flag": np.ones(n, dtype=int),
                "Unplanned_Stop_Flag": np.ones(n, dtype=int),
                "Reefer_Fault_Flag": np.random.choice([0, 1], p=[0.7, 0.3], size=n),
                "Cargo_Integrity_Status": np.full(n, 3, dtype=int)
            })

        dfs = [
            gen_nominal(n_nominal),
            gen_delay(n_delay),
            gen_thermal(n_rare),
            gen_theft(n_hidden)
        ]
        df_all = pd.concat(dfs, ignore_index=True)
        return df_all.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)

    def load_data(
        self,
        use_offline_sim: bool = False,
        max_samples: Optional[int] = None,
        random_seed: int = 42
    ) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        n_load = max_samples or 4000
        df = self._simulate_logistics_data(n_samples=n_load, random_seed=random_seed)
        feature_cols = self.feature_names
        X_raw = df[feature_cols].values
        y = df[self.target_name].values.astype(int)

        if not self._is_fitted:
            self.scaler.fit(X_raw)
            self._scaler_means = self.scaler.mean_
            self._scaler_scales = self.scaler.scale_
            self._is_fitted = True

        X_scaled = self.scaler.transform(X_raw)
        return df, X_scaled, y

    def realism_rules(self, candidates_tensor: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size = candidates_tensor.size(0)
        device = candidates_tensor.device
        valid_mask = torch.ones(batch_size, dtype=torch.bool, device=device)
        penalty = torch.zeros(batch_size, dtype=torch.float32, device=device)

        if self._scaler_means is not None and self._scaler_scales is not None:
            means = torch.tensor(self._scaler_means, device=device, dtype=torch.float32)
            scales = torch.tensor(self._scaler_scales, device=device, dtype=torch.float32)
            raw = candidates_tensor * scales + means

            # Temperature bounds: -40 to 60 C
            temp = raw[:, 0]
            penalty += torch.clamp(-40.0 - temp, min=0.0) * 0.5
            penalty += torch.clamp(temp - 60.0, min=0.0) * 0.5

            # Humidity must be 0-100%
            hum = raw[:, 3]
            penalty += torch.clamp(-hum, min=0.0) * 2.0
            penalty += torch.clamp(hum - 100.0, min=0.0) * 2.0

            # Battery voltage: 2.0 - 5.0 V
            volt = raw[:, 7]
            penalty += torch.clamp(2.0 - volt, min=0.0) * 3.0
            penalty += torch.clamp(volt - 5.0, min=0.0) * 3.0

            valid_mask = penalty < 2.0

        return valid_mask, penalty

    def explain_candidate(
        self,
        candidate_vector: np.ndarray,
        reference_mean: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        if self._scaler_means is not None and self._scaler_scales is not None:
            raw_vals = candidate_vector * self._scaler_scales + self._scaler_means
        else:
            raw_vals = candidate_vector

        feat_dict = {
            name: round(float(raw_vals[i]), 2)
            for i, name in enumerate(self.feature_names)
        }

        anomalies = []
        if feat_dict["Temp_Celsius"] > 12.0:
            anomalies.append(f"Severe thermal excursion to {feat_dict['Temp_Celsius']}°C (Target: 2-8°C).")
        if feat_dict["Weight_Variance_Kg"] < -20.0:
            anomalies.append(f"Significant payload mass loss ({feat_dict['Weight_Variance_Kg']} kg discrepancy).")
        if feat_dict["Route_Deviation_Km"] > 30.0:
            anomalies.append(f"Major geographical corridor excursion ({feat_dict['Route_Deviation_Km']} km off-track).")
        if feat_dict["Seal_Broken_Flag"] > 0.5:
            anomalies.append("Electronic container security seal breached.")
        if feat_dict["Shock_G_Force"] > 3.0:
            anomalies.append(f"Severe mechanical impact shock ({feat_dict['Shock_G_Force']} g).")

        if feat_dict["Seal_Broken_Flag"] > 0.5 or feat_dict["Weight_Variance_Kg"] < -50.0:
            risk = "Critical"
            summary = "Covert high-value cargo breach: Physical seal severed with acute mass deficit."
        elif feat_dict["Temp_Celsius"] > 14.0 or len(anomalies) >= 2:
            risk = "High"
            summary = "Thermal cold-chain compromise threatening pharmaceutical batch stability."
        else:
            risk = "Medium"
            summary = "Transient supply chain disturbance within tolerable margin."

        return {
            "summary": summary,
            "key_anomalies": anomalies or ["Peripheral transit deviation"],
            "risk_level": risk,
            "features": feat_dict
        }
