import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest


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

model_config = config["detection"]["isolation_forest"]

if not model_config["enabled"]:
    raise ValueError("Isolation Forest is disabled in configuration.")

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

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load normal training features
# --------------------------------------------------

train_features = pd.read_csv(
    FEATURE_DIR / "train_normal_features.csv"
)

train_metadata = pd.read_csv(
    FEATURE_DIR / "train_normal_metadata.csv"
)

if len(train_features) != len(train_metadata):
    raise ValueError("Feature and metadata row counts do not match.")

if not train_metadata["is_attack"].eq(0).all():
    raise ValueError("Training data contains attack records.")

if not np.isfinite(train_features.to_numpy()).all():
    raise ValueError("Training features contain invalid values.")

print(f"Training samples: {len(train_features)}")
print(f"Input features: {train_features.shape[1]}")


# --------------------------------------------------
# 3. Initialize and train Isolation Forest
# --------------------------------------------------

model = IsolationForest(
    n_estimators=model_config["n_estimators"],
    random_state=model_config["random_state"],
    contamination="auto",
    n_jobs=-1
)

model.fit(train_features)

print("Isolation Forest training completed.")


# --------------------------------------------------
# 4. Save model and feature schema
# --------------------------------------------------

joblib.dump(
    model,
    MODEL_DIR / "isolation_forest.joblib"
)

with open(
    MODEL_DIR / "feature_names.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        train_features.columns.tolist(),
        file,
        indent=2
    )

print("Model and feature schema saved successfully.")