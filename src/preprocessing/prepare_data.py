import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = json.load(file)

settings = config["preprocessing"]

categorical_features = settings["categorical_features"]
numerical_features = settings["numerical_features"]
excluded_columns = settings["excluded_columns"]

if settings["training_strategy"] != "normal_only":
    raise ValueError("Only normal-only training is supported.")

if settings["scaling"] != "standard":
    raise ValueError("Unsupported scaling configuration.")

if settings["categorical_encoding"] != "one_hot":
    raise ValueError("Unsupported categorical encoding.")

if settings["handle_unknown_categories"] != "ignore":
    raise ValueError("Unsupported unknown-category configuration.")


# --------------------------------------------------
# 2. Input and output paths
# --------------------------------------------------

SPLIT_DIR = (
    PROJECT_ROOT
    / config["paths"]["processed_data"]
    / "splits"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / config["paths"]["processed_data"]
    / "features"
)

ARTIFACT_DIR = PROJECT_ROOT / "models" / "preprocessing"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 3. Load datasets
# --------------------------------------------------

train_df = pd.read_csv(SPLIT_DIR / "train.csv")
validation_df = pd.read_csv(SPLIT_DIR / "validation.csv")
test_df = pd.read_csv(SPLIT_DIR / "test.csv")

feature_columns = categorical_features + numerical_features
required_columns = feature_columns + excluded_columns

if len(required_columns) != len(set(required_columns)):
    raise ValueError("Duplicate feature or metadata columns.")

for name, df in [
    ("train", train_df),
    ("validation", validation_df),
    ("test", test_df),
]:
    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"{name}: missing columns: {missing}")

    if df[required_columns].isna().any().any():
        raise ValueError(f"{name}: missing values detected.")

    if not df["is_attack"].isin([0, 1]).all():
        raise ValueError(f"{name}: invalid ground-truth labels.")

    if not df["event_id"].is_unique:
        raise ValueError(f"{name}: duplicate event IDs.")


# --------------------------------------------------
# 4. Select normal training records
# --------------------------------------------------

normal_train = train_df.loc[
    train_df["is_attack"] == 0
].copy()

print(f"Normal training records: {len(normal_train)}")


# --------------------------------------------------
# 5. Define preprocessing pipeline
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        ),
        (
            "numerical",
            StandardScaler(),
            numerical_features
        )
    ],
    remainder="drop",
    verbose_feature_names_out=True
)


# --------------------------------------------------
# 6. Fit on normal training data ONLY
# --------------------------------------------------

preprocessor.fit(normal_train[feature_columns])

output_feature_names = preprocessor.get_feature_names_out()

print(f"Processed feature count: {len(output_feature_names)}")


# --------------------------------------------------
# 7. Transform and save datasets
# --------------------------------------------------

datasets = {
    "train_normal": normal_train,
    "validation": validation_df,
    "test": test_df
}

for name, df in datasets.items():

    transformed = preprocessor.transform(
        df[feature_columns]
    )

    if not np.isfinite(transformed).all():
        raise ValueError(
            f"{name}: non-finite processed values detected."
        )

    processed_df = pd.DataFrame(
        transformed,
        columns=output_feature_names
    )

    # Metadata is preserved separately from model features.
    metadata_df = df[
        ["event_id", "is_attack"]
    ].reset_index(drop=True)

    processed_df.to_csv(
        OUTPUT_DIR / f"{name}_features.csv",
        index=False
    )

    metadata_df.to_csv(
        OUTPUT_DIR / f"{name}_metadata.csv",
        index=False
    )

    print(
        f"{name}: {processed_df.shape[0]} events, "
        f"{processed_df.shape[1]} features"
    )


# --------------------------------------------------
# 8. Save fitted preprocessing artifact
# --------------------------------------------------

joblib.dump(
    preprocessor,
    ARTIFACT_DIR / "preprocessor.joblib"
)

with open(
    ARTIFACT_DIR / "feature_names.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        output_feature_names.tolist(),
        file,
        indent=2
    )

print("\nPreprocessing completed successfully.")