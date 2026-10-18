"""
SENTINEL — Step 2: Baseline Detector

Trains a straightforward XGBoost classifier on the raw Kaggle
Credit Card Fraud dataset. This is your BEFORE number — later,
once the Generator + self-play loop exist, you'll retrain and
show the improvement over this baseline. Keep this script and
its metrics.json output untouched so the comparison is honest.

Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
Expected columns: Time, V1..V28, Amount, Class (Class=1 is fraud)
"""

import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
    confusion_matrix,
)
from xgboost import XGBClassifier


DATA_PATH = "data/creditcard.csv"
RESULTS_PATH = "results/baseline_metrics.json"
RANDOM_STATE = 42


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} rows — {df['Class'].sum()} fraud "
          f"({100 * df['Class'].mean():.3f}% of total)")
    return df


def prepare_features(df: pd.DataFrame):
    X = df.drop(columns=["Class"])
    y = df["Class"]

    scaler = StandardScaler()
    X[["Time", "Amount"]] = scaler.fit_transform(X[["Time", "Amount"]])

    return train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )


def train_baseline(X_train, y_train) -> XGBClassifier:
    fraud_ratio = (y_train == 0).sum() / (y_train == 1).sum()

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        scale_pos_weight=fraud_ratio,
        eval_metric="aucpr",
        random_state=RANDOM_STATE,
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict:
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    roc_auc = roc_auc_score(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    metrics = {
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "true_positives": int(tp),
        "false_negatives": int(fn),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "detection_rate": round(tp / (tp + fn), 4),
    }

    print("\n--- Baseline Detector results ---")
    print(json.dumps(metrics, indent=2))
    print("\n" + classification_report(y_test, y_pred, target_names=["legit", "fraud"]))

    return metrics


def main():
    df = load_data()
    X_train, X_test, y_train, y_test = prepare_features(df)
    model = train_baseline(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)

    with open(RESULTS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved baseline metrics to {RESULTS_PATH}")

    model.save_model("results/baseline_model.json")
    print("Saved model to results/baseline_model.json")


if __name__ == "__main__":
    main()