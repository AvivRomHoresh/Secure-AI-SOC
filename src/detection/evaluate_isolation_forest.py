import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. Project paths and configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

with open(
    PROJECT_ROOT / "config" / "project_config.json",
    "r",
    encoding="utf-8"
) as file:
    config = json.load(file)

FEATURE_DIR = (
    PROJECT_ROOT
    / config["paths"]["processed_data"]
    / "features"
)

MODEL_DIR = (
    PROJECT_ROOT
    / config["paths"]["models"]
    / "isolation_forest"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / config["paths"]["results"]
    / "isolation_forest"
)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load trained model and validation data
# --------------------------------------------------

model = joblib.load(
    MODEL_DIR / "isolation_forest.joblib"
)

with open(
    MODEL_DIR / "feature_names.json",
    "r",
    encoding="utf-8"
) as file:
    expected_features = json.load(file)

validation_features = pd.read_csv(
    FEATURE_DIR / "validation_features.csv"
)

validation_metadata = pd.read_csv(
    FEATURE_DIR / "validation_metadata.csv"
)


# --------------------------------------------------
# 3. Validate inputs
# --------------------------------------------------

if validation_features.columns.tolist() != expected_features:
    raise ValueError("Validation feature schema does not match training.")

if len(validation_features) != len(validation_metadata):
    raise ValueError("Feature and metadata row counts do not match.")

if not validation_metadata["event_id"].is_unique:
    raise ValueError("Duplicate event IDs detected.")

if not validation_metadata["is_attack"].isin([0, 1]).all():
    raise ValueError("Invalid ground-truth labels.")

if not np.isfinite(validation_features.to_numpy()).all():
    raise ValueError("Validation features contain invalid values.")


# --------------------------------------------------
# 4. Calculate anomaly scores
# --------------------------------------------------

# Isolation Forest's decision_function assigns lower
# values to more anomalous observations.
# Negating it makes higher scores indicate more anomalies.

anomaly_scores = -model.decision_function(
    validation_features
)


# --------------------------------------------------
# 5. Save results with event identifiers
# --------------------------------------------------

results = validation_metadata[
    ["event_id", "is_attack"]
].copy()

results["anomaly_score"] = anomaly_scores

output_path = (
    RESULTS_DIR / "validation_scores.csv"
)

results.to_csv(output_path, index=False)


# --------------------------------------------------
# 6. Display summary
# --------------------------------------------------

print(f"Validation events: {len(results)}")
print(f"Normal events: {(results['is_attack'] == 0).sum()}")
print(f"Attack events: {(results['is_attack'] == 1).sum()}")

print("\nAnomaly score statistics:")
print(results["anomaly_score"].describe())

print(f"\nResults saved to: {output_path}")