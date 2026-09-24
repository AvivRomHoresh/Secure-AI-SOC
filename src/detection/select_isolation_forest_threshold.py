import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "isolation_forest"
)

SCORES_PATH = RESULTS_DIR / "validation_scores.csv"


# --------------------------------------------------
# 2. Load validation scores
# --------------------------------------------------

data = pd.read_csv(SCORES_PATH)

required_columns = {
    "event_id",
    "is_attack",
    "anomaly_score"
}

if not required_columns.issubset(data.columns):
    raise ValueError("Missing required columns.")

if data.empty:
    raise ValueError("Validation results are empty.")

if not data["event_id"].is_unique:
    raise ValueError("Duplicate event IDs detected.")

if data["is_attack"].isna().any():
    raise ValueError("Missing ground-truth labels.")

if not data["is_attack"].isin([0, 1]).all():
    raise ValueError("Invalid ground-truth labels.")

if not np.isfinite(data["anomaly_score"].to_numpy()).all():
    raise ValueError("Invalid anomaly scores.")

y_true = data["is_attack"].to_numpy()
scores = data["anomaly_score"].to_numpy()


# --------------------------------------------------
# 3. Generate candidate thresholds
# --------------------------------------------------

# Higher anomaly scores indicate greater abnormality.
# An event is classified as an attack when:
#
# anomaly_score >= threshold
#
# We evaluate every distinct score as a possible
# threshold, plus one threshold above the maximum
# score to represent the all-normal prediction.

unique_scores = np.sort(np.unique(scores))

candidate_thresholds = np.append(
    unique_scores,
    np.nextafter(unique_scores[-1], np.inf)
)


# --------------------------------------------------
# 4. Select threshold using validation F1
# --------------------------------------------------

best_threshold = None
best_f1 = -1.0

# Tie-breaking rule:
# If several thresholds achieve the same F1,
# select the highest threshold.
#
# This is deterministic and favors fewer
# positive predictions among tied candidates.

for threshold in candidate_thresholds:

    predictions = (scores >= threshold).astype(int)

    current_f1 = f1_score(
        y_true,
        predictions,
        zero_division=0
    )

    if (
        current_f1 > best_f1 + 1e-12
        or (
            abs(current_f1 - best_f1) <= 1e-12
            and (
                best_threshold is None
                or threshold > best_threshold
            )
        )
    ):
        best_f1 = current_f1
        best_threshold = float(threshold)


# --------------------------------------------------
# 5. Calculate validation metrics
# --------------------------------------------------

predictions = (
    scores >= best_threshold
).astype(int)

precision = precision_score(
    y_true,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_true,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_true,
    predictions,
    zero_division=0
)

tn, fp, fn, tp = confusion_matrix(
    y_true,
    predictions,
    labels=[0, 1]
).ravel()


# --------------------------------------------------
# 6. Save threshold and metrics
# --------------------------------------------------

results = {
    "model": "Isolation Forest",
    "selection_dataset": "validation",
    "selection_metric": "F1",
    "prediction_rule": "anomaly_score >= threshold",
    "tie_breaking_rule": "highest_threshold",
    "threshold": best_threshold,
    "precision": float(precision),
    "recall": float(recall),
    "f1": float(f1),
    "confusion_matrix": {
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "TP": int(tp)
    }
}

output_path = RESULTS_DIR / "threshold_selection.json"

with open(
    output_path,
    "w",
    encoding="utf-8"
) as file:
    json.dump(results, file, indent=4)


# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print("Isolation Forest - Threshold Selection")
print("--------------------------------------")

print(f"Validation events: {len(data)}")
print(f"Selected threshold: {best_threshold:.6f}")

print("\nValidation metrics:")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nConfusion matrix:")
print(f"TN: {tn}")
print(f"FP: {fp}")
print(f"FN: {fn}")
print(f"TP: {tp}")

print(f"\nResults saved to: {output_path}")