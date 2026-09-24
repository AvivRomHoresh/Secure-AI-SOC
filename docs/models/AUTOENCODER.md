# Autoencoder — Model Training and Validation

## 1. Objective
Train a lightweight reconstruction-based anomaly detector on normal synthetic login telemetry. The model learns to reconstruct normal events; high reconstruction error is treated as an anomaly score.

## 2. Dataset and preprocessing
- Dataset: synthetic login telemetry generated for this project.
- Split: stratified 70% training, 15% validation, 15% held-out test (random seed 42).
- Model training: **2,660 normal training events only**.
- Inputs: **17 preprocessed features** produced by the shared preprocessing pipeline (one-hot encoding and standard scaling). Event identifiers and attack labels are excluded from model inputs.
- Validation: **594 events** (570 normal and 24 attacks).
- The held-out test set has not been used for training, threshold selection, or evaluation.

## 3. Architecture and training
The implementation uses `sklearn.neural_network.MLPRegressor` with normal events as both inputs and reconstruction targets (`X -> X`). It is an MLP-based autoencoder, not a TensorFlow/PyTorch implementation.

| Parameter | Value |
| --- | --- |
| Architecture | 17 -> 8 -> 4 -> 8 -> 17 |
| Activation | ReLU |
| Optimizer | Adam |
| Alpha (L2) | 0.0001 |
| Batch size | 64 |
| Initial learning rate | 0.001 |
| Maximum iterations | 500 |
| Random seed | 42 |
| Training strategy | Normal-only |

Observed training output:
- Actual iterations: **60**.
- Final reported training loss: **0.083025**.
- Mean per-event training reconstruction MSE: **0.165873**.

The reported MLP training loss and the mean per-event reconstruction MSE are related but are not the same reported quantity; compare validation events using the explicitly computed per-event reconstruction MSE.

## 4. Validation anomaly scores
For each validation event, calculate the mean squared error between its 17 input features and its reconstruction. Larger scores indicate greater deviation from patterns learned from normal training events.

| Actual class | Events | Mean reconstruction MSE | Minimum | Maximum |
| --- | ---: | ---: | ---: | ---: |
| Normal | 570 | 0.176235 | 0.058768 | 0.869302 |
| Attack | 24 | 21202.953396 | 678.017893 | 56217.124496 |

In this validation split, the largest normal-event score is lower than the smallest attack-event score.

## 5. Threshold selection and validation results
Threshold selection uses **validation data only**. Candidate thresholds are all distinct observed validation scores, plus a candidate immediately above the maximum score. The selected threshold maximizes validation F1; ties are resolved in favor of the highest threshold. Predict an attack when `reconstruction_mse >= selected_threshold`.

- Selected threshold: **678.017893** (rounded for display; retain the full-precision value from the JSON file).
- Precision: **1.0000**.
- Recall: **1.0000**.
- F1-score: **1.0000**.
- Confusion matrix: **TN=570, FP=0, FN=0, TP=24**.

These are validation results used in model development, **not** independent held-out test results.

## 6. Interpretation and limitations
The validation scores show complete separation in this split, but the synthetic dataset contains unusually distinctive attack features. The attack sample is small (24 validation events), and the threshold was optimized on the same validation labels used to report the metrics. The very large attack reconstruction errors should not be interpreted as evidence of realistic production SOC performance. No claims about real-world generalization can be made from these results.

Freeze the trained model and selected threshold before using the held-out test set. Do not adjust either in response to test-set results. Later comparison with Isolation Forest should distinguish validation findings from independent test evaluation.

## 7. Reproducibility and artifacts
Run the scripts from the repository root in this order:

```cmd
python src\detection\train_autoencoder.py
python src\detection\evaluate_autoencoder.py
python src\detection\select_autoencoder_threshold.py
```

Relevant artifacts:
- `src/detection/train_autoencoder.py` — normal-only training.
- `src/detection/evaluate_autoencoder.py` — validation reconstruction scores.
- `src/detection/select_autoencoder_threshold.py` — validation threshold selection.
- `models/autoencoder/autoencoder.joblib` — trained model (local artifact; do not commit the binary).
- `models/autoencoder/feature_names.json` — ordered feature schema.
- `models/autoencoder/training_info.json` — training metadata (note: its initial `threshold_selected` and `validation_evaluated` fields describe the state immediately after training; the later threshold-selection result is authoritative).
- `results/autoencoder/validation_scores.csv` — per-event validation scores.
- `results/autoencoder/threshold_selection.json` — selected threshold and validation metrics.

## 8. Next steps
1. Record the Autoencoder checkpoint in `docs/PROJECT_PLAN.md` and commit the code, documentation, feature schema, training metadata, and validation results. Do not commit the serialized model.
2. Freeze both models and their thresholds.
3. Evaluate both models on the held-out test set once, then compare their predictions and agreement.
