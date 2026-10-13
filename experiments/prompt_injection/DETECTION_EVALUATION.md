\# Phase 12A — Detection Evaluation Results



\*\*Project:\*\* Secure \& Explainable AI-Powered SOC  

\*\*Evaluation stage:\*\* Phase 12A — Detection Evaluation  

\*\*Evaluation protocol:\*\* `PHASE12\_EVALUATION\_PROTOCOL.md`  

\*\*Status:\*\* Detection evaluation completed; documentation pending final verification



\---



\## 1. Objective



This evaluation compares the detection performance of two anomaly-detection models:



\- Isolation Forest

\- Autoencoder



The evaluation uses the existing held-out test dataset and the previously frozen model thresholds.



The objectives are to measure detection performance, analyze model agreement and disagreement, investigate false positives and false negatives, and document limitations.



No model retraining, threshold adjustment, or modification of the original experimental results was performed during this analysis.



\## 2. Evaluation Dataset



The held-out test dataset contains 594 events.



| Category | Count | Percentage |

|---|---:|---:|

| Normal events | 570 | 95.96% |

| Attack-labeled events | 24 | 4.04% |

| Total | 594 | 100% |



The positive class is an attack-labeled event (`is\_attack = 1`).



The negative class is a normal event (`is\_attack = 0`).



The dataset is imbalanced, with substantially more normal events than attack-labeled events. Consequently, accuracy alone is insufficient to characterize detection performance.



\### Source files



\- `results/detection\_comparison/test\_metrics.json`

\- `results/detection\_comparison/test\_predictions.csv`

\- `data/processed/splits/test.csv`

\- `data/processed/features/test\_features.csv`

\- `data/processed/features/test\_metadata.csv`

\- `src/preprocessing/prepare\_data.py`



\## 3. Frozen Detection Thresholds



The thresholds were selected using validation data and subsequently frozen before evaluation on the held-out test dataset.



| Model | Frozen threshold |

|---|---:|

| Isolation Forest | 0.164029646520074 |

| Autoencoder | 678.0178934710984 |



The two models produce different types of anomaly scores.



Isolation Forest uses its anomaly score, whereas Autoencoder uses reconstruction mean squared error (MSE).



The numerical values of these scores are not directly comparable across models.



\## 4. Main Performance Results



| Metric | Isolation Forest | Autoencoder |

|---|---:|---:|

| True Positives (TP) | 23 | 24 |

| True Negatives (TN) | 570 | 570 |

| False Positives (FP) | 0 | 0 |

| False Negatives (FN) | 1 | 0 |

| Precision | 100.00% | 100.00% |

| Recall | 95.83% | 100.00% |

| F1-score | 97.87% | 100.00% |

| False Positive Rate | 0.00% | 0.00% |

| False Negative Rate | 4.17% | 0.00% |



Both detectors achieved perfect precision on the evaluated test set.



Isolation Forest correctly identified 23 of the 24 attack-labeled events, missing one event.



Autoencoder correctly identified all 24 attack-labeled events.



Neither detector produced a false positive on the 570 normal events.



These results describe the observed performance on this particular held-out dataset and do not establish perfect detection performance on unseen operational traffic.



\## 5. Confusion Matrices



Rows represent the actual class, and columns represent the predicted class.



\### 5.1 Isolation Forest



| Actual / Predicted | Normal | Attack |

|---|---:|---:|

| Normal | 570 (TN) | 0 (FP) |

| Attack | 1 (FN) | 23 (TP) |



Isolation Forest correctly classified 593 of the 594 test events.



Its only classification error was a false negative.



\### 5.2 Autoencoder



| Actual / Predicted | Normal | Attack |

|---|---:|---:|

| Normal | 570 (TN) | 0 (FP) |

| Attack | 0 (FN) | 24 (TP) |



Autoencoder correctly classified all 594 events in the held-out test set.



This is an observed result for the evaluated dataset, not a guarantee of zero errors in future deployments.



\## 6. Model Agreement and Disagreement



The models were compared using their final binary classifications for the same test events.



| Agreement category | Events |

|---|---:|

| Both predict normal | 570 |

| Both predict anomaly | 23 |

| Isolation Forest only predicts anomaly | 0 |

| Autoencoder only predicts anomaly | 1 |

| Total agreements | 593 |

| Total disagreements | 1 |



\*\*Observed agreement rate:\*\* 593 / 594 = 99.83%.



\*\*Observed disagreement rate:\*\* 1 / 594 = 0.17%.



The models agreed on all 570 normal events and 23 of the 24 attack-labeled events.



The single disagreement occurred on event `3505`.



High agreement indicates similar binary classifications on this test set. It does not imply that the models use identical decision mechanisms or will necessarily agree on different datasets.



\## 7. False Positive Analysis



Neither model produced a false positive.



| Model | False positives |

|---|---:|

| Isolation Forest | 0 |

| Autoencoder | 0 |



Therefore, no representative false-positive case exists in the evaluated test set.



The observed false-positive rate of 0% should not be interpreted as evidence that false positives cannot occur in operational environments.



\## 8. False Negative Analysis — Event 3505



\### 8.1 Identification



Event `3505` was the only false negative produced by Isolation Forest.



The event was labeled as an attack in the held-out test dataset.



| Property | Value |

|---|---|

| Event ID | 3505 |

| Ground-truth label | Attack |

| Isolation Forest prediction | Normal |

| Autoencoder prediction | Anomaly |

| Models agree | False |



\### 8.2 Original Event Characteristics



The original event record contains the following values:



| Feature | Value |

