# Synthetic Login Telemetry Dataset

## 1. Overview

This dataset contains synthetic security telemetry representing

normal and potentially malicious login activity.

The dataset is based on the synthetic data generation code

provided in the course's Anomaly Detection laboratory.

It serves as the initial dataset for the Secure & Explainable

AI-Powered SOC project.

## 2. Dataset Characteristics

| Property | Value |

|---|---|

| Dataset type | Synthetic login telemetry |

| Total records | 3,960 |

| Normal records | 3,800 |

| Attack records | 160 |

| Total features/columns | 10 |

| Random seed | 42 |

| Missing values | 0 |

| Duplicate records | 0 |

Attack prevalence: approximately 4.04%.

## 3. Dataset Features

| Feature | Description |

|---|---|

| user | User account identifier |

| country | Country associated with the login |

| device | Device used for authentication |

| protocol | Communication protocol |

| hour | Hour of activity |

| failed_attempts | Number of failed authentication attempts |

| distance_km | Simulated geographical distance |

| session_minutes | Session duration |

| bytes_out_mb | Outbound data volume |

| is_attack | Ground-truth label |

The `is_attack` column uses the following values:

- 0: Normal activity

- 1: Simulated attack activity

The ground-truth label must not be used as an input

feature during model training.

## 3.1. Evidence and Model Feature Separation

The project distinguishes between four types of data.

### Raw Security Evidence

The original telemetry fields are preserved for
security analysis and event-level explanations.

These fields include:

- user
- country
- device
- protocol
- hour
- failed_attempts
- distance_km
- session_minutes
- bytes_out_mb

### Model Input Features

The initial candidate model features are the nine
telemetry fields listed above.

Categorical fields will require encoding.
Numerical fields may require scaling.

The final feature representation and any additional
engineered features will be documented in Phase 2.

### Ground Truth

The is_attack column represents the synthetic
ground-truth label.

It will be used for stratified dataset splitting,
validation, and evaluation.

It must never be included in model input features.

### Event Identification

The event_id column is assigned before dataset splitting.

It preserves traceability between the original telemetry,
processed features, model predictions, explanations,
and subsequent SOC analysis.

It must never be included in model input features.

The original raw dataset contains ten columns.
The event_id column is additional metadata introduced
during dataset splitting.

### Leakage Prevention

Preprocessing transformations will be fitted using
the appropriate training data only.

Validation and test records will be transformed using
the fitted preprocessing artifacts.

The test set will remain isolated until the final
evaluation procedure has been established.

## 4. Data Generation

The dataset is generated using NumPy and Pandas.

Normal activity follows predefined user profiles,

including typical devices, countries and working hours.

Attack activity introduces unusual behavioral patterns,

including:

- Login attempts from unusual countries.

- Unknown or unmanaged devices.

- Activity during unusual hours.

- Multiple failed authentication attempts.

- Unusually large geographical distances.

- Increased outbound data volume.

A fixed random seed ensures reproducible data generation

under the same software environment.

Generation script:

`src/data_generation/generate_telemetry.py`

Generated dataset:

`data/raw/synthetic_login_telemetry.csv`

## 5. Data Validation

The following checks were executed successfully:

- Dataset dimensions: 3,960 rows and 10 columns.

- Class distribution: 3,800 normal and 160 attack records.

- Missing values: 0.

- Duplicate rows: 0.

These checks establish basic structural integrity.

They do not independently validate the realism of the

simulated security events.

## 6. Research Limitations

The dataset is synthetic rather than real-world SOC telemetry.

Attack events were generated using deliberately unusual

feature combinations, which may make them easier to detect

than realistic attacks.

Consequently, strong detection results on this dataset

would not automatically demonstrate equivalent performance

in a production SOC environment.

The dataset currently contains an hour-of-day feature,

but does not include complete event timestamps.

This limitation must be considered if temporal analysis

or chronological train/test splitting is introduced.

## 7. Intended Use

The dataset will support:

1\. Security telemetry preprocessing.

2\. Isolation Forest anomaly detection.

3\. Autoencoder anomaly detection.

4\. Model evaluation using ground-truth labels.

5\. Explainability and evidence extraction.

6\. Evidence-based security analysis.

The project's adversarial experiments will examine

manipulation of the AI reasoning layer.

The underlying security telemetry must remain identical

across the baseline, adversarial and defended conditions.

## 8. Reproducibility

The dataset generation process uses a fixed random seed:

`SEED = 42`

The dataset generation script is located at:

`src/data_generation/generate_telemetry.py`

The generated raw dataset is stored at:

`data/raw/synthetic_login_telemetry.csv`

Both the generation script and the raw dataset
are tracked in the Git repository.

The dataset splitting script is located at:

`src/analysis/split_data.py`

The splitting strategy uses stratified random sampling
with a fixed random state of 42.

The resulting partitions are:

- Training: 2,772 events.
- Validation: 594 events.
- Test: 594 events.

The generated partitions are stored locally in:

`data/processed/splits/`

The partitioning methodology is documented in:

`docs/datasets/DATA_SPLITTING.md`

The software environment and dependencies are
documented separately in the project.