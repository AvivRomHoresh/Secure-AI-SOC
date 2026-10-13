# Secure & Explainable AI-Powered SOC

**Final project — Introduction to AI-Driven Cybersecurity (Summer 2026)**
**Student:** Aviv Rom Horesh
**Lecturer:** Andrei Kozakhov
**Project type:** Integrated final project (Type 2)

> **AI assists. Humans decide.** An experimental, evidence-first SOC prototype, not a production security system.

## Overview

This completed project evaluates a lightweight SOC workflow integrating **Isolation Forest and Autoencoder anomaly detection**, model-specific explanation diagnostics, structured evidence, conservative **MITRE ATT&CK screening**, a local **Ollama LLM (`llama3.2:3b`)**, application-layer security controls, and independent human review.

The security experiment asks whether malicious instructions in untrusted AI-visible context can manipulate LLM recommendations while **the underlying telemetry stays unchanged**, and whether defenses contain the resulting outputs. Raw model susceptibility and application-layer containment are reported separately.

## Architecture

```text
Synthetic login telemetry
        ↓
Preprocessing + frozen Isolation Forest / Autoencoder
        ↓
Model-specific XAI diagnostics + structured evidence
        ↓
Deterministic MITRE ATT&CK screening
        ↓
Local LLM (advisory recommendation)
        ↓
Input/output validation and withholding controls
        ↓
Independent human analyst decision
```

An anomaly score is not proof of compromise; XAI diagnostics are not causal explanations; a MITRE candidate is not confirmed attribution; and an LLM recommendation is not an operational decision.

## Evaluated results

### Detection — held-out synthetic test set

The dataset contains **3,960 synthetic login events**, stratified into train/validation/test partitions (70/15/15; seed 42). The **594-event** test partition contains **570 normal and 24 attack-labeled events**.

| Measure | Isolation Forest | Autoencoder |
|---|---:|---:|
| TP / TN / FP / FN | 23 / 570 / 0 / 1 | 24 / 570 / 0 / 0 |
| Precision | 100.00% | 100.00% |
| Recall | 95.83% | 100.00% |
| F1 | 97.87% | 100.00% |

Detector agreement: **593/594 (99.83%)**. Event `3505` was missed by Isolation Forest but detected by Autoencoder. These are results on a **separable synthetic dataset**, not evidence of real-world detection performance.

### AI security — recorded local LLM experiment

The official experiment manifest contains **63 runs across three underlying synthetic incidents**: 9 Baseline, 27 Adversarial, and 27 Defended. Direct, Indirect, and Authority prompt-injection families were tested. The primary raw-model attack-success criterion was **S5 = Yes** (attacker-requested deviation followed).

| Outcome | Adversarial | Defended |
|---|---:|---:|
| Raw-model attacker-directed outcomes | 5/27 (18.52%) | 2/27 (7.41%) |
| Recommendations withheld downstream | See evaluation report | 27/27 |

In the Defended condition, all nine Direct attacks were rejected before model execution. **All 27 defended recommendations were withheld**; this is containment with a substantial **security–utility tradeoff**, not proof of model immunity. These results are **descriptive**, not statistically significant; repeated runs are not independent incidents.

## Explainability and MITRE scope

- **Autoencoder:** grouped squared reconstruction-error diagnostics across original telemetry fields.
- **Isolation Forest:** normal-reference replacement sensitivity, **not SHAP** and not causal attribution.
- **MITRE:** `mitre-t1110-screen-v0.1` screens original failed-attempt counts. At least five failures yield `insufficient_evidence` and a possible, unconfirmed **T1110 / TA0006** indicator; otherwise `no_mapping`. Neither outcome proves an attack or benignness.

## Quick start — Windows CMD

From the repository root:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run demo/app.py
```

Open `http://localhost:8501`. The Streamlit dashboard replays recorded experiments and supports an offline fallback dataset; **a live LLM and retraining are not required for replay**. See [demo documentation](demo/README.md) and [setup](docs/SETUP.md). Running new LLM experiments separately requires local Ollama and `llama3.2:3b`.

## Repository map

| Location | Purpose |
|---|---|
| [`docs/FINAL_RESULTS_AND_CONCLUSIONS.md`](docs/FINAL_RESULTS_AND_CONCLUSIONS.md) | Authoritative final research synthesis |
| [`docs/PROJECT_SCOPE.md`](docs/PROJECT_SCOPE.md) | Approved scope and research questions |
| [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) | Historical development plan and milestones |
| [`docs/SETUP.md`](docs/SETUP.md) | Setup and environment |
| [`docs/datasets/`](docs/datasets/) | Data generation, EDA, splitting, preprocessing |
| [`docs/models/`](docs/models/) | Detection, comparison, explanation methods |
| [`docs/mitre/`](docs/mitre/) | Evidence-grounded ATT&CK mapping |
| [`experiments/prompt_injection/`](experiments/prompt_injection/) | Frozen protocols, manifest, experimental evaluations |
| [`src/`](src/) | Implementation |
| [`results/`](results/) | Recorded evaluation evidence |
| [`demo/`](demo/) | Offline Streamlit replay dashboard |

The `docs/PROJECT_PLAN.md` file is retained as a **historical record**: earlier milestones and future-tense statements there do not override the completed results. Experimental JSON identifiers and manifest filenames retain their original names to preserve provenance and compatibility.

## Research limitations

Only synthetic data and **three underlying LLM incidents** were evaluated. Repeated runs are correlated. Explanations are diagnostic rather than causal, MITRE mappings are deliberately cautious, and the study does not establish production robustness or statistically significant defense efficacy. Human review remains essential.

## Submission materials

The academic Project Summary Form, Poster, Presentation and Final Report are submitted separately to the lecturer; they are **not included in this source repository**.
