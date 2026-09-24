from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "synthetic_login_telemetry.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "splits"

RANDOM_STATE = 42


# --------------------------------------------------
# 2. Load dataset and preserve event identity
# --------------------------------------------------

df = pd.read_csv(INPUT_PATH)

# The source dataset has no event ID.
# Assign one before splitting to preserve traceability.
df.insert(
    0,
    "event_id",
    range(1, len(df) + 1)
)

# Ensure the synthetic ground-truth labels are valid.
assert df["is_attack"].isin([0, 1]).all()
assert df["event_id"].is_unique


# --------------------------------------------------
# 3. Stratified train / validation / test split
# --------------------------------------------------

# First split: 70% training, 30% temporary.
train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    random_state=RANDOM_STATE,
    stratify=df["is_attack"]
)

# Second split: 15% validation, 15% test.
validation_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=RANDOM_STATE,
    stratify=temp_df["is_attack"]
)


# --------------------------------------------------
# 4. Validate the partition
# --------------------------------------------------

train_ids = set(train_df["event_id"])
validation_ids = set(validation_df["event_id"])
test_ids = set(test_df["event_id"])

assert train_ids.isdisjoint(validation_ids)
assert train_ids.isdisjoint(test_ids)
assert validation_ids.isdisjoint(test_ids)

assert (
    len(train_ids | validation_ids | test_ids)
    == len(df)
)

assert len(train_df) == 2772
assert len(validation_df) == 594
assert len(test_df) == 594


# --------------------------------------------------
# 5. Save partitioned datasets
# --------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

partitions = {
    "train": train_df,
    "validation": validation_df,
    "test": test_df
}

for name, partition in partitions.items():

    output_path = OUTPUT_DIR / f"{name}.csv"

    partition.to_csv(
        output_path,
        index=False
    )

    print(f"\n{name.upper()}")

    print(f"Total events: {len(partition)}")

    print("Class distribution:")
    print(
        partition["is_attack"]
        .value_counts()
        .sort_index()
    )

    print(f"Saved to: {output_path}")


print("\nAll partitions validated successfully.")