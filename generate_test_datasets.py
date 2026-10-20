"""
Generates benchmark CSV datasets for SENTINEL:
1. sentinel_finance_test.csv (3,000 rows, 75 fraud: card_testing, account_takeover, geo_impossible, plus novel_mule_structuring and novel_dormant_burst)
2. sentinel_health_test.csv (2,000 rows, 46 rare: adult_onset_stills, hlh, fabry_disease, plus novel_unclassified_cluster)
3. sentinel_finance_rare_events_tail1.4x.csv (200 rows, 4 aggressive-tail event types)
4. 50 domain test datasets in test_datasets/ (10 per domain for health, finance, cyber, sensors, logistics)
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)

def generate_benchmark_finance():
    n_total = 3000
    n_fraud = 75
    n_normal = n_total - n_fraud

    # Normal transactions
    amounts_norm = np.random.lognormal(mean=3.8, sigma=0.9, size=n_normal)
    amounts_norm = np.clip(amounts_norm, 2.5, 450.0).round(2)
    velocity_norm = np.random.poisson(lam=2.5, size=n_normal)
    velocity_norm = np.clip(velocity_norm, 1, 8)
    geo_norm = np.random.exponential(scale=45.0, size=n_normal).round(1)
    geo_norm = np.clip(geo_norm, 0.5, 300.0)
    foreign_norm = np.random.binomial(n=1, p=0.08, size=n_normal)
    age_norm = np.random.randint(45, 1800, size=n_normal)
    pin_norm = np.random.choice([0, 1], size=n_normal, p=[0.92, 0.08])
    risk_norm = np.random.choice([0, 1], size=n_normal, p=[0.88, 0.12])

    df_normal = pd.DataFrame({
        "Amount": amounts_norm,
        "Velocity_24h": velocity_norm,
        "Geo_Distance_Km": geo_norm,
        "Foreign_Tx": foreign_norm,
        "Account_Age_Days": age_norm,
        "Failed_PIN_Attempts": pin_norm,
        "Risk_Category": risk_norm,
        "is_fraud": 0,
        "fraud_type": "normal"
    })

    # Fraud types distribution:
    # 45 known fraud: 15 card_testing, 15 account_takeover, 15 geo_impossible
    # 30 held-out novel: 15 novel_mule_structuring, 15 novel_dormant_burst
    fraud_rows = []

    # 1. card_testing (15)
    for _ in range(15):
        fraud_rows.append({
            "Amount": round(float(np.random.uniform(0.99, 4.99)), 2),
            "Velocity_24h": int(np.random.randint(18, 45)),
            "Geo_Distance_Km": round(float(np.random.uniform(5.0, 80.0)), 1),
            "Foreign_Tx": int(np.random.choice([0, 1], p=[0.4, 0.6])),
            "Account_Age_Days": int(np.random.randint(1, 14)),
            "Failed_PIN_Attempts": int(np.random.randint(2, 5)),
            "Risk_Category": 2,
            "is_fraud": 1,
            "fraud_type": "card_testing"
        })

    # 2. account_takeover (15)
    for _ in range(15):
        fraud_rows.append({
            "Amount": round(float(np.random.uniform(1800.0, 5500.0)), 2),
            "Velocity_24h": int(np.random.randint(10, 25)),
            "Geo_Distance_Km": round(float(np.random.uniform(400.0, 2500.0)), 1),
            "Foreign_Tx": 1,
            "Account_Age_Days": int(np.random.randint(200, 900)),
            "Failed_PIN_Attempts": int(np.random.randint(3, 6)),
            "Risk_Category": 2,
            "is_fraud": 1,
            "fraud_type": "account_takeover"
        })

    # 3. geo_impossible (15)
    for _ in range(15):
        fraud_rows.append({
            "Amount": round(float(np.random.uniform(350.0, 2200.0)), 2),
            "Velocity_24h": int(np.random.randint(8, 20)),
            "Geo_Distance_Km": round(float(np.random.uniform(5000.0, 14000.0)), 1),
            "Foreign_Tx": 1,
            "Account_Age_Days": int(np.random.randint(60, 500)),
            "Failed_PIN_Attempts": int(np.random.choice([0, 1])),
            "Risk_Category": 2,
            "is_fraud": 1,
            "fraud_type": "geo_impossible"
        })

    # 4. novel_mule_structuring (15) - HELD OUT
    for _ in range(15):
        fraud_rows.append({
            "Amount": round(float(np.random.uniform(940.0, 995.0)), 2),
            "Velocity_24h": int(np.random.randint(12, 28)),
            "Geo_Distance_Km": round(float(np.random.uniform(80.0, 450.0)), 1),
            "Foreign_Tx": 0,
            "Account_Age_Days": int(np.random.randint(5, 25)),
            "Failed_PIN_Attempts": 0,
            "Risk_Category": 1,
            "is_fraud": 1,
            "fraud_type": "novel_mule_structuring"
        })

    # 5. novel_dormant_burst (15) - HELD OUT
    for _ in range(15):
        fraud_rows.append({
            "Amount": round(float(np.random.uniform(3200.0, 8900.0)), 2),
            "Velocity_24h": int(np.random.randint(15, 35)),
            "Geo_Distance_Km": round(float(np.random.uniform(200.0, 1800.0)), 1),
            "Foreign_Tx": 1,
            "Account_Age_Days": int(np.random.randint(1200, 2400)),
            "Failed_PIN_Attempts": 1,
            "Risk_Category": 2,
            "is_fraud": 1,
            "fraud_type": "novel_dormant_burst"
        })

    df_fraud = pd.DataFrame(fraud_rows)
    df_combined = pd.concat([df_normal, df_fraud], ignore_index=True)
    df_combined = df_combined.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df_combined.to_csv("sentinel_finance_test.csv", index=False)
    print("Created sentinel_finance_test.csv with shape:", df_combined.shape)


def generate_benchmark_health():
    n_total = 2000
    n_rare = 46
    n_normal = n_total - n_rare
    np.random.seed(42)

    # Normal / common viral patients (1954)
    ages = np.random.randint(20, 78, size=n_normal)
    sexes = np.random.choice(["M", "F"], size=n_normal, p=[0.48, 0.52])
    sbp = np.random.normal(122, 12, size=n_normal).round(0).astype(int)
    sbp = np.clip(sbp, 95, 160)
    hr = np.random.normal(76, 10, size=n_normal).round(0).astype(int)
    hr = np.clip(hr, 55, 105)
    glucose = np.random.normal(98, 18, size=n_normal).round(1)
    glucose = np.clip(glucose, 65.0, 155.0)
    wbc = np.random.normal(7.2, 1.8, size=n_normal).round(1)
    wbc = np.clip(wbc, 3.8, 12.0)
    # Hemoglobin: normal distribution strictly clipped to max 18.0
    hgb = np.random.normal(14.2, 1.4, size=n_normal).round(2)
    hgb = np.clip(hgb, 11.0, 18.0)
    platelets = np.random.normal(245, 45, size=n_normal).round(0).astype(int)
    platelets = np.clip(platelets, 140, 420)
    ferritin = np.random.exponential(110, size=n_normal).round(0).astype(int)
    ferritin = np.clip(ferritin, 20, 380)
    crp = np.random.exponential(2.2, size=n_normal).round(2)
    crp = np.clip(crp, 0.3, 8.0)
    fever_days = np.random.choice([0, 1, 2, 3], size=n_normal, p=[0.78, 0.14, 0.06, 0.02])
    fatigue_scores = np.random.choice(range(11), size=n_normal, p=[0.30, 0.25, 0.16, 0.10, 0.07, 0.05, 0.03, 0.02, 0.01, 0.005, 0.005])
    weight_loss = np.random.exponential(0.6, size=n_normal).round(1)
    weight_loss = np.clip(weight_loss, 0.0, 3.5)

    df_normal = pd.DataFrame({
        "age": ages,
        "sex": sexes,
        "systolic_bp": sbp,
        "heart_rate": hr,
        "glucose": glucose,
        "wbc_count": wbc,
        "hemoglobin": hgb,
        "platelets_k": platelets,
        "ferritin_ng_ml": ferritin,
        "crp": crp,
        "fever_days": fever_days,
        "fatigue_score": fatigue_scores,
        "joint_pain": np.random.choice([0, 1], size=n_normal, p=[0.88, 0.12]),
        "rash": np.random.choice([0, 1], size=n_normal, p=[0.93, 0.07]), # 7% prevalence
        "enlarged_spleen": np.random.choice([0, 1], size=n_normal, p=[0.98, 0.02]),
        "neuro_symptoms": np.random.choice([0, 1], size=n_normal, p=[0.95, 0.05]),
        "weight_loss_kg": weight_loss,
        "is_rare_disease": 0,
        "rare_condition": np.random.choice(["healthy_baseline", "common_viral"], size=n_normal, p=[0.68, 0.32])
    })

    rare_rows = []

    # 1. adult_onset_stills (12)
    for _ in range(12):
        rare_rows.append({
            "age": int(np.random.randint(22, 45)),
            "sex": str(np.random.choice(["M", "F"])),
            "systolic_bp": int(np.random.randint(110, 135)),
            "heart_rate": int(np.random.randint(95, 125)),
            "glucose": round(float(np.random.uniform(85, 130)), 1),
            "wbc_count": round(float(np.random.uniform(16.5, 28.0)), 1),
            "hemoglobin": round(float(np.random.uniform(9.5, 12.5)), 2),
            "platelets_k": int(np.random.randint(380, 680)),
            "ferritin_ng_ml": int(np.random.randint(4200, 14500)),
            "crp": round(float(np.random.uniform(45.0, 160.0)), 2),
            "fever_days": int(np.random.randint(10, 24)),
            "fatigue_score": int(np.random.randint(6, 10)),
            "joint_pain": 1,
            "rash": 1,
            "enlarged_spleen": 1,
            "neuro_symptoms": 0,
            "weight_loss_kg": round(float(np.random.uniform(2.5, 7.5)), 1),
            "is_rare_disease": 1,
            "rare_condition": "adult_onset_stills"
        })

    # 2. hlh (Hemophagocytic Lymphohistiocytosis) (12)
    for _ in range(12):
        rare_rows.append({
            "age": int(np.random.randint(19, 58)),
            "sex": str(np.random.choice(["M", "F"])),
            "systolic_bp": int(np.random.randint(88, 115)),
            "heart_rate": int(np.random.randint(105, 140)),
            "glucose": round(float(np.random.uniform(80, 125)), 1),
            "wbc_count": round(float(np.random.uniform(1.2, 2.8)), 1),
            "hemoglobin": round(float(np.random.uniform(7.5, 10.5)), 2),
            "platelets_k": int(np.random.randint(18, 55)),
            "ferritin_ng_ml": int(np.random.randint(8500, 26000)),
            "crp": round(float(np.random.uniform(65.0, 210.0)), 2),
            "fever_days": int(np.random.randint(14, 30)),
            "fatigue_score": int(np.random.randint(7, 10)),
            "joint_pain": 0,
            "rash": 1,
            "enlarged_spleen": 1,
            "neuro_symptoms": 0,
            "weight_loss_kg": round(float(np.random.uniform(4.0, 10.0)), 1),
            "is_rare_disease": 1,
            "rare_condition": "hlh"
        })

    # 3. fabry_disease (10)
    for _ in range(10):
        rare_rows.append({
            "age": int(np.random.randint(24, 52)),
            "sex": str(np.random.choice(["M", "F"])),
            "systolic_bp": int(np.random.randint(130, 160)),
            "heart_rate": int(np.random.randint(52, 74)),
            "glucose": round(float(np.random.uniform(90, 135)), 1),
            "wbc_count": round(float(np.random.uniform(5.5, 9.2)), 1),
            "hemoglobin": round(float(np.random.uniform(12.0, 15.2)), 2),
            "platelets_k": int(np.random.randint(180, 310)),
            "ferritin_ng_ml": int(np.random.randint(80, 320)),
            "crp": round(float(np.random.uniform(0.5, 4.0)), 2),
            "fever_days": 0,
            "fatigue_score": int(np.random.randint(6, 9)),
            "joint_pain": 0,
            "rash": 1,
            "enlarged_spleen": 0,
            "neuro_symptoms": 1,
            "weight_loss_kg": round(float(np.random.uniform(0.0, 2.5)), 1),
            "is_rare_disease": 1,
            "rare_condition": "fabry_disease"
        })

    # 4. novel_unclassified_cluster (12) - STRICTLY HELD OUT FROM TRAINING
    for _ in range(12):
        rare_rows.append({
            "age": int(np.random.randint(30, 65)),
            "sex": str(np.random.choice(["M", "F"])),
            "systolic_bp": int(np.random.randint(118, 132)),
            "heart_rate": int(np.random.randint(72, 88)),
            "glucose": round(float(np.random.uniform(95, 140)), 1),
            "wbc_count": round(float(np.random.uniform(5.5, 11.5)), 1),
            "hemoglobin": round(float(np.random.uniform(11.8, 14.5)), 2),
            "platelets_k": int(np.random.randint(130, 170)), # Held-out feature profile
            "ferritin_ng_ml": int(np.random.randint(600, 1200)), # Held-out feature profile
            "crp": round(float(np.random.uniform(0.8, 3.2)), 2), # Normal CRP
            "fever_days": int(np.random.randint(3, 8)), # Low-grade fever
            "fatigue_score": int(np.random.randint(5, 8)),
            "joint_pain": int(np.random.choice([0, 1])),
            "rash": int(np.random.choice([0, 1])),
            "enlarged_spleen": int(np.random.choice([0, 1])),
            "neuro_symptoms": 1, # Neuro symptoms present
            "weight_loss_kg": round(float(np.random.uniform(6.0, 14.0)), 1), # Weight loss 6-14 kg
            "is_rare_disease": 1,
            "rare_condition": "novel_unclassified_cluster"
        })

    df_rare = pd.DataFrame(rare_rows)
    df_combined = pd.concat([df_normal, df_rare], ignore_index=True)
    df_combined = df_combined.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df_combined.to_csv("sentinel_health_test.csv", index=False)
    print("Created sentinel_health_test.csv with shape:", df_combined.shape)


def generate_tail_showcase():
    # 200 rows, 4 aggressive-tail event types (50 rows per archetype)
    rows = []
    archetypes = [
        ("Archetype_1_Extreme_Amount_Divergence", 1),
        ("Archetype_2_Coupled_Velocity_Geo_Cluster", 2),
        ("Archetype_3_High_Variance_Latency_Incursion", 3),
        ("Archetype_4_Asymmetric_PIN_Burst", 4)
    ]

    for arch_name, arch_id in archetypes:
        for _ in range(50):
            if arch_id == 1:
                amt = round(float(np.random.uniform(6200.0, 14500.0)), 2)
                vel = int(np.random.randint(4, 12))
                geo = round(float(np.random.uniform(120.0, 600.0)), 1)
                for_tx = 1
                age = int(np.random.randint(30, 180))
                pin = 1
            elif arch_id == 2:
                amt = round(float(np.random.uniform(850.0, 2400.0)), 2)
                vel = int(np.random.randint(28, 55))
                geo = round(float(np.random.uniform(6500.0, 15000.0)), 1)
                for_tx = 1
                age = int(np.random.randint(10, 90))
                pin = 0
            elif arch_id == 3:
                amt = round(float(np.random.uniform(1900.0, 4800.0)), 2)
                vel = int(np.random.randint(14, 30))
                geo = round(float(np.random.uniform(1500.0, 4500.0)), 1)
                for_tx = 1
                age = int(np.random.randint(3, 20))
                pin = 2
            else:
                amt = round(float(np.random.uniform(300.0, 1200.0)), 2)
                vel = int(np.random.randint(20, 42))
                geo = round(float(np.random.uniform(50.0, 350.0)), 1)
                for_tx = 0
                age = int(np.random.randint(400, 1500))
                pin = int(np.random.randint(4, 7))

            p_val = round(float(np.random.uniform(0.78, 0.94)), 3)
            nov = round(float(np.random.uniform(88.5, 99.2)), 1)
            conf_p = round(float(np.random.uniform(0.0012, 0.0185)), 4)

            rows.append({
                "Amount": amt,
                "Velocity_24h": vel,
                "Geo_Distance_Km": geo,
                "Foreign_Tx": for_tx,
                "Account_Age_Days": age,
                "Failed_PIN_Attempts": pin,
                "Risk_Category": 2,
                "plausibility": p_val,
                "novelty": nov,
                "conformal_p_value": conf_p,
                "archetype_id": arch_id,
                "archetype_name": arch_name
            })

    df_tail = pd.DataFrame(rows)
    df_tail.to_csv("sentinel_finance_rare_events_tail1.4x.csv", index=False)
    print("Created sentinel_finance_rare_events_tail1.4x.csv with shape:", df_tail.shape)


def generate_50_domain_datasets():
    os.makedirs("test_datasets", exist_ok=True)
    domains = ["health", "finance", "cyber", "sensors", "logistics"]

    for d in domains:
        for idx in range(1, 11):
            seed = 1000 * (domains.index(d) + 1) + idx
            np.random.seed(seed)
            filename = f"test_datasets/{d}_test_{idx:02d}.csv"
            n_rows = 300 + idx * 50

            if d == "health":
                df = pd.DataFrame({
                    "Age": np.random.randint(18, 85, n_rows),
                    "Systolic_BP": np.random.normal(122, 14, n_rows).round(0).astype(int),
                    "Heart_Rate": np.random.normal(76, 12, n_rows).round(0).astype(int),
                    "Glucose": np.random.normal(102, 22, n_rows).round(1),
                    "WBC_Count": np.random.normal(7.4, 2.2, n_rows).round(1),
                    "Platelets": np.random.normal(240, 50, n_rows).round(0).astype(int),
                    "Ferritin": np.random.exponential(140, n_rows).round(1),
                    "Troponin": np.random.exponential(0.025, n_rows).round(3),
                    "Fever": np.random.choice([0, 1], n_rows, p=[0.7, 0.3]),
                    "Dyspnea": np.random.choice([0, 1], n_rows, p=[0.85, 0.15]),
                    "is_rare_disease": np.random.choice([0, 1], n_rows, p=[0.96, 0.04])
                })
            elif d == "finance":
                df = pd.DataFrame({
                    "Amount": np.random.exponential(120, n_rows).round(2),
                    "Velocity_24h": np.random.poisson(3, n_rows),
                    "Geo_Distance_Km": np.random.exponential(50, n_rows).round(1),
                    "Foreign_Tx": np.random.binomial(1, 0.1, n_rows),
                    "Account_Age_Days": np.random.randint(1, 1500, n_rows),
                    "Failed_PIN_Attempts": np.random.choice([0, 1, 2], n_rows, p=[0.9, 0.08, 0.02]),
                    "is_fraud": np.random.choice([0, 1], n_rows, p=[0.97, 0.03])
                })
            elif d == "cyber":
                df = pd.DataFrame({
                    "Packet_Size": np.random.normal(720, 250, n_rows).round(0).astype(int),
                    "SYN_Rate": np.random.normal(240, 80, n_rows).round(0).astype(int),
                    "Conn_Duration": np.random.exponential(150, n_rows).round(1),
                    "Port_Entropy": np.random.uniform(0.1, 0.95, n_rows).round(3),
                    "Payload_Entropy": np.random.uniform(2.5, 7.95, n_rows).round(3),
                    "Geo_Drift_Score": np.random.uniform(0.0, 1.0, n_rows).round(3),
                    "is_intrusion": np.random.choice([0, 1], n_rows, p=[0.96, 0.04])
                })
            elif d == "sensors":
                df = pd.DataFrame({
                    "Vibration_X": np.random.normal(1.2, 0.35, n_rows).round(3),
                    "Bearing_Temp": np.random.normal(68.0, 8.5, n_rows).round(1),
                    "Motor_Current": np.random.normal(18.5, 3.2, n_rows).round(1),
                    "Supply_Voltage": np.random.normal(398.0, 5.0, n_rows).round(1),
                    "Acoustic_Emission": np.random.normal(45.0, 12.0, n_rows).round(1),
                    "Rotational_RPM": np.random.normal(2980, 45, n_rows).round(0).astype(int),
                    "is_fault": np.random.choice([0, 1], n_rows, p=[0.96, 0.04])
                })
            else:
                df = pd.DataFrame({
                    "Temp_Celsius": np.random.normal(4.2, 1.5, n_rows).round(1),
                    "Shock_G_Force": np.random.exponential(1.2, n_rows).round(2),
                    "Transit_Delay_Hours": np.random.exponential(4.0, n_rows).round(1),
                    "Humidity_Percent": np.random.normal(62.0, 8.0, n_rows).round(1),
                    "Route_Deviation_Km": np.random.exponential(12.0, n_rows).round(1),
                    "Seal_Broken_Flag": np.random.binomial(1, 0.03, n_rows),
                    "is_spoilage": np.random.choice([0, 1], n_rows, p=[0.96, 0.04])
                })

            df.to_csv(filename, index=False)

    print("Created 50 test datasets in test_datasets/ (10 per domain)")

if __name__ == "__main__":
    generate_benchmark_finance()
    generate_benchmark_health()
    generate_tail_showcase()
    generate_50_domain_datasets()
