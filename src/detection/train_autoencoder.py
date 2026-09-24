"""Train a lightweight MLP autoencoder on normal login telemetry only.

Run from the repository root:
    python src/detection/train_autoencoder.py

This script deliberately DOES NOT access validation/test partitions. Threshold
selection and evaluation will be separate subsequent steps.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[2]

with (PROJECT_ROOT / "config" / "project_config.json").open(encoding="utf-8") as file:
    config = json.load(file)

model_config = config["detection"]["autoencoder"]
if not model_config["enabled"]:
    raise ValueError("Autoencoder is disabled in the project configuration.")

seed = int(model_config["random_seed"])
np.random.seed(seed)

feature_dir = PROJECT_ROOT / config["paths"]["processed_data"] / "features"
model_dir = PROJECT_ROOT / config["paths"]["models"] / "autoencoder"
model_dir.mkdir(parents=True, exist_ok=True)

features = pd.read_csv(feature_dir / "train_normal_features.csv")
metadata = pd.read_csv(feature_dir / "train_normal_metadata.csv")

if features.empty:
    raise ValueError("Normal training features are empty.")
if len(features) != len(metadata):
    raise ValueError("Feature and metadata row counts do not match.")
if not {"event_id", "is_attack"}.issubset(metadata.columns):
    raise ValueError("Missing training metadata columns.")
if not metadata["event_id"].is_unique:
    raise ValueError("Duplicate training event IDs detected.")
if not metadata["is_attack"].eq(0).all():
    raise ValueError("Autoencoder training data contains attack records.")
if {"event_id", "is_attack"}.intersection(features.columns):
    raise ValueError("Event identifiers or labels leaked into model features.")

X = features.to_numpy(dtype=np.float64)
if not np.isfinite(X).all():
    raise ValueError("Training features contain NaN or infinite values.")

# The narrow bottleneck (17 -> 8 -> 4 -> 8 -> 17) encourages compression.
# MLPRegressor's output has one unit per input feature when fitted to X -> X.
# Its squared-error loss is the reconstruction objective.
model = MLPRegressor(
    hidden_layer_sizes=(8, 4, 8),
    activation="relu",
    solver="adam",
    alpha=1e-4,
    batch_size=64,
    learning_rate_init=0.001,
    max_iter=500,
    shuffle=True,
    random_state=seed,
    early_stopping=False,
)

print(f"Training samples: {len(X)}")
print(f"Input features: {X.shape[1]}")
print("Architecture: input -> 8 -> 4 -> 8 -> reconstruction")

# Unsupervised learning: normal features are both input and reconstruction target.
# The held-out validation and test sets are intentionally untouched.
model.fit(X, X)

reconstruction = model.predict(X)
train_errors = np.mean((X - reconstruction) ** 2, axis=1)
if not np.isfinite(train_errors).all():
    raise ValueError("Invalid reconstruction errors after training.")

joblib.dump(model, model_dir / "autoencoder.joblib")
with (model_dir / "feature_names.json").open("w", encoding="utf-8") as file:
    json.dump(features.columns.tolist(), file, indent=2)

training_info = {
    "model": "MLPRegressor-based autoencoder",
    "seed": seed,
    "training_samples": int(len(X)),
    "input_features": int(X.shape[1]),
    "hidden_layer_sizes": [8, 4, 8],
    "activation": "relu",
    "optimizer": "adam",
    "max_iter": 500,
    "actual_iterations": int(model.n_iter_),
    "final_training_loss": float(model.loss_),
    "training_reconstruction_mse_mean": float(train_errors.mean()),
    "training_reconstruction_mse_median": float(np.median(train_errors)),
    "converged_before_iteration_limit": bool(model.n_iter_ < model.max_iter),
    "threshold_selected": False,
    "validation_evaluated": False,
    "test_evaluated": False,
}
with (model_dir / "training_info.json").open("w", encoding="utf-8") as file:
    json.dump(training_info, file, indent=2)

print(f"Iterations: {model.n_iter_}")
print(f"Final training loss: {model.loss_:.6f}")
print(f"Mean training reconstruction MSE: {train_errors.mean():.6f}")
if model.n_iter_ == model.max_iter:
    print("NOTE: Iteration limit reached; inspect training loss before proceeding.")
print(f"Model and training metadata saved to: {model_dir}")
