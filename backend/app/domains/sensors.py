"""
Industrial IoT Equipment Sensors Domain Plugin:
Simulates high-frequency industrial telemetry for rotating machinery (turbines/pumps).
Evaluates early detection of catastrophic cavitation and bearing fracture before failure.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

from app.domains.base import BaseDomain


class SensorsDomain(BaseDomain):
    """Industrial Equipment Telemetry Domain."""

    def __init__(self):
        self._feature_names = [
            "Vibration_X", "Vibration_Y", "Vibration_Z",
            "Bearing_Temp", "Motor_Current", "Supply_Voltage",
            "Acoustic_Emission", "Lube_Oil_Pressure", "Rotational_RPM",
            "Ambient_Temp"
        ]
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._scaler_means: Optional[np.ndarray] = None
        self._scaler_scales: Optional[np.ndarray] = None

    @property
    def id(self) -> str:
        return "sensors"

    @property
    def name(self) -> str:
        return "Industrial IoT & Sensors"

    @property
    def description(self) -> str:
        return (
            "Rotating machinery telemetry benchmark. Evaluates detection of sudden catastrophic "
            "cavitation shockwaves and mechanical fracture hidden within continuous sensor streams."
        )

    @property
    def feature_names(self) -> List[str]:
        return self._feature_names

    @property
    def target_name(self) -> str:
        return "Machinery_State"

    @property
    def class_labels(self) -> Dict[int, str]:
        return {
            0: "Nominal Operation",
            1: "Minor Bearing Wear",
            2: "Severe Rotor Imbalance (Known Rare)",
            3: "Cavitation Shockwave Failure (Hidden Class / Zero-Shot)"
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
            "Vibration_X": {"type": "continuous", "min": 0.0, "max": 25.0, "mean": 2.1, "std": 0.8, "unit": "mm/s RMS", "description": "Radial X-axis acceleration RMS"},
            "Vibration_Y": {"type": "continuous", "min": 0.0, "max": 25.0, "mean": 2.3, "std": 0.9, "unit": "mm/s RMS", "description": "Radial Y-axis acceleration RMS"},
            "Vibration_Z": {"type": "continuous", "min": 0.0, "max": 30.0, "mean": 1.6, "std": 0.7, "unit": "mm/s RMS", "description": "Axial Z-axis acceleration RMS"},
            "Bearing_Temp": {"type": "continuous", "min": 20.0, "max": 140.0, "mean": 58.0, "std": 8.5, "unit": "°C", "description": "Drive-end roller bearing surface temperature"},
            "Motor_Current": {"type": "continuous", "min": 5.0, "max": 120.0, "mean": 42.0, "std": 6.2, "unit": "Amperes", "description": "Stator current consumption"},
            "Supply_Voltage": {"type": "continuous", "min": 360.0, "max": 440.0, "mean": 400.0, "std": 5.5, "unit": "Volts", "description": "Three-phase RMS supply line voltage"},
            "Acoustic_Emission": {"type": "continuous", "min": 30.0, "max": 130.0, "mean": 52.0, "std": 7.0, "unit": "dB", "description": "High-frequency ultrasonic structural wave emission"},
            "Lube_Oil_Pressure": {"type": "continuous", "min": 0.5, "max": 8.0, "mean": 4.5, "std": 0.6, "unit": "Bar", "description": "Hydraulic lubrication system pressure"},
            "Rotational_RPM": {"type": "continuous", "min": 800.0, "max": 3600.0, "mean": 1780.0, "std": 45.0, "unit": "RPM", "description": "Main shaft encoder rotational speed"},
            "Ambient_Temp": {"type": "continuous", "min": 5.0, "max": 55.0, "mean": 26.0, "std": 5.0, "unit": "°C", "description": "Ambient plant floor atmospheric temperature"}
        }

    def _simulate_sensor_data(self, n_samples: int = 10000, random_seed: int = 42) -> pd.DataFrame:
        np.random.seed(random_seed)
        n_hidden = int(n_samples * 0.015)  # 1.5% Cavitation Shockwave (Hidden)
        n_rare = int(n_samples * 0.035)    # 3.5% Severe Imbalance (Known Rare)
        n_wear = int(n_samples * 0.12)     # 12% Minor Wear
        n_nominal = n_samples - n_rare - n_hidden - n_wear

        records = []

        # 1. Nominal
        for _ in range(n_nominal):
            records.append({
                "Vibration_X": np.random.normal(2.1, 0.4),
                "Vibration_Y": np.random.normal(2.3, 0.4),
                "Vibration_Z": np.random.normal(1.6, 0.3),
                "Bearing_Temp": np.random.normal(55, 4),
                "Motor_Current": np.random.normal(41, 3),
                "Supply_Voltage": np.random.normal(400, 3),
                "Acoustic_Emission": np.random.normal(50, 4),
                "Lube_Oil_Pressure": np.random.normal(4.6, 0.3),
                "Rotational_RPM": np.random.normal(1785, 15),
                "Ambient_Temp": np.random.normal(25, 3),
                "Machinery_State": 0
            })

        # 2. Minor Wear
        for _ in range(n_wear):
            records.append({
                "Vibration_X": np.random.normal(3.8, 0.6),
                "Vibration_Y": np.random.normal(4.1, 0.7),
                "Vibration_Z": np.random.normal(2.5, 0.5),
                "Bearing_Temp": np.random.normal(68, 6),
                "Motor_Current": np.random.normal(45, 4),
                "Supply_Voltage": np.random.normal(399, 4),
                "Acoustic_Emission": np.random.normal(66, 6),
                "Lube_Oil_Pressure": np.random.normal(4.2, 0.4),
                "Rotational_RPM": np.random.normal(1775, 20),
                "Ambient_Temp": np.random.normal(26, 4),
                "Machinery_State": 1
            })

        # 3. Severe Rotor Imbalance (Known Rare)
        for _ in range(n_rare):
            records.append({
                "Vibration_X": np.random.normal(9.5, 1.8),
                "Vibration_Y": np.random.normal(10.2, 2.0),
                "Vibration_Z": np.random.normal(6.8, 1.4),
                "Bearing_Temp": np.random.normal(89, 8),
                "Motor_Current": np.random.normal(64, 7),
                "Supply_Voltage": np.random.normal(395, 6),
                "Acoustic_Emission": np.random.normal(82, 8),
                "Lube_Oil_Pressure": np.random.normal(3.8, 0.5),
                "Rotational_RPM": np.random.normal(1730, 45),
                "Ambient_Temp": np.random.normal(27, 4),
                "Machinery_State": 2
            })

        # 4. Cavitation Shockwave Failure (Hidden Class)
        for _ in range(n_hidden):
            records.append({
                "Vibration_X": np.random.normal(4.5, 1.0),
                "Vibration_Y": np.random.normal(5.0, 1.2),
                "Vibration_Z": np.random.normal(14.5, 3.0), # Extreme axial shock
                "Bearing_Temp": np.random.normal(95, 10),
                "Motor_Current": np.random.normal(78, 10),   # Severe cavitation drag
                "Supply_Voltage": np.random.normal(392, 8),
                "Acoustic_Emission": np.random.uniform(98.0, 125.0), # Ultrasonic explosion
                "Lube_Oil_Pressure": np.random.uniform(1.0, 2.2),    # Acute oil pressure collapse
                "Rotational_RPM": np.random.normal(1640, 70),
                "Ambient_Temp": np.random.normal(28, 4),
                "Machinery_State": 3
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
        df = self._simulate_sensor_data(n_samples=samples_to_gen, random_seed=random_seed)

        features = df[self._feature_names].copy()
        y = df[self.target_name].to_numpy(dtype=int)

        X = self.scaler.fit_transform(features)
        self._is_fitted = True
        self._scaler_means = self.scaler.mean_
        self._scaler_scales = self.scaler.scale_

        return df, X, y

    def realism_rules(self, candidates_tensor: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size = candidates_tensor.shape[0]
        device = candidates_tensor.device

        penalties = torch.zeros(batch_size, device=device)
        valid_mask = torch.ones(batch_size, dtype=torch.bool, device=device)

        if self._is_fitted and self._scaler_means is not None:
            # Physical bounds
            for i, feat_name in enumerate(self._feature_names):
                mean = float(self._scaler_means[i])
                scale = float(self._scaler_scales[i])
                raw_val = candidates_tensor[:, i] * scale + mean

                min_limit = 0.0
                if feat_name == "Supply_Voltage":
                    min_limit = 200.0
                elif feat_name == "Rotational_RPM":
                    min_limit = 400.0

                viol = raw_val < min_limit
                valid_mask = valid_mask & (~viol)
                penalties += torch.relu(min_limit - raw_val) / (scale + 1e-6)

        return valid_mask, penalties

    def explain_candidate(
        self,
        candidate_vector: np.ndarray,
        reference_mean: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        if self._is_fitted and self._scaler_means is not None:
            raw_vals = candidate_vector * self._scaler_scales + self._scaler_means
        else:
            raw_vals = candidate_vector

        vib_z = float(raw_vals[2])
        bearing_t = float(raw_vals[3])
        current = float(raw_vals[4])
        acoustic = float(raw_vals[6])
        oil_p = float(raw_vals[7])
        rpm = float(raw_vals[8])

        anomalies = []
        if acoustic > 95.0:
            anomalies.append(f"High-frequency ultrasonic shock emission ({acoustic:.1f} dB)")
        if vib_z > 8.0:
            anomalies.append(f"Severe axial Z-axis vibration thrust ({vib_z:.2f} mm/s)")
        if oil_p < 2.5:
            anomalies.append(f"Critical lubrication oil pressure loss ({oil_p:.2f} bar)")
        if bearing_t > 85.0:
            anomalies.append(f"Elevated bearing thermal runaway ({bearing_t:.1f} °C)")

        risk = "Critical" if (acoustic > 100 or vib_z > 10.0 or oil_p < 2.0) else ("High" if len(anomalies) >= 2 else "Medium")

        return {
            "summary": (
                f"Synthetic Turbomachinery Telemetry: Acoustic {acoustic:.1f} dB, "
                f"Axial Vib {vib_z:.2f} mm/s, Oil Pressure {oil_p:.2f} bar at {rpm:.0f} RPM."
            ),
            "key_anomalies": anomalies or ["Micro-harmonic resonance drift across radial axes"],
            "risk_level": risk,
            "metrics": {
                "acoustic_db": round(acoustic, 1),
                "vibration_z_rms": round(vib_z, 2),
                "bearing_temp_c": round(bearing_t, 1),
                "oil_pressure_bar": round(oil_p, 2),
                "rpm": round(rpm, 0)
            }
        }
