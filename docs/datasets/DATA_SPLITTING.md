# Dataset Splitting Strategy

## 1. Objective

The purpose of this stage is to establish a reproducible

train/validation/test partitioning strategy for the

Secure \& Explainable AI-Powered SOC project.

The same partitions will be used to evaluate both

Isolation Forest and Autoencoder.

## 2. Dataset

The dataset contains 3,960 synthetic login events:

\- Normal events: 3,800

\- Attack events: 160

\- Random seed: 42

The original dataset is preserved without modification.

## 3. Partitioning Strategy

The dataset was divided using stratified random sampling.

| Partition | Percentage | Normal | Attack | Total |

|-----------|------------|--------|--------|-------|

| Training | 70% | 2660 | 112 | 2772 |

| Validation | 15% | 570 | 24 | 594 |

| Test | 15% | 570 | 24 | 594 |

| Total | 100% | 3800 | 160 | 3960 |

Stratification preserves approximately the same

normal-to-attack ratio across all three partitions.

The partitioning procedure uses:

\- `train\_test\_split` from scikit-learn.

\- `random\_state=42`.

\- Stratification based on `is\_attack`.

The original dataset does not contain complete timestamps.

Consequently, chronological partitioning is not possible.

## 4. Event Traceability

The original dataset does not contain unique event IDs.

Before partitioning, a sequential `event\_id` was assigned

to every record.

Event IDs are preserved in all three partitions.

This enables future model predictions, explanations,

MITRE ATT\&CK mappings, and LLM recommendations to be

linked to their original security telemetry.

The assigned IDs identify rows in the generated dataset.

They are not original identifiers from a real SOC system.

## 5. Model Training Strategy

Both anomaly-detection models will use the same

training, validation, and test partitions.

The planned training strategy is to fit both

Isolation Forest and Autoencoder using only the

2,660 normal events in the training partition.

The 112 attack events in the training partition

will not be used to fit either detector.

The validation partition will be used for

model development and threshold selection.

The test partition will remain untouched until

the evaluation procedure has been finalized.

This approach enables a controlled comparison

between the two anomaly-detection models.

## 6. Data Leakage Prevention

The following precautions will be applied:

1\. The `is\_attack` label will be excluded from

&#x20;  model input features.

2\. The `event\_id` identifier will also be excluded

&#x20;  from model input features.

3\. Preprocessing transformations will be fitted

&#x20;  exclusively on the appropriate training data.

4\. The fitted preprocessing transformations will

&#x20;  be reused for validation and testing.

5\. The test partition will not be used for

&#x20;  model training, hyperparameter tuning,

&#x20;  threshold selection, or feature selection.

6\. All experimental results will preserve

&#x20;  the original event identifiers.

The implementation of these precautions will

be verified during preprocessing and evaluation.

## 7. Reproducibility

The partitioning procedure is implemented in:

`src/analysis/split\_data.py`

The generated partitions are stored in:

\- `data/processed/splits/train.csv`

\- `data/processed/splits/validation.csv`

\- `data/processed/splits/test.csv`

The source dataset is:

`data/raw/synthetic\_login\_telemetry.csv`

Using the same source dataset, software environment,

random seed, and partitioning script should reproduce

the same partitions.

## 8. Limitations

The dataset is synthetic and contains several

features that strongly separate normal events

from attack events.

Additionally, the dataset does not contain complete

timestamps or real-world event identifiers.

Stratified random splitting preserves class

proportions but does not simulate chronological

deployment or distribution changes over time.

Consequently, the final evaluation will measure

performance on this particular synthetic dataset

rather than establish real-world SOC performance.

## 9. Next Steps

Phase 2 will implement preprocessing and feature

engineering.

The preprocessing pipeline will:

\- Preserve original security evidence.

\- Exclude labels and event IDs from model features.

\- Encode categorical variables.

\- Scale numerical features where appropriate.

\- Fit transformations using training data only.

\- Apply identical transformations to validation

&#x20; and test data.

\- Save the fitted preprocessing artifacts.

The resulting processed data will be used in

Phase 3 for Isolation Forest and Autoencoder.

