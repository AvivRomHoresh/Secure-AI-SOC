\# Isolation Forest — Model Training and Validation



\## 1. Objective



The objective of this experiment is to train an Isolation Forest

model to detect anomalous security events in synthetic login telemetry.



The model is trained exclusively on normal events and assigns an

anomaly score to previously unseen observations.



Higher anomaly scores indicate more anomalous behavior.



\## 2. Dataset and Preprocessing



The experiment uses the synthetic login telemetry dataset

generated during Phase 1.



The dataset was divided into training, validation, and test sets

using a stratified 70/15/15 split with random seed 42.



The model uses 17 preprocessed features.



Preprocessing includes:

\- One-hot encoding of categorical features.

\- Standard scaling of numerical features.

\- Exclusion of event identifiers and ground-truth labels.



The preprocessing pipeline was fitted exclusively on normal

training observations.



\## 3. Model Configuration



Algorithm: Isolation Forest



Configuration:

\- Training samples: 2,660 normal events

\- Input features: 17

\- Number of estimators: 100

\- Random seed: 42

\- Contamination: auto

\- Parallel processing: enabled



The model was trained without using attack labels.



The default Isolation Forest classification threshold was not

used for the reported validation results.



\## 4. Anomaly Scoring



Anomaly scores were calculated using:



&#x20;   anomaly\_score = -model.decision\_function(X)



The sign was reversed so that higher scores represent

greater abnormality.



Scores were saved alongside their corresponding event IDs

and ground-truth labels for evaluation purposes.



Ground-truth labels were not provided as model inputs.



\## 5. Validation Dataset



The validation dataset contains 594 events:



| Event Type | Count |

|------------|------:|

| Normal | 570 |

| Attack | 24 |

| Total | 594 |



The following score statistics were observed:



| Statistic | Normal | Attack |

|-----------|-------:|-------:|

| Mean | -0.0100 | 0.1881 |

| Standard deviation | 0.0467 | 0.0135 |

| Minimum | -0.0932 | 0.1640 |

| Maximum | 0.1513 | 0.2102 |



The observed validation scores show complete separation

between normal and attack events.



This observation applies only to the current synthetic

validation dataset.



\## 6. Threshold Selection



The classification threshold was selected using the

validation dataset.



Every distinct observed anomaly score was evaluated as a

candidate threshold. An additional candidate above the

maximum score represented the all-normal prediction.



The selection criterion was maximum F1-score.



When multiple thresholds achieved the same F1-score,

the highest threshold was selected.



Classification rule:



&#x20;   predicted\_attack = anomaly\_score >= threshold



Selected threshold:



&#x20;   0.164030



The selected threshold was saved for subsequent evaluation.



\## 7. Validation Results



| Metric | Result |

|--------|-------:|

| Precision | 1.0000 |

| Recall | 1.0000 |

| F1-score | 1.0000 |



Confusion matrix:



| Actual / Predicted | Normal | Attack |

|--------------------|-------:|-------:|

| Normal | 570 | 0 |

| Attack | 0 | 24 |



Additional results:



\- True negatives (TN): 570

\- False positives (FP): 0

\- False negatives (FN): 0

\- True positives (TP): 24



All 24 attack events were detected without false positives

on the validation dataset.



\## 8. Limitations



The results should be interpreted with several limitations:



1\. The telemetry is synthetic and contains strongly

&#x20;  distinguishable normal and attack characteristics.



2\. The validation dataset contains only 24 attack events.



3\. The threshold was selected using validation labels.

&#x20;  Consequently, the reported validation metrics are not

&#x20;  an independent estimate of generalization performance.



4\. The dataset was randomly divided rather than

&#x20;  chronologically divided.



5\. The current experiment does not establish performance

&#x20;  on real-world security telemetry.



\## 9. Reproducibility



Training script:



&#x20;   src/detection/train\_isolation\_forest.py



Validation scoring script:



&#x20;   src/detection/evaluate\_isolation\_forest.py



Threshold selection script:



&#x20;   src/detection/select\_isolation\_forest\_threshold.py



Saved model:



&#x20;   models/isolation\_forest/isolation\_forest.joblib



Saved feature schema:



&#x20;   models/isolation\_forest/feature\_names.json



Validation scores:



&#x20;   results/isolation\_forest/validation\_scores.csv



Threshold selection results:



&#x20;   results/isolation\_forest/threshold\_selection.json



\## 10. Next Steps



The selected threshold will remain fixed for subsequent

evaluation.



The held-out test dataset will not be used for additional

model training or threshold optimization.



The next detection component will be an Autoencoder,

allowing comparison between two anomaly detection methods.



The models will subsequently contribute to the

explainable SOC analysis pipeline.

