# Exploratory Data Analysis (EDA)

## 1. Objective

The purpose of this analysis is to examine the synthetic login

telemetry dataset, evaluate its quality, investigate feature

distributions, and identify limitations before preprocessing

and anomaly detection.

## 2. Dataset Overview

The dataset contains 3,960 synthetic login events and 10 columns.

Class distribution:

| Class | Events | Percentage |

|-------|--------|------------|

| Normal (0) | 3,800 | 95.96% |

| Attack (1) | 160 | 4.04% |

The dataset is imbalanced, with attack events representing

approximately 4% of all records.

The `is\_attack` column provides the synthetic ground truth.

It will be used for evaluation and appropriate dataset

partitioning, but excluded from model input features.

## 3. Data Quality

The following checks were performed:

\- Missing values: 0.

\- Duplicate records: 0.

\- Invalid numeric values: 0 for the defined validation checks.

\- All expected dataset columns are present.

The dataset passed the initial data-quality checks.

These checks do not establish that the synthetic events

accurately represent real-world security environments.

## 4. Numerical Feature Analysis

### 4.1 Failed Login Attempts

Normal events contain between 0 and 4 failed attempts.

Attack events contain between 5 and 17 failed attempts.

There is no overlap between the two classes for this feature.

Consequently, a simple threshold could perfectly separate

the two classes in the current dataset.

### 4.2 Geographic Distance

Normal events have geographic distances between approximately

0 and 54 km.

Attack events have distances between approximately

857 and 8,925 km.

There is no overlap between the classes.

This feature provides a particularly strong separation

between normal and attack events in the synthetic dataset.

### 4.3 Outbound Traffic

Normal events have outbound traffic values between

approximately 0.64 and 67.52 MB.

Attack events have values between approximately

19.93 and 935.48 MB.

Unlike failed attempts and geographic distance,

this feature exhibits some overlap between classes.

Therefore, outbound traffic alone cannot perfectly

separate normal and attack events.

## 5. Categorical Feature Analysis

The categorical analysis revealed additional limitations.

All normal events originate from Israel (IL), while

all attack events originate from other countries.

Additionally, normal and attack events use completely

different device categories.

These characteristics introduce artificial class

separation and may allow models to exploit dataset-specific

patterns instead of learning generalizable suspicious behavior.

The protocol and user features exhibit overlap between

normal and attack events.

## 6. Research Implications

The dataset is suitable for implementing and testing

the initial anomaly-detection pipeline.

However, several features provide unusually strong

separation between normal and attack events.

As a result, high detection performance on this dataset

must not be interpreted as evidence of equivalent

performance in real-world SOC environments.

The evaluation will therefore:

1\. Report multiple detection metrics rather than accuracy alone.

2\. Preserve the original synthetic dataset for reproducibility.

3\. Document the limitations introduced by artificial

&#x20;  class separation.

4\. Consider an additional feature-ablation experiment

&#x20;  to investigate dependence on strongly separating features.

The proposed ablation experiment is an additional analysis,

not a replacement for the original evaluation.

## 7. EDA Figures

The following figures were generated:

\- `class\_distribution.png`

\- `hour\_distribution.png`

\- `failed\_attempts\_distribution.png`

\- `distance\_km\_distribution.png`

\- `session\_minutes\_distribution.png`

\- `bytes\_out\_mb\_distribution.png`

Location:

`results/figures/eda/`

These figures illustrate the class distribution and

numerical feature distributions for normal and attack events.

## 8. Conclusions

The initial EDA confirmed that the dataset contains

3,960 events, has a substantial class imbalance, and

passes the defined data-quality checks.

Several numerical and categorical features exhibit

complete separation between normal and attack events.

These characteristics must be considered when

interpreting the results of Isolation Forest and

Autoencoder.

The next step is to define a reproducible

train/validation/test partitioning strategy before

implementing preprocessing.

