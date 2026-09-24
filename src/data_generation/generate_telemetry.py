from pathlib import Path
import random

import numpy as np
import pandas as pd


# Reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Dataset size
N_NORMAL = 3800
N_ATTACK = 160

# Normal user profiles
users = [
    "analyst01",
    "analyst02",
    "finance01",
    "developer01",
    "admin01",
]

usual_country = {
    user: "IL" for user in users
}

usual_device = {
    "analyst01": "managed_laptop",
    "analyst02": "managed_laptop",
    "finance01": "managed_laptop",
    "developer01": "developer_workstation",
    "admin01": "admin_workstation",
}

rows = []

# Generate normal login events
for _ in range(N_NORMAL):
    user = np.random.choice(
        users,
        p=[0.25, 0.20, 0.20, 0.25, 0.10]
    )

    rows.append({
        "user": user,
        "country": usual_country[user],
        "device": usual_device[user],
        "protocol": np.random.choice(
            ["HTTPS", "VPN", "SSH"],
            p=[0.60, 0.32, 0.08]
        ),
        "hour": int(np.clip(np.random.normal(12.5, 2.5), 6, 21)),
        "failed_attempts": np.random.poisson(0.25),
        "distance_km": abs(np.random.normal(8, 12)),
        "session_minutes": max(1, np.random.gamma(3.5, 12)),
        "bytes_out_mb": max(0.1, np.random.lognormal(2.0, 0.6)),
        "is_attack": 0,
    })

# Generate attack events
for _ in range(N_ATTACK):
    user = np.random.choice(users)

    rows.append({
        "user": user,
        "country": np.random.choice(["RU", "CN", "SG", "US", "DE"]),
        "device": np.random.choice(
            ["unknown", "mobile", "unmanaged_laptop"]
        ),
        "protocol": np.random.choice(["HTTPS", "VPN", "SSH"]),
        "hour": np.random.choice([0, 1, 2, 3, 4, 23]),
        "failed_attempts": np.random.randint(5, 18),
        "distance_km": np.random.uniform(800, 9000),
        "session_minutes": np.random.uniform(1, 20),
        "bytes_out_mb": np.random.lognormal(5.0, 0.7),
        "is_attack": 1,
    })

# Create and shuffle the dataset
df = (
    pd.DataFrame(rows)
    .sample(frac=1, random_state=SEED)
    .reset_index(drop=True)
)

# Save the original dataset
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "synthetic_login_telemetry.csv"

df.to_csv(output_file, index=False)

print(f"Dataset saved to: {output_file}")
print(f"Dataset shape: {df.shape}")
print("\nClass distribution:")
print(df["is_attack"].value_counts())