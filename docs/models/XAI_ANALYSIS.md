# Phase 4 — Explainability and Structured Evidence

**Project:** Secure & Explainable AI-Powered SOC  
**Student:** Aviv Rom Horesh  
**Status:** Three representative event-level cases validated; broader validation remains open.

## Objective and approach

Explain the frozen Isolation Forest and Autoencoder outputs without confusing model diagnostics with independent security evidence or causal attribution. No detector was retrained and no validation-selected threshold was changed during this phase.

- **Autoencoder:** Compute squared reconstruction error for each of the 17 transformed features, then group by the nine original telemetry fields. The grouped values are sums of squared errors; overall reconstruction MSE is the sum across all 17 transformed features divided by 17. The grouped values therefore are **not** on the same numerical scale as the overall MSE.
- **Isolation Forest:** Replace one original field at a time with a normal-training reference value in transformed feature space and recompute the anomaly score. `score_drop_when_replaced = original_score - replacement_score`. Positive values mean the replacement reduced the anomaly score. This is a reference-replacement sensitivity diagnostic, **not SHAP**, causal importance, or an additive decomposition. Results depend on the reference and may reflect unrealistic feature combinations or feature interactions.

Both explanations are interpreted alongside the original, unmodified security telemetry. Numerical values from the two explanation methods must not be compared directly.

## Validated examples

The following results were reported by the local scripts and were inspected through their command-line outputs. Labels are used **only for offline evaluation** and are deliberately excluded from operational evidence JSON.

| Event | Offline label | Isolation Forest | Autoencoder | Agreement |
|---|---|---|---|---|
| 3216 | Normal | Normal; score 0.001957 | Normal; MSE 0.151009 | Yes |
| 2624 | Attack | Anomaly; score 0.187445 | Anomaly; MSE 8121.156861 | Yes |
| 3505 | Attack | Normal; score 0.160557 | Anomaly; MSE 25444.780291 | No |

Frozen thresholds selected from validation data: Isolation Forest **0.164029646520074** and Autoencoder **678.0178934710984**. Scores at or above the respective threshold are anomalies.

### Event 3216 — correctly classified normal event

- Autoencoder's largest grouped reconstruction errors: `device` 1.308541, `user` 1.003590, `protocol` 0.211889. Overall MSE remains low at 0.151009.
- Isolation Forest's largest positive score drops after reference replacement: `device` 0.055441 and `user` 0.041657.
- Interpretation: a normal event can still have nonzero reconstruction errors and replacement sensitivity. A prominent field in an explanation is not, by itself, proof of malicious activity.

### Event 2624 — attack detected by both models

- Autoencoder's largest grouped error: `distance_km` 131559.859488, followed by `hour` 2790.199499 and `session_minutes` 2259.706283.
- Isolation Forest's largest positive score drops: `bytes_out_mb` 0.047150, `failed_attempts` 0.040211, `distance_km` 0.037433.
- Replacing any one of those three fields separately reduced the Isolation Forest score below its frozen threshold. This is a local sensitivity observation, not a claim of causation or proof that any single field determines the original classification.

### Event 3505 — model disagreement

**Original telemetry:** `user=analyst01`, `country=SG`, `device=mobile`, `protocol=HTTPS`, `hour=4`, `failed_attempts=13`, `distance_km=5844.112668`, `session_minutes=15.156078`, `bytes_out_mb=123.770367`.

- Isolation Forest scored 0.160557, just below its 0.164030 threshold, and missed the attack.
- Autoencoder MSE was 25444.780291, above its 678.017893 threshold, and detected the attack.
- Autoencoder's largest grouped error was `distance_km` 411339.899107; other substantial grouped errors included `hour` 7632.985558 and `session_minutes` 7295.159735.
- Isolation Forest's largest positive score drops were `failed_attempts` 0.055616, `bytes_out_mb` 0.050378, and `distance_km` 0.037749.
- Replacing `country` had zero effect under the chosen reference-replacement diagnostic. Because the preprocessor encodes unseen categorical values as all zeros, this result requires further investigation; zero sensitivity alone does not establish that geography is irrelevant to the model.

## Structured operational evidence

`src/explainability/build_evidence.py --event-id <ID>` generated:

- `results/explainability/evidence/event_3216_evidence.json`
- `results/explainability/evidence/event_2624_evidence.json`
- `results/explainability/evidence/event_3505_evidence.json`

Each version-1.0 object preserves nine raw telemetry fields, the two frozen model scores/thresholds/predictions, agreement status, both model-specific explanations, provenance, and an analyst notice. `mitre_mapping`, `llm_recommendation`, and `human_decision` are currently `null` for later pipeline stages. **Ground-truth labels are not included in operational evidence.** The JSON is a structured record, not evidence that downstream trust boundaries or end-to-end integration have already been tested.

## Limitations and outstanding checks

1. This dataset is synthetic and strongly separable; explanations and detection results do not establish real-world SOC performance.
2. Reconstruction error and reference-replacement sensitivity explain different properties and do not measure causal importance.
3. Reference replacements may create unrealistic combinations, depend on selected reference values, and do not capture feature interactions.
4. Unknown categories are represented by all-zero one-hot groups; inspect their influence separately before drawing categorical conclusions.
5. The held-out test set contained **no false positives** from either detector. Therefore, a false-positive explanation case cannot be honestly presented from this evaluation; an explicitly labeled synthetic stress case could be developed separately without retuning the frozen detectors.
6. Three selected cases demonstrate functionality, not broad explanation fidelity or stability. Additional consistency checks and an optional visualization remain useful before claiming full Phase 4 validation.
7. The scripts' CLI displays offline `Actual label` for research diagnostics; this label must not enter the operational evidence object or later LLM input.

## Automated evidence-integrity tests

After generating the three case-study evidence objects, four automated
`unittest` checks passed locally (`Ran 4 tests ... OK`):

- `test_explanations_cover_original_fields`: explanation field groups cover the original telemetry schema.
- `test_no_ground_truth_or_premature_decisions`: operational evidence excludes the true attack label and does not populate later MITRE/LLM/human decisions.
- `test_raw_fields_match_original_events`: stored raw evidence matches the source test events.
- `test_saved_records_match_frozen_predictions`: saved detection records match the frozen test predictions.

Run from the repository root:

```cmd
python -m unittest discover -s tests -p "test_evidence.py" -v
```

These tests establish **structural integrity and consistency for the three
selected records**, not broad explanation fidelity, robustness, causal
validity, or security of future downstream components. No false positives
were observed on the held-out test set, so a false-positive explanation
was not evaluated. The test file should be committed alongside this
checkpoint.

## Reproduction

From the repository root, with the original frozen models and local preprocessed data available:

```cmd
python src\explainability\explain_autoencoder.py --event-id 3505
python src\explainability\explain_isolation_forest.py --event-id 3505
python src\explainability\build_evidence.py --event-id 3505
```

Repeat with IDs `3216` and `2624`. Model binaries and locally processed data are intentionally excluded from Git. The committed JSON examples and scripts preserve the documented outputs and implementation.
