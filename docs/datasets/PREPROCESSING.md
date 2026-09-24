# Phase 2 — Preprocessing and Feature Engineering

**Project:** Secure & Explainable AI-Powered SOC  
**Student:** Aviv Rom Horesh  
**Date:** 24 September 2026  
**Status:** Preprocessing implementation and reported checks completed; integrated-demo reuse and downstream end-to-end traceability remain future work.

## 1. Objective and inputs

Convert the Phase 1 synthetic login telemetry into reproducible model inputs while keeping original event evidence and ground-truth labels separate. Phase 1 generated 3,960 synthetic events (3,800 normal, 160 attacks), assigned `event_id` before splitting, and produced stratified partitions using seed 42: training 2,772 (2,660 normal, 112 attack), validation 594 (570 normal, 24 attack), and test 594 (570 normal, 24 attack).

Input files are generated locally under `data/processed/splits/`. The implementation is `src/preprocessing/prepare_data.py`, configured through `config/project_config.json`.

## 2. Transformations

| Original fields | Processing | Purpose |
| --- | --- | --- |
| `user`, `country`, `device`, `protocol` | `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` | Convert categorical telemetry into numeric features while accepting unseen values at inference time. |
| `hour`, `failed_attempts`, `distance_km`, `session_minutes`, `bytes_out_mb` | `StandardScaler` | Provide a consistent numeric scale, especially for the planned Autoencoder. |
| `event_id` | Excluded from features; stored as metadata | Link model outputs back to source events. |
| `is_attack` | Excluded from features; stored as metadata | Reserve ground truth for evaluation rather than allowing label leakage. |

No new behavioral features were engineered in this version; encoding and scaling operate on the nine original telemetry fields. The selected dataset required no imputation: the script rejects missing values, missing required fields, invalid labels, or duplicate IDs within a partition. It does not silently clean malformed records.

**Training-only fitting:** The `ColumnTransformer` is fitted on **2,660 normal training records only**, then reused unchanged to transform normal training, full validation, and full test sets. The 112 attack-labeled training records are not used in fitting or included in the exported normal-only training feature matrix. Validation and test labels remain separate from model inputs.

**Unknown categories:** `handle_unknown="ignore"` represents an unseen category with zeros across that field's one-hot columns. This prevents transformation failures, but may affect anomaly detection and explanation quality; interpret this behavior explicitly during evaluation.

## 3. Saved outputs and reproducibility

- `data/processed/features/train_normal_features.csv` and `train_normal_metadata.csv`: 2,660 rows.
- `data/processed/features/validation_features.csv` and `validation_metadata.csv`: 594 rows.
- `data/processed/features/test_features.csv` and `test_metadata.csv`: 594 rows.
- Every feature matrix has **17 columns**; metadata contains `event_id` and `is_attack` in original row order.
- `models/preprocessing/preprocessor.joblib`: fitted encoder/scaler pipeline.
- `models/preprocessing/feature_names.json`: ordered output feature names.

From the repository root with `.venv` activated, regenerate the Phase 1 splits if necessary, then run:

```cmd
python src\preprocessing\prepare_data.py
```

Generated data, the `.joblib` artifact, and generated feature-name JSON are ignored by Git. To reproduce outputs on another machine, regenerate the Phase 1 input partitions and rerun this script. Never load `.joblib` files from untrusted sources.

## 4. Observed run and verification

The user ran the script and reported:

```text
Normal training records: 2660
Processed feature count: 17
train_normal: 2660 events, 17 features
validation: 594 events, 17 features
test: 594 events, 17 features
Preprocessing completed successfully.
```

Additional independent command-line checks reported:

| Check | Observed result |
| --- | --- |
| Feature matrices contain neither `event_id` nor `is_attack` | Passed for all three exported partitions |
| Feature and metadata row counts align | Passed for all three partitions |
| Event IDs unique within each exported partition | Passed |
| Saved scaler means match normal-only training data | `True` |
| Saved scaler training sample count | `2660.0`, expected `2660` |
| Encoder categories match normal-only training categories | `True` |
| Encoder handles an artificially unseen category | `True` |
| Recomputed validation feature names, shape, and values match saved CSV | `True` for all three |

These checks support the implementation's training-only preprocessing and deterministic reuse on validation data. They do **not** yet establish integrated-demo behavior, downstream end-to-end event traceability, or cross-partition ID disjointness. These should be checked separately as integration progresses.

## 5. Limitations and next actions

The source data are synthetic, and Phase 1 identified unusually strong normal/attack separation in some fields. Detection results must not be generalized to production SOC traffic without additional evidence. Row-level stratified splitting, rather than chronological splitting, was used because the dataset lacks complete timestamps. Unseen-category zero encoding also deserves attention in later XAI analysis.

Before Phase 3, decide whether any additional justified behavioral features are needed; changing the feature schema later requires retraining. During later integration, verify saved-transformer reuse in the demo and trace an `event_id` from raw evidence through detection, XAI, MITRE mapping, LLM recommendation, and the independent human decision. The final test set should remain reserved for final evaluation rather than iterative threshold selection.
