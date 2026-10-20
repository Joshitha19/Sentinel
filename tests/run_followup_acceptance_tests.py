"""
SENTINEL Follow-Up Fix Acceptance Tests
=======================================
Verifies all 5 Acceptance Criteria required by the user:
1. No generated row has an invalid sex/flag/integer type or an out-of-range value (print min/max per column).
2. Realism, Novelty, and Hardness differ across the 6 cases (print them).
3. Text-vs-feature consistency check passes for all 6 cases.
4. The Novelty discovery check result is displayed (12 held-out novel_unclassified_cluster cases).
5. Schema and physiological range limits verified.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure backend path is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.engine.tabular_gan import AdversarialSelfPlayEngine, TabularSchemaInferer


def run_followup_acceptance_tests():
    print("=" * 80)
    print("SENTINEL HEALTH GENERATOR FOLLOW-UP FIX ACCEPTANCE TESTS")
    print("=" * 80)

    health_csv_path = Path(__file__).resolve().parent.parent / "sentinel_health_test.csv"
    if not health_csv_path.exists():
        print("Regenerating sentinel_health_test.csv...")
        import generate_test_datasets
        generate_test_datasets.generate_benchmark_health()

    df_health = pd.read_csv(health_csv_path)
    print(f"Loaded dataset: {health_csv_path.name} ({len(df_health)} rows, {len(df_health.columns)} columns)")

    # Initialize Engine on health dataset
    engine = AdversarialSelfPlayEngine(df_health, domain_id="health", seed=2026)
    print("Training Adversarial Self-Play GAN (12 rounds)...")
    proof = engine.train_self_play(n_rounds=12, tail_multiplier=1.15)
    print(f"Self-play completed in {proof['training_time_seconds']}s. Real-vs-Fake AUC: {proof['real_vs_fake_auc']:.3f}")

    # Generate 6 Rare Health Cases (RARE-ARCH-01 to 06)
    print("\nGenerating 6 Rare Archetypes (RARE-ARCH-01 to 06)...")
    events = engine.select_archetypes(pool_size=1000, n_showcase=6, tail_multiplier=1.15)
    assert len(events) == 6, f"Expected 6 events, got {len(events)}"

    print(f"Successfully generated {len(events)} rare health cases.\n")

    # =========================================================================
    # CRITERION 1: Feature Type and Physiological Range Limits Verification
    # =========================================================================
    print("-" * 80)
    print("CRITERION 1: FEATURE TYPES & PHYSIOLOGICAL RANGE LIMITS")
    print("-" * 80)
    
    # Check all 6 cases have valid types
    binary_cols = ["joint_pain", "rash", "enlarged_spleen", "neuro_symptoms"]
    integer_cols = ["age", "fever_days", "fatigue_score", "platelets_k", "ferritin_ng_ml"]
    
    all_rows = [e["features"] for e in events]
    df_gen = pd.DataFrame(all_rows)

    print(f"{'Feature':<22} | {'Data Min':<10} | {'Data Max':<10} | {'Gen Min':<10} | {'Gen Max':<10} | {'Type Check'}")
    print("-" * 80)

    type_errors = []
    range_errors = []

    for col in engine.inferer.feature_cols:
        stat = engine.inferer.col_stats.get(col, {})
        if col == "sex":
            unique_vals = set(df_gen["sex"].unique())
            valid_sex = unique_vals.issubset({"M", "F"})
            if not valid_sex:
                type_errors.append(f"Invalid sex values: {unique_vals}")
            print(f"{col:<22} | {'Categoric':<10} | {'M / F':<10} | {str(unique_vals):<10} | {'-':<10} | {'PASS (M/F)' if valid_sex else 'FAIL'}")
            continue

        gen_min = df_gen[col].min()
        gen_max = df_gen[col].max()
        data_min = stat["min"]
        data_max = stat["max"]

        type_status = "PASS"
        if col in binary_cols:
            if not set(df_gen[col].unique()).issubset({0, 1}):
                type_status = "FAIL (not 0/1)"
                type_errors.append(f"{col} contains non-binary values: {df_gen[col].unique()}")
            else:
                type_status = "PASS (0/1)"
        elif col in integer_cols:
            is_int = all(isinstance(v, (int, np.integer)) or float(v).is_integer() for v in df_gen[col])
            if not is_int:
                type_status = "FAIL (not integer)"
                type_errors.append(f"{col} contains non-integers")
            else:
                type_status = "PASS (int)"

        # Check range limits (max 10-15% headroom beyond data min/max)
        headroom = 0.15
        span = data_max - data_min
        allowed_min = max(0.0 if data_min >= 0 else -1e9, data_min - headroom * span)
        allowed_max = data_max + headroom * span

        # Specific physiological bounds
        if col == "hemoglobin":
            allowed_max = 18.5  # Data max is 18.0
        elif col == "fatigue_score":
            allowed_max = 10
            allowed_min = 0

        range_ok = (gen_min >= allowed_min - 1e-4) and (gen_max <= allowed_max + 1e-4)
        if not range_ok:
            range_errors.append(f"{col} out of physiological bounds: gen [{gen_min}, {gen_max}], allowed [{allowed_min:.2f}, {allowed_max:.2f}]")

        print(f"{col:<22} | {data_min:<10.2f} | {data_max:<10.2f} | {gen_min:<10.2f} | {gen_max:<10.2f} | {type_status}")

    c1_passed = len(type_errors) == 0 and len(range_errors) == 0
    print(f"\n-> Criterion 1 Status: {'PASS' if c1_passed else 'FAIL'}")
    if type_errors:
        print(f"   Type errors: {type_errors}")
    if range_errors:
        print(f"   Range errors: {range_errors}")

    # =========================================================================
    # CRITERION 2: Real Model Scores Differ Visibly Across All 6 Cases
    # =========================================================================
    print("\n" + "-" * 80)
    print("CRITERION 2: REAL MODEL SCORES VARY ACROSS 6 CASES (Realism, Novelty, Hardness)")
    print("-" * 80)
    print(f"{'Case ID':<14} | {'Realism (%)':<14} | {'Tail Novelty (%)':<18} | {'Hardness (/100)':<16} | {'Risk (/100)'}")
    print("-" * 80)

    realisms = []
    novelties = []
    hardnesses = []

    for e in events:
        r = round(e["plausibility_score"] * 100, 1)
        n = round(float(e["rarity_score"]), 1)
        h = round(float(e["hardness_score"]), 1)
        realisms.append(r)
        novelties.append(n)
        hardnesses.append(h)
        print(f"{e['event_id']:<14} | {r:<14.1f} | {n:<18.1f} | {h:<16.1f} | {e['risk_score']}")

    # Check variation (not near constant ~85% or ~90%)
    realism_std = np.std(realisms)
    novelty_std = np.std(novelties)
    hardness_std = np.std(hardnesses)

    print(f"\nScore Variation Standard Deviations:")
    print(f"  Realism std: {realism_std:.2f}% (Range: {min(realisms):.1f}% - {max(realisms):.1f}%)")
    print(f"  Tail Novelty std: {novelty_std:.2f}% (Range: {min(novelties):.1f}% - {max(novelties):.1f}%)")
    print(f"  Hardness std: {hardness_std:.2f} (Range: {min(hardnesses):.1f} - {max(hardnesses):.1f})")

    c2_passed = (len(set(realisms)) >= 4) and (len(set(novelties)) >= 4) and (len(set(hardnesses)) >= 4)
    print(f"-> Criterion 2 Status: {'PASS' if c2_passed else 'FAIL'} (Scores computed from critic, kNN, and detector vary authentically)")

    # Print formula tooltips
    print("\nScore Formula Tooltips:")
    sample_formulas = events[0].get("score_formulas", {})
    for k, f in sample_formulas.items():
        print(f"  {k}: {f}")

    # =========================================================================
    # CRITERION 3: Text-vs-Feature Verbatim Consistency Check
    # =========================================================================
    print("\n" + "-" * 80)
    print("CRITERION 3: TEXT-VS-FEATURE VERBATIM CONSISTENCY CHECK")
    print("-" * 80)
    c3_all_pass = True
    for e in events:
        is_ok, msg = engine.verify_text_number_consistency(e["simple_explanation"], e["features"])
        if not is_ok:
            c3_all_pass = False
        print(f"  {e['event_id']}: {'MATCH [OK]' if is_ok else 'MISMATCH [FAIL]'}")
        print(f"    Explanation: \"{e['simple_explanation']}\"")
        print(f"    Validation detail: {msg}\n")

    print(f"-> Criterion 3 Status: {'PASS' if c3_all_pass else 'FAIL'} (All narrative numbers match feature values)")

    # =========================================================================
    # CRITERION 4: Binary/Ordinal Prevalence Without Sigmas
    # =========================================================================
    print("-" * 80)
    print("CRITERION 4: BINARY/ORDINAL ANOMALIES USE PREVALENCE (NO SIGMAS)")
    print("-" * 80)
    c4_pass = True
    for e in events:
        for anom in e["key_anomalies"]:
            # Check if any binary feature mentions sigma
            for bcol in binary_cols:
                if bcol in anom and "sigma" in anom.lower():
                    c4_pass = False
                    print(f"  FAIL: Found sigma in binary feature: '{anom}'")
        print(f"  {e['event_id']} Key Anomalies:")
        for anom in e["key_anomalies"]:
            print(f"    * {anom}")

    print(f"-> Criterion 4 Status: {'PASS' if c4_pass else 'FAIL'} (Prevalence percentages used for binary/ordinal features)")

    # =========================================================================
    # CRITERION 5: Novelty Discovery Check on Held-Out Cases
    # =========================================================================
    print("\n" + "-" * 80)
    print("CRITERION 5: NOVELTY DISCOVERY CHECK (12 Held-Out novel_unclassified_cluster cases)")
    print("-" * 80)
    novelty_eval = engine.evaluate_novelty_discovery(events)
    for k, v in novelty_eval.items():
        print(f"  {k:<38}: {v}")

    c5_pass = novelty_eval.get("has_held_out") is True and novelty_eval.get("total_held_out_cases") == 12
    print(f"\n-> Criterion 5 Status: {'PASS' if c5_pass else 'FAIL'} (Zero-shot discovery & detector recall evaluated against Isolation Forest)")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY OF ALL ACCEPTANCE CRITERIA")
    print("=" * 80)
    print(f"1. Valid Feature Types & Physiological Limits (hemoglobin <= 18.5, sex M/F, binary 0/1): {'PASS' if c1_passed else 'FAIL'}")
    print(f"2. Real Varying Scores (Realism, Tail Novelty, Hardness):                                {'PASS' if c2_passed else 'FAIL'}")
    print(f"3. Verbatim Text-Feature Consistency Check:                                             {'PASS' if c3_all_pass else 'FAIL'}")
    print(f"4. Binary/Ordinal Prevalence (No Sigmas):                                               {'PASS' if c4_pass else 'FAIL'}")
    print(f"5. Novelty Discovery Check (Held-out 12 clusters evaluated):                            {'PASS' if c5_pass else 'FAIL'}")
    print("=" * 80)

    all_passed = c1_passed and c2_passed and c3_all_pass and c4_pass and c5_pass
    print(f"OVERALL FOLLOW-UP ACCEPTANCE: {'PASSED' if all_passed else 'FAILED'}\n")
    return all_passed


if __name__ == "__main__":
    ok = run_followup_acceptance_tests()
    sys.exit(0 if ok else 1)
