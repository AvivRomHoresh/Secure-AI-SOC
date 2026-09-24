# Detection Model Comparison — Held-Out Test Evaluation

**Project:** Secure & Explainable AI-Powered SOC  
**Student:** Aviv Rom Horesh  
**Phase:** 3 — Anomaly Detection  
**Evaluation:** Frozen Isolation Forest and Autoencoder on the held-out synthetic test partition

## 1. Experimental Protocol

Both detectors were trained on the same 2,660 normal-only training events and the same 17 preprocessed features. Their decision thresholds were selected using the separate validation partition (594 events). The trained models and full-precision validation-selected thresholds were frozen before evaluation on the held-out test partition. The test partition contains **594 events: 570 normal and 24 labeled attacks**. Ground-truth labels were used for evaluation, not as detector inputs. No post-test model or threshold tuning is permitted.

- **Isolation Forest:** anomaly score = `-decision_function(X)`; classify as attack when score >= **0.164029646520074**.
- **Autoencoder:** per-event mean squared reconstruction error; classify as attack when error >= **678.0178934710984**.
- **Reproducible test script:** `src/detection/evaluate_detectors_test.py`.
- **Saved outputs:** `results/detection_comparison/test_metrics.json` and `results/detection_comparison/test_predictions.csv`.

## 2. Held-Out Test Results

| Metric | Isolation Forest | Autoencoder |
|---|---:|---:|
| Precision | 1.0000 | 1.0000 |
| Recall | 0.9583 | 1.0000 |
| F1-score | 0.9787 | 1.0000 |
| False positive rate (FPR) | 0.0000 | 0.0000 |
| False negative rate (FNR) | 0.0417 | 0.0000 |
| True negatives (TN) | 570 | 570 |
| False positives (FP) | 0 | 0 |
| False negatives (FN) | 1 | 0 |
| True positives (TP) | 23 | 24 |
| Predicted anomalies | 23 | 24 |

**Agreement:** 593 of 594 test events (**99.83%**); **one disagreement**. This is agreement in binary decisions, not calibrated confidence or proof of independent detection quality.

## 3. Disagreement Case — Event 3505

The only disagreement was on a **labeled attack**. Its original held-out telemetry is:

| Field | Value |
|---|---|
| `event_id` | 3505 |
| `user` | analyst01 |
| `country` | SG |
| `device` | mobile |
| `protocol` | HTTPS |
| `hour` | 4 |
| `failed_attempts` | 13 |
| `distance_km` | 5844.112668 |
| `session_minutes` | 15.156078 |
| `bytes_out_mb` | 123.770367 |
| `is_attack` | 1 |

- **Isolation Forest:** score **0.160557**, below its frozen threshold **0.164030**; predicted **normal** (false negative).
- **Autoencoder:** reconstruction MSE **25444.780291**, above its frozen threshold **678.017893**; predicted **attack** (true positive).

The event has observable features worth investigating, including 13 failed attempts, a large recorded distance and a 04:00 event hour. These facts do **not** establish which features caused either model's decision. Feature-level attribution belongs to the subsequent XAI/evidence phase; do not claim a causal model explanation from this comparison alone. The two score scales are fundamentally different and should not be compared numerically against each other.

## 4. Interpretation and Limitations

The Autoencoder detected the single labeled attack missed by Isolation Forest on this particular test partition. Retaining both outputs and explicit disagreement flags can provide useful additional information to a human analyst; this experiment does not establish how a production aggregation rule should classify future disagreements.

**Critical limitations:** The telemetry is synthetic and intentionally strongly separable, including large differences in attack-related features. The test partition has only 24 labeled attacks. Random stratified splitting may also place events associated with the same users in multiple partitions. Consequently, very high test metrics do **not** demonstrate real-world detection performance, resilience to novel attack types, or model robustness under distribution shift. The test partition has now been used for final reporting; do not use it for further model or threshold selection.

## 5. Next Phase Handoff

Preserve `event_id`, the original telemetry, each model's separate score and binary prediction, the agreement flag, and ground truth strictly for offline evaluation. In the next XAI/evidence phase, analyze event 3505 without retroactively changing these test results. Keep model outputs distinct from validated evidence and from any later LLM recommendation or human decision.
