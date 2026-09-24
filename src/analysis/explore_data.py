from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. Project configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "synthetic_login_telemetry.csv"
)

NUMERIC_FEATURES = [
    "hour",
    "failed_attempts",
    "distance_km",
    "session_minutes",
    "bytes_out_mb",
]

CATEGORICAL_FEATURES = [
    "user",
    "country",
    "device",
    "protocol",
]


# --------------------------------------------------
# 2. Load dataset
# --------------------------------------------------

df = pd.read_csv(DATASET_PATH)

print("\n========== DATASET OVERVIEW ==========")

print(f"Dataset shape: {df.shape}")

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)


# --------------------------------------------------
# 3. Data quality
# --------------------------------------------------

print("\n========== DATA QUALITY ==========")

print("\nMissing values:")
print(df.isnull().sum())

print(f"\nDuplicate rows: {df.duplicated().sum()}")

print("\nInvalid numeric values:")

invalid_checks = {
    "hour": ~df["hour"].between(0, 23),
    "failed_attempts": df["failed_attempts"] < 0,
    "distance_km": df["distance_km"] < 0,
    "session_minutes": df["session_minutes"] < 0,
    "bytes_out_mb": df["bytes_out_mb"] < 0,
}

for feature, invalid_mask in invalid_checks.items():
    print(f"{feature}: {invalid_mask.sum()}")


# --------------------------------------------------
# 4. Class distribution
# --------------------------------------------------

print("\n========== CLASS DISTRIBUTION ==========")

class_counts = df["is_attack"].value_counts().sort_index()

print("\nClass counts:")
print(class_counts)

print("\nClass percentages:")
print(
    df["is_attack"]
    .value_counts(normalize=True)
    .sort_index()
    .mul(100)
    .round(2)
)


# --------------------------------------------------
# 5. Numerical feature analysis
# --------------------------------------------------

print("\n========== NUMERICAL FEATURES ==========")

print(
    df.groupby("is_attack")[NUMERIC_FEATURES]
    .agg(["mean", "median", "std", "min", "max"])
    .round(2)
    .to_string()
)


# --------------------------------------------------
# 6. Categorical feature analysis
# --------------------------------------------------

print("\n========== CATEGORICAL FEATURES ==========")

for feature in CATEGORICAL_FEATURES:

    print(f"\nFeature: {feature}")

    print(
        pd.crosstab(
            df[feature],
            df["is_attack"]
        ).to_string()
    )


print("\nEDA completed successfully.")
# --------------------------------------------------
# 7. EDA Visualizations
# --------------------------------------------------

FIGURES_DIR = PROJECT_ROOT / "results" / "figures" / "eda"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Class distribution
plt.figure(figsize=(7, 5))
class_counts.plot(kind="bar")

plt.title("Class Distribution")
plt.xlabel("Class (0 = Normal, 1 = Attack)")
plt.ylabel("Number of Events")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(FIGURES_DIR / "class_distribution.png", dpi=150)
plt.close()


# Numerical feature distributions
for feature in NUMERIC_FEATURES:

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    for ax, label, title in zip(
        axes,
        [0, 1],
        ["Normal", "Attack"]
    ):
        values = df.loc[df["is_attack"] == label, feature]

        ax.hist(values, bins=30)
        ax.set_title(f"{feature} - {title}")
        ax.set_xlabel(feature)
        ax.set_ylabel("Frequency")

    fig.tight_layout()

    fig.savefig(
        FIGURES_DIR / f"{feature}_distribution.png",
        dpi=150
    )

    plt.close(fig)


print(f"\nEDA figures saved to: {FIGURES_DIR}")