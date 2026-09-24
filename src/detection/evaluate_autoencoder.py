"""Calculate validation reconstruction errors for the frozen autoencoder.

Run from repository root:
    python src/detection/evaluate_autoencoder.py

Does not fit the model, select a threshold, or access the held-out test set.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
with (PROJECT_ROOT / "config" / "project_config.json").open(encoding="utf-8") as file:
    config = json.load(file)

feature_dir = PROJECT_ROOT / config["paths"]["processed_data"] / "features"
model_dir = PROJECT_ROOT / config["paths"]["models"] / "autoencoder"
results_dir = PROJECT_ROOT / config["paths"]["results"] / "autoencoder"
results_dir.mkdir(parents=True, exist_ok=True)

model = joblib.load(model_dir / "autoencoder.joblib")
with (model_dir / "feature_names.json").open(encoding="utf-8") as file:
    expected_features = json.load(file)

features = pd.read_csv(feature_dir / "validation_features.csv")
metadata = pd.read_csv(feature_dir / "validation_metadata.csv")

if features.empty:
    raise ValueError("Validation features are empty.")
if features.columns.tolist() != expected_features:
    raise ValueError("Validation feature schema differs from training schema.")
if len(features) != len(metadata):
    raise ValueError("Validation feature and metadata row counts differ.")
if not {"event_id", "is_attack"}.issubset(metadata.columns):
    raise ValueError("Missing validation metadata columns.")
if metadata[["event_id", "is_attack"]].isna().any().any():
    raise ValueError("Validation metadata contains missing identifiers or labels.")
if not metadata["event_id"].is_unique:
    raise ValueError("Duplicate validation event IDs.")
if not metadata["is_attack"].isin([0, 1]).all():
    raise ValueError("Validation labels must be binary.")

X = features.to_numpy(dtype=np.float64)
if not np.isfinite(X).all():
    raise ValueError("Validation features contain invalid values.")
if X.shape[1] != model.n_features_in_:
    raise ValueError("Model input dimension differs from validation features.")

reconstructed = model.predict(X)
if reconstructed.shape != X.shape or not np.isfinite(reconstructed).all():
    raise ValueError("Model returned invalid reconstructions.")
errors = np.mean((X - reconstructed) ** 2, axis=1)

results = metadata[["event_id", "is_attack"]].copy()
results["reconstruction_mse"] = errors
output = results_dir / "validation_scores.csv"
results.to_csv(output, index=False)

print(f"Validation events: {len(results)}")
print(f"Normal events: {(results['is_attack'] == 0).sum()}")
print(f"Attack events: {(results['is_attack'] == 1).sum()}")
print("\nReconstruction MSE by actual class:")
print(results.groupby("is_attack")["reconstruction_mse"].describe().round(6).to_string())
print(f"\nValidation scores saved to: {output}")
print("No threshold selected; held-out test set remains untouched.")
