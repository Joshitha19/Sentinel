"""
Cybersecurity & Network Intrusion Domain Plugin:
Simulates packet flow features, connection dynamics, and authentication telemetry.
Evaluates detection of evasive zero-day APT intrusion and stealth exfiltration.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

from app.domains.base import BaseDomain


class CyberDomain(BaseDomain):
    """Cybersecurity & Zero-Day Intrusion Domain."""

    def __init__(self):
        self._numeric_features = [
            "Packet_Size", "SYN_Rate", "Conn_Duration", "Port_Entropy",
            "Failed_Logins", "Payload_Entropy", "Geo_Drift_Score", "Payload_Anomalies"
        ]
        self._binary_features = [
            "Unusual_Port_Flag", "Encrypted_Tunnel_Flag", "Repeated_Reset_Flag", "Privilege_Escalation_Attempt"
        ]
        self._feature_names = self._numeric_features + self._binary_features
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._scaler_means: Optional[np.ndarray] = None
        self._scaler_scales: Optional[np.ndarray] = None

    @property
    def id(self) -> str:
        return "cyber"

    @property
    def name(self) -> str:
        return "Cybersecurity & Intrusion"

    @property
    def description(self) -> str:
        return (
            "Network packet dynamics and host telemetry benchmark. Evaluates detection of "
            "stealthy APT command-and-control beacons and zero-day data exfiltration."
        )

    @property
    def feature_names(self) -> List[str]:
        return self._feature_names

    @property
    def target_name(self) -> str:
        return "Threat_Category"

    @property
    def class_labels(self) -> Dict[int, str]:
        return {
            0: "Routine Network Traffic",
            1: "Known Probe / Port Scan",
            2: "Distributed SYN Flood (Known Rare)",
            3: "Zero-Day APT Stealth Exfiltration (Hidden Class)"
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
            "Packet_Size": {"type": "continuous", "min": 40.0, "max": 65535.0, "mean": 620.0, "std": 380.0, "unit": "bytes", "description": "Average packet payload length"},
            "SYN_Rate": {"type": "continuous", "min": 0.0, "max": 5000.0, "mean": 12.0, "std": 28.0, "unit": "pkts/s", "description": "SYN requests arrival rate"},
            "Conn_Duration": {"type": "continuous", "min": 0.01, "max": 7200.0, "mean": 14.5, "std": 45.0, "unit": "sec", "description": "TCP connection active duration"},
            "Port_Entropy": {"type": "continuous", "min": 0.0, "max": 8.0, "mean": 1.4, "std": 0.8, "unit": "bits", "description": "Shannon entropy of destination ports"},
            "Failed_Logins": {"type": "continuous", "min": 0.0, "max": 50.0, "mean": 0.05, "std": 0.3, "unit": "count", "description": "Recent failed authentication attempts"},
            "Payload_Entropy": {"type": "continuous", "min": 0.5, "max": 8.0, "mean": 4.1, "std": 1.1, "unit": "bits", "description": "Byte randomness indicating encryption/compression"},
            "Geo_Drift_Score": {"type": "continuous", "min": 0.0, "max": 1.0, "mean": 0.08, "std": 0.15, "unit": "score", "description": "Geographic distance drift from user baseline"},
            "Payload_Anomalies": {"type": "continuous", "min": 0.0, "max": 25.0, "mean": 0.1, "std": 0.6, "unit": "count", "description": "N-gram syntax anomalies in request headers"},
            "Unusual_Port_Flag": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.03, "std": 0.17, "unit": "flag", "description": "Connection to non-standard high port"},
            "Encrypted_Tunnel_Flag": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.12, "std": 0.32, "unit": "flag", "description": "Custom TLS / SSH / DNS tunnel detected"},
            "Repeated_Reset_Flag": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.02, "std": 0.14, "unit": "flag", "description": "Excessive TCP RST flags exchanged"},
            "Privilege_Escalation_Attempt": {"type": "binary", "min": 0.0, "max": 1.0, "mean": 0.01, "std": 0.10, "unit": "flag", "description": "Suspicious sudo/kernel token query"}
        }

    def _simulate_network_data(self, n_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
        np.random.seed(random_seed)
        n_hidden = int(n_samples * 0.015)   # 1.5% Zero-Day APT
        n_rare = int(n_samples * 0.035)     # 3.5% SYN Flood
        n_probe = int(n_samples * 0.10)     # 10% Port Scans
        n_routine = n_samples - n_hidden - n_rare - n_probe

        def generate_routine(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Packet_Size": np.random.normal(550.0, 150.0, n).clip(64, 1500),
                "SYN_Rate": np.random.exponential(5.0, n).clip(0, 50),
                "Conn_Duration": np.random.exponential(8.0, n).clip(0.1, 180),
                "Port_Entropy": np.random.normal(1.2, 0.4, n).clip(0.1, 3.0),
                "Failed_Logins": np.random.choice([0, 1], p=[0.97, 0.03], size=n),
                "Payload_Entropy": np.random.normal(3.8, 0.6, n).clip(1.0, 5.5),
                "Geo_Drift_Score": np.random.beta(1, 10, n),
                "Payload_Anomalies": np.random.choice([0, 1], p=[0.95, 0.05], size=n),
                "Unusual_Port_Flag": np.random.choice([0, 1], p=[0.98, 0.02], size=n),
                "Encrypted_Tunnel_Flag": np.random.choice([0, 1], p=[0.90, 0.10], size=n),
                "Repeated_Reset_Flag": np.random.choice([0, 1], p=[0.98, 0.02], size=n),
                "Privilege_Escalation_Attempt": np.zeros(n, dtype=int),
                "Threat_Category": np.zeros(n, dtype=int)
            })

        def generate_probes(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Packet_Size": np.random.normal(60.0, 10.0, n).clip(40, 100),
                "SYN_Rate": np.random.normal(60.0, 20.0, n).clip(20, 150),
                "Conn_Duration": np.random.uniform(0.01, 1.0, n),
                "Port_Entropy": np.random.normal(5.8, 0.5, n).clip(4.0, 7.5),
                "Failed_Logins": np.random.choice([0, 1, 2], p=[0.80, 0.15, 0.05], size=n),
                "Payload_Entropy": np.random.normal(2.0, 0.4, n).clip(0.5, 3.5),
                "Geo_Drift_Score": np.random.beta(2, 5, n),
                "Payload_Anomalies": np.random.poisson(0.5, n).clip(0, 3),
                "Unusual_Port_Flag": np.random.choice([0, 1], p=[0.3, 0.7], size=n),
                "Encrypted_Tunnel_Flag": np.zeros(n, dtype=int),
                "Repeated_Reset_Flag": np.random.choice([0, 1], p=[0.4, 0.6], size=n),
                "Privilege_Escalation_Attempt": np.zeros(n, dtype=int),
                "Threat_Category": np.ones(n, dtype=int)
            })

        def generate_syn_flood(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Packet_Size": np.random.normal(54.0, 6.0, n).clip(40, 80),
                "SYN_Rate": np.random.normal(2200.0, 450.0, n).clip(800, 4500),
                "Conn_Duration": np.random.uniform(0.001, 0.2, n),
                "Port_Entropy": np.random.normal(1.1, 0.3, n).clip(0.1, 2.0),
                "Failed_Logins": np.zeros(n, dtype=int),
                "Payload_Entropy": np.random.normal(1.2, 0.3, n).clip(0.5, 2.5),
                "Geo_Drift_Score": np.random.uniform(0.6, 0.98, n),
                "Payload_Anomalies": np.random.poisson(2.0, n).clip(0, 8),
                "Unusual_Port_Flag": np.random.choice([0, 1], p=[0.8, 0.2], size=n),
                "Encrypted_Tunnel_Flag": np.zeros(n, dtype=int),
                "Repeated_Reset_Flag": np.ones(n, dtype=int),
                "Privilege_Escalation_Attempt": np.zeros(n, dtype=int),
                "Threat_Category": np.full(n, 2, dtype=int)
            })

        def generate_apt_stealth(n: int) -> pd.DataFrame:
            return pd.DataFrame({
                "Packet_Size": np.random.normal(1420.0, 60.0, n).clip(1200, 1500),
                "SYN_Rate": np.random.uniform(1.0, 4.0, n),
                "Conn_Duration": np.random.normal(3200.0, 600.0, n).clip(1800, 7200),
                "Port_Entropy": np.random.normal(0.8, 0.2, n).clip(0.2, 1.5),
                "Failed_Logins": np.random.choice([0, 1], p=[0.7, 0.3], size=n),
                "Payload_Entropy": np.random.normal(7.85, 0.08, n).clip(7.6, 8.0), # High entropy encrypted exfiltration
                "Geo_Drift_Score": np.random.uniform(0.75, 0.99, n),
                "Payload_Anomalies": np.random.poisson(4.5, n).clip(1, 15),
                "Unusual_Port_Flag": np.random.choice([0, 1], p=[0.2, 0.8], size=n),
                "Encrypted_Tunnel_Flag": np.ones(n, dtype=int),
                "Repeated_Reset_Flag": np.zeros(n, dtype=int),
                "Privilege_Escalation_Attempt": np.random.choice([0, 1], p=[0.4, 0.6], size=n),
                "Threat_Category": np.full(n, 3, dtype=int)
            })

        dfs = [
            generate_routine(n_routine),
            generate_probes(n_probe),
            generate_syn_flood(n_rare),
            generate_apt_stealth(n_hidden)
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
        df = self._simulate_network_data(n_samples=n_load, random_seed=random_seed)
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

            # Packet size must be between 20 and 65535
            pkt_size = raw[:, 0]
            penalty += torch.clamp(20.0 - pkt_size, min=0.0) * 0.1
            penalty += torch.clamp(pkt_size - 65535.0, min=0.0) * 0.1

            # SYN rate cannot be negative
            syn_rate = raw[:, 1]
            penalty += torch.clamp(-syn_rate, min=0.0) * 2.0

            # Payload entropy must be <= 8.0
            entropy = raw[:, 5]
            penalty += torch.clamp(entropy - 8.0, min=0.0) * 10.0
            penalty += torch.clamp(0.0 - entropy, min=0.0) * 5.0

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
        if feat_dict["Payload_Entropy"] > 7.7:
            anomalies.append(f"Near-maximum payload entropy ({feat_dict['Payload_Entropy']} bits), indicating covert encrypted payload.")
        if feat_dict["SYN_Rate"] > 300:
            anomalies.append(f"High-frequency SYN packet arrival ({feat_dict['SYN_Rate']} pkts/s).")
        if feat_dict["Conn_Duration"] > 1800:
            anomalies.append(f"Persistent long-lived TCP tunnel ({feat_dict['Conn_Duration'] / 60:.1f} minutes).")
        if feat_dict["Geo_Drift_Score"] > 0.8:
            anomalies.append(f"Severe geographic IP divergence (Drift {feat_dict['Geo_Drift_Score']}).")
        if feat_dict["Privilege_Escalation_Attempt"] > 0.5:
            anomalies.append("Root privilege escalation token query detected.")

        if len(anomalies) >= 3 or feat_dict["Payload_Entropy"] > 7.8:
            risk = "Critical"
            summary = "Advanced Persistent Threat (APT) signature with stealth encrypted exfiltration tunnel."
        elif len(anomalies) >= 1:
            risk = "High"
            summary = "Evasive cyber threat pattern showing atypical packet entropy and connection duration."
        else:
            risk = "Medium"
            summary = "Mild network anomaly within peripheral operational tolerance."

        return {
            "summary": summary,
            "key_anomalies": anomalies or ["Peripheral deviation across multiple network channels"],
            "risk_level": risk,
            "features": feat_dict
        }