|---|---|

| User | analyst01 |

| Country | SG |

| Device | mobile |

| Protocol | HTTPS |

| Hour | 04:00 |

| Failed authentication attempts | 13 |

| Distance | 5,844.11 km |

| Session duration | 15.16 minutes |

| Outbound traffic | 123.77 MB |



The event includes several potentially suspicious observations, including multiple failed authentication attempts, an unusual activity hour, and a large geographical distance.



These observations are relevant to anomaly analysis but do not independently establish a confirmed real-world security incident.



\### 8.3 Model Scores and Decisions



| Metric | Isolation Forest | Autoencoder |

|---|---:|---:|

| Observed score | 0.160557391 | 25,444.780291 |

| Frozen threshold | 0.164029647 | 678.017893 |

| Threshold comparison | Below threshold | Above threshold |

| Prediction | Normal | Anomaly |

| Classification result | False Negative | True Positive |



The Isolation Forest anomaly score was approximately 0.00347 below its frozen threshold.



The Autoencoder reconstruction MSE was approximately 37.53 times its frozen threshold.



The models therefore produced different classifications for the same attack-labeled event.



The relative threshold comparisons explain the final classifications, but they do not establish which individual input features caused the models to disagree.



\### 8.4 Processed Features



The test preprocessing pipeline uses:



\- OneHotEncoder for categorical features.

\- StandardScaler for numerical features.



The preprocessing pipeline is fitted using normal training records only.



The transformed test features and their metadata are saved separately.



The code constructs both outputs from the same input DataFrame without an explicit row-reordering operation.



The current feature and metadata files each contain 594 rows.



Event `3505` appears exactly once in the metadata, at zero-based row index 258.



Assuming these files were generated together by the inspected preprocessing pipeline, the corresponding processed feature row contains:



| Numerical feature | Processed value |

|---|---:|

| Hour | -3.224298 |

| Failed attempts | 25.348858 |

| Distance | 687.070094 |

| Session minutes | -1.183836 |

| Bytes out | 20.886885 |



These values are transformed model inputs, not original physical measurements.



The categorical representation includes an active indicator for `analyst01` and `HTTPS`. The inspected processed row also contains zero values for the other displayed categorical indicators.



The large numerical transformed values indicate substantial deviations relative to the preprocessing transformation.



However, they do not establish the individual contribution of each feature to the final model prediction.



\### 8.5 Interpretation



The observed disagreement demonstrates that two anomaly-detection methods can classify the same event differently.



Isolation Forest did not cross its frozen anomaly threshold, while Autoencoder produced a reconstruction error substantially above its threshold.



This is consistent with the models having different decision mechanisms and sensitivities.



However, the available evaluation results do not establish a feature-level causal explanation for the disagreement.



A separate model-specific explanation would be necessary to support stronger conclusions about individual feature contributions.



\## 9. Detection Limitations



\### 9.1 Dataset size



The evaluation contains 594 events, including only 24 attack-labeled events.



The relatively small positive class limits the strength of conclusions about attack detection across a broader range of scenarios.



\### 9.2 Dataset imbalance



Approximately 96% of the test records are normal.



For this reason, precision, recall, F1-score, and confusion matrices are more informative than accuracy alone.



\### 9.3 Synthetic experimental context



The evaluation is based on the project's experimental telemetry dataset.



Results may not reflect the variability, noise, and complexity of operational SOC environments.



\### 9.4 Threshold dependence



Both detectors rely on previously frozen thresholds.



Different thresholds could produce different false-positive and false-negative trade-offs.



The thresholds were not modified during this evaluation.



\### 9.5 Feature dependence



The models can only evaluate patterns represented in the available input features.



Relevant security context absent from the dataset cannot be inferred reliably from anomaly scores alone.



\### 9.6 Anomaly versus confirmed attack



An anomaly-detection result indicates statistical or learned deviation from normal patterns.



It is not equivalent to a confirmed malicious action or verified MITRE ATT\&CK technique.



Additional security evidence may be necessary for an operational incident assessment.



\### 9.7 Generalization



The Autoencoder achieved perfect classification on this particular held-out test set.



This does not demonstrate that the model will maintain perfect precision or recall on unseen datasets.



\### 9.8 Explanation limitations



The score and threshold analysis explains how the recorded binary decisions were reached.



It does not independently identify the causal contribution of each feature.



\## 10. Conclusions



The detection evaluation produced the following findings:



1\. Both Isolation Forest and Autoencoder achieved 100% precision on the held-out test set.

2\. Isolation Forest achieved 95.83% recall and 97.87% F1-score.

3\. Autoencoder achieved 100% recall and 100% F1-score.

4\. The models agreed on 593 of 594 events, corresponding to 99.83% agreement.

5\. The only disagreement involved event `3505`, which Isolation Forest missed and Autoencoder detected.

6\. Neither detector produced a false positive.

7\. The observed results support using both models as complementary anomaly-detection signals within the experimental SOC architecture.

8\. The results do not establish operational security effectiveness or universal superiority of one model.



\## 11. Evaluation Integrity



This evaluation follows the frozen Phase 12 Evaluation Protocol.



The analysis uses the existing held-out test results and preserves the original model thresholds.



No test event was excluded because of its classification result.



The false-negative event was retained and analyzed explicitly.



The original detection outputs and preprocessing files were not modified during this evaluation.



\*\*Phase 12A conclusion:\*\* Detection performance, confusion matrices, model agreement, false-positive analysis, false-negative analysis, and detection limitations have been documented for the frozen held-out test set.

