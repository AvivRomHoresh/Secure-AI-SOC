"""One-time held-out evaluation of two frozen anomaly detectors.

Run from repository root:
    python src/detection/evaluate_detectors_test.py

No training, preprocessing fitting, or threshold tuning is performed here.
Run only after both models and validation thresholds are frozen.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parents[2]
with (ROOT / "config/project_config.json").open(encoding="utf-8") as f:
    config = json.load(f)

features_dir = ROOT / config["paths"]["processed_data"] / "features"
models_dir = ROOT / config["paths"]["models"]
results_dir = ROOT / config["paths"]["results"] / "detection_comparison"

# Load the *previously prepared* held-out data, without fitting preprocessing.
features = pd.read_csv(features_dir / "test_features.csv")
metadata = pd.read_csv(features_dir / "test_metadata.csv")
if features.empty or len(features) != len(metadata):
    raise ValueError("Test features are empty or misaligned with metadata.")
if not {"event_id", "is_attack"}.issubset(metadata.columns):
    raise ValueError("Missing event_id or is_attack in test metadata.")
if metadata[["event_id", "is_attack"]].isna().any().any():
    raise ValueError("Missing values in test metadata.")
if not metadata.event_id.is_unique or not metadata.is_attack.isin([0, 1]).all():
    raise ValueError("Invalid test event IDs or ground-truth labels.")
if {"event_id", "is_attack"}.intersection(features.columns):
    raise ValueError("Metadata leaked into test features.")
X = features.to_numpy(dtype=np.float64)
if not np.isfinite(X).all():
    raise ValueError("Invalid test feature values.")

# Check schema identity, not just feature count.
def load_schema(model_name):
    with (models_dir / model_name / "feature_names.json").open(encoding="utf-8") as f:
        schema = json.load(f)
    if features.columns.tolist() != schema:
        raise ValueError(f"{model_name}: test feature schema differs from training.")

load_schema("isolation_forest")
load_schema("autoencoder")

with (results_dir.parent / "isolation_forest" / "threshold_selection.json").open(encoding="utf-8") as f:
    if_threshold_info = json.load(f)
with (results_dir.parent / "autoencoder" / "threshold_selection.json").open(encoding="utf-8") as f:
    ae_threshold_info = json.load(f)
if if_threshold_info.get("selection_dataset") != "validation" or ae_threshold_info.get("dataset") != "validation":
    raise ValueError("Expected validation-derived thresholds; test-derived thresholds are forbidden.")
if_threshold = float(if_threshold_info["threshold"])
ae_threshold = float(ae_threshold_info["selected_threshold"])
if not np.isfinite(if_threshold) or not np.isfinite(ae_threshold):
    raise ValueError("Thresholds must be finite.")

if_model = joblib.load(models_dir / "isolation_forest" / "isolation_forest.joblib")
ae_model = joblib.load(models_dir / "autoencoder" / "autoencoder.joblib")
if X.shape[1] != if_model.n_features_in_ or X.shape[1] != ae_model.n_features_in_:
    raise ValueError("Saved model input dimensions differ from test data.")

if_scores = -if_model.decision_function(features)
reconstruction = ae_model.predict(X)
if reconstruction.shape != X.shape or not np.isfinite(reconstruction).all():
    raise ValueError("Invalid autoencoder reconstructions.")
ae_scores = np.mean((X - reconstruction) ** 2, axis=1)
if not np.isfinite(if_scores).all() or not np.isfinite(ae_scores).all():
    raise ValueError("Invalid detector scores.")

if_predictions = (if_scores >= if_threshold).astype(int)
ae_predictions = (ae_scores >= ae_threshold).astype(int)
y = metadata.is_attack.to_numpy(dtype=int)

def evaluate(pred):
    tn, fp, fn, tp = map(int, confusion_matrix(y, pred, labels=[0, 1]).ravel())
    p, r, f1, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    return {
        "precision": float(p), "recall": float(r), "f1": float(f1),
        "false_positive_rate": float(fp / (fp + tn)) if fp + tn else None,
        "false_negative_rate": float(fn / (fn + tp)) if fn + tp else None,
        "predicted_anomalies": int(pred.sum()),
        "predicted_anomaly_rate": float(pred.mean()),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }

agreement = (if_predictions == ae_predictions)
results = {
    "dataset": "held_out_test", "total_events": len(y),
    "normal_events": int((y == 0).sum()), "attack_events": int((y == 1).sum()),
    "threshold_source": "validation_only_frozen", "thresholds": {
        "isolation_forest": if_threshold, "autoencoder": ae_threshold,
    },
    "isolation_forest": evaluate(if_predictions),
    "autoencoder": evaluate(ae_predictions),
    "model_agreement": {
        "agree_count": int(agreement.sum()), "disagree_count": int((~agreement).sum()),
        "agreement_rate": float(agreement.mean()),
        "both_anomaly": int(((if_predictions == 1) & (ae_predictions == 1)).sum()),
        "both_normal": int(((if_predictions == 0) & (ae_predictions == 0)).sum()),
        "isolation_forest_only": int(((if_predictions == 1) & (ae_predictions == 0)).sum()),
        "autoencoder_only": int(((if_predictions == 0) & (ae_predictions == 1)).sum()),
    },
}

predictions = metadata[["event_id", "is_attack"]].copy()
predictions["isolation_forest_score"] = if_scores
predictions["isolation_forest_pred"] = if_predictions
predictions["autoencoder_reconstruction_mse"] = ae_scores
predictions["autoencoder_pred"] = ae_predictions
predictions["models_agree"] = agreement

# Avoid accidentally overwriting an earlier final test evaluation.
results_dir.mkdir(parents=True, exist_ok=True)
metrics_path = results_dir / "test_metrics.json"
pred_path = results_dir / "test_predictions.csv"
if metrics_path.exists() or pred_path.exists():
    raise FileExistsError("Held-out test outputs already exist. Inspect them; do not repeatedly tune on test.")
with metrics_path.open("w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
predictions.to_csv(pred_path, index=False)

print("Held-out test evaluation — frozen detectors and thresholds")
print(f"Events: {len(y)} | Normal: {(y == 0).sum()} | Attack: {(y == 1).sum()}")
for name, label in [("isolation_forest", "Isolation Forest"), ("autoencoder", "Autoencoder")]:
    m = results[name]
    print(f"\n{label} (threshold={results['thresholds'][name]:.6f}):")
    print(f"Precision={m['precision']:.4f} Recall={m['recall']:.4f} F1={m['f1']:.4f}")
    print(f"FPR={m['false_positive_rate']:.4f} FNR={m['false_negative_rate']:.4f}")
    print("Confusion matrix:", m["confusion_matrix"])
print(f"\nAgreement: {agreement.sum()}/{len(y)} ({agreement.mean():.2%})")
print(f"Disagreements: {(~agreement).sum()}")
print(f"Saved metrics: {metrics_path}")
print(f"Saved event-level predictions: {pred_path}")
print("NOTE: Synthetic, strongly separable dataset; results do not establish real-world performance.")
