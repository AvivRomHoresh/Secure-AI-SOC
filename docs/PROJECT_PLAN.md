# Final Project Work Plan

## Secure & Explainable AI-Powered SOC

**Student:** Aviv Rom Horesh\
**Course:** AI-Guided / AI-Enhanced Cybersecurity\
**Project status:** Approved by lecturer\
**Project type:** Integrated project (Type 2)\
**Core principle:** AI assists. Humans decide.

------------------------------------------------------------------------

# 1. Approved Project Scope

The project will implement and experimentally evaluate a lightweight,
explainable AI-assisted SOC.

The approved core architecture is:

``` text
Security Telemetry
        ↓
Data Preparation / Feature Engineering
        ↓
Anomaly Detection
(Isolation Forest + Autoencoder)
        ↓
XAI / Supporting Evidence
        ↓
MITRE ATT&CK Mapping
        ↓
Local LLM
        ↓
Analyst Recommendation
        ↓
Human Decision
```

The project has two connected goals:

1.  Build an AI-assisted SOC that can detect suspicious behavior and
    provide useful, explainable evidence to a human analyst.
2.  Treat the AI reasoning layer itself as an attack surface and
    evaluate whether adversarial context can manipulate the LLM
    recommendation independently of the underlying security evidence.

NVIDIA Morpheus is an **optional extension only**. The core project must
not depend on Morpheus, Kafka, Triton, or GPU availability.

------------------------------------------------------------------------

# 2. Central Research Question

> **How effectively can a lightweight, explainable AI-assisted SOC
> support security analysis while remaining robust against adversarial
> manipulation of its AI reasoning layer?**

## Supporting Research Questions

### RQ1 --- Detection

How effectively can Isolation Forest and an Autoencoder detect
suspicious behavior in the selected security telemetry?

### RQ2 --- Explainability

Can the system provide supporting evidence that clearly explains why an
event was considered anomalous?

### RQ3 --- AI Security

Can adversarial context manipulate the LLM recommendation while the
underlying security telemetry remains unchanged?

### RQ4 --- Defense

Can trust separation, evidence validation, and Responsible AI controls
reduce the effect of adversarial manipulation?

### RQ5 --- Human Decision

Does separating the AI recommendation, supporting evidence, and final
human decision preserve human decision sovereignty and allow the analyst
to identify cases in which the AI recommendation is not grounded in the
evidence?

------------------------------------------------------------------------

# 3. Experimental Principle

A central requirement of the experiment is:

> **The underlying security telemetry must remain identical when
> comparing the Baseline, Adversarial, and Defended conditions.**

This allows us to test manipulation of the AI reasoning layer
independently from changes in the actual security incident.

For the same selected incident:

``` text
                         SAME TELEMETRY
                               |
               +---------------+---------------+
               |               |               |
               v               v               v
           BASELINE       ADVERSARIAL       DEFENDED
               |               |               |
               v               v               v
          Normal LLM       Attacked LLM    Protected Flow
               |               |               |
               +---------------+---------------+
                               |
                               v
                         Compare Results
```

------------------------------------------------------------------------

## Submission clarification (lecturer email, 24 September 2026)

The lecturer confirmed the following **artifact choice**:

1. **Project Summary Form** — required.
2. **Project Poster** — required; follow the supplied template and poster guidelines. Prepare **PPTX and PDF**, as specified in the poster guidelines.
3. **Choose one:** Project Presentation **or** Final Project Report. Both may be prepared voluntarily, but both are **not** required by this clarification.

The chosen presentation/report has **no additional mandatory template**. It should professionally cover the problem and objectives, approach/methodology, implementation, results/evaluation, and conclusions.

**Summary-form format discrepancy:** the earlier lecturer email requested Word + PDF, while the supplied form says Word only. Prepare Word + PDF provisionally, and check final submission instructions before upload; do not describe the conflict as resolved.

**Demo:** retain the integrated demonstration as a project implementation/assessment goal from the original project plan; the new artifact clarification does not independently specify a separate demo-file submission format.

Preserve the lecturer's clarification email unchanged in `docs/official/lecturer_approval/` (local filename: `Andrie artification approval`, with its actual extension).

------------------------------------------------------------------------

# 4. Phase 0 --- Project Structure and Reproducibility

## Goal

Create a clean project structure before implementing the experimental
components.

## Tasks

-   [x] Create the project Git repository and push to GitHub.
-   [x] Create the top-level directory structure; create planned subdirectories as each phase begins.
-   [ ] Create a Python virtual environment (next step).
-   [ ] Create `requirements.txt`.
-   [ ] Create an initial `README.md`.
-   [ ] Record Python, library, Ollama/Llama, and operating-system
    versions.
-   [ ] Define configuration files instead of hard-coding thresholds and
    paths.
-   [ ] Define a reproducible random seed where applicable.
-   [ ] Create separate folders for raw data, processed data, models,
    experiments, results, figures, and documentation.
-   [x] Create an initial `.gitignore` (review it again when adding data, models, and secrets).

## Proposed Structure

``` text
secure-ai-soc/
│
├── README.md
├── requirements.txt
├── config/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── experimental/
│
├── src/
│   ├── preprocessing/
│   ├── detection/
│   ├── xai/
│   ├── mitre/
│   ├── llm/
│   ├── rai/
│   └── evaluation/
│
├── models/
│
├── experiments/
│   ├── baseline/
│   ├── adversarial/
│   └── defended/
│
├── results/
│   ├── metrics/
│   ├── logs/
│   └── figures/
│
├── demo/
│
└── docs/
    ├── architecture/
    ├── report/
    └── presentation/
```

## Completion Criteria

-   The repository can be cloned and the environment can be recreated.
-   Project paths and configuration are organized.
-   The project can later be reproduced without relying on undocumented
    manual steps.

------------------------------------------------------------------------

# 5. Phase 1 --- Dataset and Security Telemetry

## Goal

Select and document the telemetry used by the SOC.

The preferred initial use case is **authentication/login security
telemetry**, because it supports meaningful anomaly detection and
behavioral interpretation.

## Tasks

-   [ ] Select the final dataset.
-   [ ] Decide whether the data is real/public, synthetic, or a
    controlled combination.
-   [ ] Document the source and generation process.
-   [ ] Define the schema.
-   [ ] Define which records represent normal behavior.
-   [ ] Define ground truth for malicious/suspicious behavior where
    available.
-   [ ] Check missing values, duplicates, invalid values, and class
    distribution.
-   [ ] Perform basic exploratory data analysis.
-   [ ] Decide which fields are raw evidence and which are derived
    features.
-   [ ] Prevent label leakage into model features.
-   [ ] Define train/test or train/validation/test separation before
    model evaluation.

## Candidate Features

Examples only; the final set must be justified by the actual dataset:

-   User/account
-   Source country / network information
-   Device
-   Protocol
-   Login hour
-   Failed attempts
-   Geographic distance
-   Session duration
-   Outbound traffic
-   Privilege/account type
-   New or known device
-   Login success/failure

## Questions to Answer in the Report

1.  What telemetry was used and why?
2.  Where did the data come from?
3.  What does one record represent?
4.  What is the dataset size?
5.  What is the normal/attack distribution?
6.  Which features were selected?
7.  Why are these features relevant to the use case?
8.  How was ground truth obtained or constructed?
9.  What limitations or biases exist in the dataset?
10. How was data leakage prevented?

## Deliverables

-   Dataset description.
-   Schema/feature table.
-   Data-quality analysis.
-   Class/behavior distribution.
-   Relevant EDA figures.
-   Reproducible preprocessing input.

------------------------------------------------------------------------

# 6. Phase 2 --- Preprocessing and Feature Engineering

## Goal

Transform raw telemetry into valid model input while preserving the
original evidence for later analysis.

## Pipeline

``` text
Raw Telemetry
      ↓
Parsing
      ↓
Validation
      ↓
Cleaning
      ↓
Feature Engineering
      ↓
Encoding / Scaling
      ↓
Model Input
```

## Tasks

-   [ ] Parse raw data.
-   [ ] Handle missing/invalid values.
-   [ ] Encode categorical variables where necessary.
-   [ ] Scale numerical features where required.
-   [ ] Create justified behavioral features.
-   [ ] Preserve original event IDs so model results can always be
    traced back to raw evidence.
-   [ ] Fit preprocessing transformations only on the appropriate
    training data.
-   [ ] Save preprocessing configuration/artifacts.
-   [ ] Verify that the same transformation is used during evaluation
    and demo.

## Questions to Answer

1.  Which preprocessing operations were required?
2.  Which features were engineered?
3.  Why was each transformation necessary?
4.  Which transformations were fitted on training data?
5.  How is each processed record linked back to the original security
    event?

## Completion Criteria

A single event must be traceable through:

``` text
Raw Event → Processed Features → Model Output → XAI → MITRE → LLM → Human Decision
```

------------------------------------------------------------------------

# 7. Phase 3 --- Anomaly Detection

## Goal

Implement the approved two-model anomaly-detection layer.

## Model A --- Isolation Forest

-   [ ] Train/configure Isolation Forest.
-   [ ] Document important hyperparameters.
-   [ ] Generate anomaly scores.
-   [ ] Define the decision threshold.
-   [ ] Evaluate predictions.

## Model B --- Autoencoder

-   [ ] Define the Autoencoder architecture.
-   [ ] Train it on the appropriate training data.
-   [ ] Calculate reconstruction error.
-   [ ] Define the anomaly threshold.
-   [ ] Evaluate predictions.
-   [ ] Save the trained model and configuration.

## Model Comparison / Aggregation

For every event, preserve both outputs separately.

Example:

``` text
Event ID: 184

Isolation Forest
Prediction: Anomaly
Score: ...

Autoencoder
Prediction: Anomaly
Reconstruction Error: ...

Models Agree: Yes
```

Do not invent a "confidence" score unless its definition is
mathematically specified and justified.

## Required Metrics

At minimum, where ground truth supports them:

-   [ ] Precision
-   [ ] Recall
-   [ ] F1-score
-   [ ] False Positive Rate
-   [ ] False Negative Rate / missed attacks
-   [ ] Confusion matrix
-   [ ] Number/rate of anomalies detected
-   [ ] Model agreement/disagreement

Additional metrics may be added if justified.

## Questions to Answer

1.  How does each detector work?
2.  Why were these two models selected?
3.  How were their thresholds selected?
4.  How well did each model perform?
5.  Where do the models disagree?
6.  What types of events produce false positives/false negatives?
7.  Does using both models provide useful additional evidence?

## Deliverables

-   Trained models.
-   Evaluation scripts.
-   Metrics table.
-   Confusion matrices/plots.
-   Model-agreement analysis.
-   Saved predictions linked to event IDs.

------------------------------------------------------------------------

# 8. Phase 4 --- XAI and Supporting Evidence

## Goal

Explain the detection without pretending that one explanation method is
appropriate for every model.

## Planned Approach

### Isolation Forest

Evaluate an appropriate feature-attribution/explanation method. SHAP may
be considered if technically appropriate and validated for the
implementation.

### Autoencoder

Use per-feature reconstruction error or another suitable
reconstruction-based explanation to show which features contributed most
strongly to the anomaly.

## Tasks

-   [ ] Select and justify the XAI method for each model.
-   [ ] Produce event-level explanations.
-   [ ] Preserve actual security evidence alongside model explanations.
-   [ ] Rank or identify important anomalous features.
-   [ ] Distinguish **model explanation** from **raw security
    evidence**.
-   [ ] Create a structured evidence object that later components can
    consume.
-   [ ] Test explanations on normal, true-positive, false-positive, and
    model-disagreement cases.

## Example Structured Evidence

``` json
{
  "event_id": 184,
  "raw_evidence": {
    "failed_attempts": 18,
    "login_hour": 3,
    "new_device": true
  },
  "detection": {
    "isolation_forest": "anomaly",
    "autoencoder": "anomaly"
  },
  "explanation": {
    "important_features": [
      "failed_attempts",
      "device",
      "login_hour"
    ]
  }
}
```

## Questions to Answer

1.  Why was each XAI method selected?
2.  What exactly does the explanation mean?
3.  Does the explanation describe model behavior, security evidence, or
    both?
4.  Are the explanations understandable to a SOC analyst?
5.  What are the limitations of the chosen XAI methods?

## Deliverables

-   XAI module.
-   Structured evidence format.
-   Example explanations.
-   Figures/tables for representative incidents.

------------------------------------------------------------------------

# 9. Phase 5 --- MITRE ATT&CK Mapping

## Goal

Translate supported observed behavior into cybersecurity context.

## Important Rule

MITRE mapping must be based on **observable behavior and available
evidence**.

Do not create unsupported mappings simply because an event has a high
anomaly score.

## Tasks

-   [ ] Define which behaviors can actually be inferred from the
    selected telemetry.
-   [ ] Define mapping logic for supported behaviors.
-   [ ] Document the evidence required for every supported mapping.
-   [ ] Map behavior to tactic/technique/sub-technique only where
    justified.
-   [ ] Support an "insufficient evidence / no mapping" result.
-   [ ] Keep the mapping result separate from the LLM.
-   [ ] Store mapping rationale/evidence.

## Conceptual Flow

``` text
Raw Evidence
     ↓
Observed Behavior
     ↓
Security Interpretation
     ↓
MITRE Tactic
     ↓
Technique / Sub-technique
     ↓
Supporting Evidence
```

## Questions to Answer

1.  Which ATT&CK techniques can the telemetry support?
2.  What evidence is required for each mapping?
3.  Which behaviors cannot be mapped reliably?
4.  Is the mapping deterministic, rule-based, assisted, or hybrid?
5.  How is hallucinated/unsupported mapping prevented?

## Deliverables

-   Mapping module.
-   Mapping table.
-   Evidence requirements.
-   Representative mapped and unmapped examples.

------------------------------------------------------------------------

# 10. Phase 6 --- Local LLM as SOC Assistant

## Goal

Use a local LLM to transform structured security evidence into a
readable analyst recommendation.

The LLM is **not** the anomaly detector and is **not** the final
decision maker.

## Input to LLM

The LLM should receive a controlled structured representation
containing, where appropriate:

-   Event information.
-   Detection outputs.
-   Supporting evidence.
-   XAI output.
-   MITRE mapping.
-   Explicit trust labels/context.
-   System instructions defining its advisory role.

## Expected Output

Prefer structured output, for example:

``` json
{
  "incident_summary": "...",
  "risk_assessment": "...",
  "evidence_used": ["..."],
  "mitre_context": ["..."],
  "recommendation": "...",
  "uncertainty": "...",
  "additional_evidence_needed": ["..."]
}
```

## Tasks

-   [ ] Install/configure the selected local Llama model.
-   [ ] Define a reproducible system prompt.
-   [ ] Define the structured input schema.
-   [ ] Define the structured output schema.
-   [ ] Validate/parse LLM output.
-   [ ] Log model/version/settings used.
-   [ ] Log prompt/context used for every experimental run.
-   [ ] Prevent the LLM from silently modifying upstream evidence.
-   [ ] Create a fallback for malformed output.

## Questions to Answer

1.  Why is the LLM used?
2.  What information is it allowed to interpret?
3.  What decisions is it not allowed to make?
4.  How is its output validated?
5.  How reproducible/variable are its responses?
6.  What are the limitations of using a local LLM?

------------------------------------------------------------------------

# 11. Phase 7 --- Responsible AI and Human-in-the-Loop

## Goal

Ensure that the LLM remains an advisory component and that high-impact
security decisions remain human decisions.

## Tasks

-   [ ] Define the RAI policy.
-   [ ] Define cases requiring human review.
-   [ ] Define what the system can recommend.
-   [ ] Define what the system is forbidden to execute automatically.
-   [ ] Preserve uncertainty and conflicting model evidence.
-   [ ] Define a human-decision interface/record.
-   [ ] Log the human decision independently from the LLM
    recommendation.
-   [ ] Allow the analyst to accept, reject, or request more evidence.

## Mandatory Separation

For every evaluated incident, store independently:

``` text
A. Supporting Security Evidence
B. LLM Recommendation
C. Final Human Analyst Decision
```

This separation is explicitly required by the lecturer.

## Example

``` text
Supporting Evidence:
- 18 failed attempts
- Unknown device
- Both detectors flagged anomaly

LLM Recommendation:
Investigate the account.

Human Decision:
Escalate for investigation.

Human Rationale:
Recommendation accepted because ...
```

## Questions to Answer

1.  What is the LLM allowed to recommend?
2.  Which actions require human approval?
3.  How are uncertainty and disagreement presented?
4.  Can the human disagree with the AI?
5.  Is the human decision recorded separately?
6.  How does the design preserve decision sovereignty?

------------------------------------------------------------------------

# 12. Phase 8 --- Baseline Experimental Condition

## Goal

Establish normal evidence-based system behavior before attacks are
introduced.

## Condition 1 --- Baseline

``` text
Same Security Telemetry
        ↓
Trusted Evidence
        ↓
Normal LLM Analysis
        ↓
Recommendation
        ↓
Human Decision
```

## Tasks

-   [ ] Select a representative experimental incident set.
-   [ ] Freeze the telemetry used in the security experiment.
-   [ ] Run the normal pipeline.
-   [ ] Save all LLM inputs.
-   [ ] Save all LLM outputs.
-   [ ] Save supporting evidence separately.
-   [ ] Record final human decision separately.
-   [ ] Define what counts as an evidence-grounded recommendation.
-   [ ] Repeat LLM runs if needed to characterize response variability.

## Baseline Questions

1.  What does the LLM recommend without adversarial context?
2.  Which evidence does it cite/use?
3.  Is its recommendation consistent with the evidence?
4.  How stable is the result across repeated runs?

------------------------------------------------------------------------

# 13. Phase 9 --- Adversarial Experimental Condition

## Goal

Determine whether the AI reasoning layer can be manipulated while the
actual incident remains unchanged.

## Condition 2 --- Adversarial

**The telemetry must be identical to Baseline.**

Attack categories approved by the lecturer include:

### A. Direct Prompt Injection

Malicious instructions directly visible to the LLM.

### B. Indirect Prompt Injection

Malicious instructions embedded in content/evidence that the LLM
processes.

### C. Authority Manipulation

Claims that a manager, SOC analyst, administrator, or other authority
has already approved/cleared the activity.

## Tasks

-   [ ] Define a controlled attack set.
-   [ ] Define attack templates before running the final evaluation.
-   [ ] Keep telemetry identical across paired baseline/adversarial
    runs.
-   [ ] Log the exact adversarial context.
-   [ ] Run each attack under controlled settings.
-   [ ] Record whether the recommendation changes.
-   [ ] Record whether evidence is ignored, contradicted, or
    misrepresented.
-   [ ] Record whether the LLM follows the malicious instruction.
-   [ ] Repeat runs where necessary to account for model variability.

## Attack-Success Definition

Before collecting final results, define objectively what counts as a
successful attack.

Possible measurable outcomes include:

-   Recommendation changed in the attacker's intended direction.
-   Risk was downgraded despite unchanged evidence.
-   The model ignored or contradicted trusted evidence.
-   The model treated untrusted authority claims as stronger than
    security evidence.
-   The model recommended no investigation when the baseline/evidence
    justified investigation.

The exact final definition must be documented before the final
experiment.

## Questions to Answer

1.  Which attack types influence the LLM?
2.  How often does manipulation succeed?
3.  Does the recommendation change even though telemetry is unchanged?
4.  Which attacks cause the greatest change?
5.  Does the LLM stop grounding its answer in actual evidence?
6.  Are results stable across repeated trials?

------------------------------------------------------------------------

# 14. Phase 10 --- Defensive Controls

## Goal

Build defenses that reduce manipulation of the AI reasoning layer.

## Condition 3 --- Defended

Use the **same telemetry and the same adversarial attacks** used in
Condition 2.

## Required Defensive Concepts

### Trust Separation

Clearly distinguish trusted structured security evidence from untrusted
narrative/context.

### Evidence Validation

Check whether the LLM recommendation is supported by the actual upstream
evidence.

### Responsible AI Controls

Apply policy rules and human review rather than allowing the LLM to
override security facts.

## Proposed Flow

``` text
Telemetry
    ↓
Detection
    ↓
XAI / Evidence
    ↓
MITRE Mapping
    ↓
Trust Classification
    ↓
LLM Analysis
    ↓
Evidence Validation
    ↓
RAI Policy Gate
    ↓
Human Decision
```

## Tasks

-   [ ] Define trusted and untrusted data sources.
-   [ ] Represent trust explicitly in the input architecture.
-   [ ] Prevent untrusted narrative from overwriting trusted fields.
-   [ ] Validate that the recommendation references real evidence.
-   [ ] Detect contradictions between recommendation and upstream
    evidence where feasible.
-   [ ] Add policy constraints.
-   [ ] Force human review for defined high-impact/uncertain cases.
-   [ ] Re-run the exact adversarial experiment.
-   [ ] Compare before/after defense.

## Questions to Answer

1.  What is considered trusted?
2.  What is considered untrusted?
3.  How is trust separation enforced?
4.  How is evidence validation implemented?
5.  What can the RAI gate block or flag?
6.  How much does the defense reduce successful manipulation?
7.  What attacks still succeed?
8.  What trade-offs does the defense introduce?

------------------------------------------------------------------------

# 15. Phase 11 --- Experimental Logging

## Goal

Create an auditable experimental record.

Every experiment should receive a unique ID.

## Recommended Record

``` json
{
  "experiment_id": "...",
  "event_id": "...",
  "condition": "baseline | adversarial | defended",
  "attack_type": "none | direct | indirect | authority",
  "telemetry_hash_or_reference": "...",
  "detector_outputs": {},
  "supporting_evidence": {},
  "mitre_mapping": {},
  "trusted_context": {},
  "untrusted_context": {},
  "llm_input_reference": "...",
  "llm_recommendation": {},
  "evidence_validation": {},
  "rai_result": {},
  "human_decision": {},
  "human_rationale": "...",
  "model_version": "...",
  "run_settings": {}
}
```

## Critical Checks

-   [ ] Same paired event really uses identical telemetry.
-   [ ] Supporting evidence is not overwritten by the LLM.
-   [ ] LLM recommendation is stored independently.
-   [ ] Human decision is stored independently.
-   [ ] Attack type/condition is recorded.
-   [ ] Model and experimental settings are recorded.

------------------------------------------------------------------------

# 16. Phase 12 --- Evaluation

## A. Detection Evaluation

Compare Isolation Forest and Autoencoder using the defined detection
metrics.

Create:

-   [ ] Main performance table.
-   [ ] Confusion matrices.
-   [ ] Model agreement/disagreement table.
-   [ ] Analysis of representative false positives.
-   [ ] Analysis of representative false negatives.
-   [ ] Detection limitations.

## B. AI-Security Evaluation

Compare:

``` text
Baseline vs Adversarial vs Defended
```

Candidate metrics:

-   [ ] Attack Success Rate (ASR).
-   [ ] Recommendation Change Rate.
-   [ ] Evidence-grounding/contradiction rate, using a clearly defined
    scoring rule.
-   [ ] Correct/expected recommendation rate, only where a defensible
    reference decision exists.
-   [ ] Results by attack type.
-   [ ] Before-vs-after-defense reduction in successful attacks.

## C. Human Decision Evaluation

At minimum:

-   [ ] Compare LLM recommendation with final human decision.
-   [ ] Record analyst disagreement with AI.
-   [ ] Identify cases where human review prevented an
    unsafe/unsupported recommendation.
-   [ ] Avoid claiming general human-performance conclusions from a
    single analyst unless the experimental design supports them.

## Statistical / Experimental Discipline

-   [ ] Freeze evaluation definitions before final runs.
-   [ ] Use enough repeated trials to handle LLM variability.
-   [ ] Keep model settings consistent across compared conditions.
-   [ ] Report number of incidents and number of runs.
-   [ ] Do not selectively remove failed or inconvenient runs.
-   [ ] Report uncertainty/variance where meaningful.

------------------------------------------------------------------------

# 17. Phase 13 --- Integrated SOC Lite Demo

## Goal

Create a demonstration that shows the complete project rather than
disconnected scripts.

## Minimum Demo View

``` text
SOC Lite Incident
────────────────────────────

Event / Telemetry

Detection
- Isolation Forest
- Autoencoder
- Agreement

XAI / Evidence
- Main evidence
- Feature explanations

MITRE ATT&CK
- Supported tactic/technique
- Mapping evidence

AI Analyst
- Summary
- Recommendation
- Evidence used
- Uncertainty

RAI
- Validation status
- Human review requirement

Human Decision
- Accept
- Reject
- Request More Evidence
```

## Security Demo

Demonstrate the same incident under:

1.  Baseline.
2.  Adversarial.
3.  Defended.

The audience should be able to see that the telemetry is unchanged.

## Tasks

-   [ ] Build a lightweight UI/dashboard or clear CLI/web demo.
-   [ ] Display the event ID and condition.
-   [ ] Display evidence separately from LLM narrative.
-   [ ] Display attack context only where appropriate.
-   [ ] Display RAI/evidence-validation result.
-   [ ] Allow/record a human decision.
-   [ ] Prepare a deterministic fallback/demo dataset in case live
    components fail.

------------------------------------------------------------------------

# 18. Phase 14 --- Optional NVIDIA Morpheus Extension

This phase is **not required for the approved core project**.

Only begin it after the core experiment is complete.

Possible extension:

``` text
Telemetry
    ↓
Morpheus-style / Morpheus Pipeline
    ↓
Preprocessing
    ↓
Detection
    ↓
Postprocessing
    ↓
Existing SOC Analysis Pipeline
```

Possible goals:

-   Streaming/event-driven processing.
-   Performance comparison.
-   CPU vs accelerated processing where resources support a fair
    experiment.
-   Pipeline integration.

## Rule

Do not sacrifice the Baseline/Adversarial/Defended experiment in order
to add Morpheus.

------------------------------------------------------------------------

# 19. Phase 15 --- Final Results and Conclusions

## Results Must Answer the Research Question

The final results section should not simply state that the application
works.

It should answer:

### Detection

-   How well did each anomaly detector perform?
-   Where did it fail?
-   What value did model agreement provide?

### Explainability

-   What evidence did the system expose?
-   Were explanations useful and technically defensible?

### MITRE

-   Which behaviors could be mapped?
-   Which could not?

### LLM

-   Did the LLM produce useful evidence-based recommendations?
-   How stable were they?

### AI Attack Surface

-   Could adversarial context change recommendations?
-   Which attacks succeeded?

### Defense

-   Did the defensive architecture reduce manipulation?
-   By how much?
-   Which vulnerabilities remained?

### Human Decision

-   Did human review identify or prevent unsupported AI recommendations?
-   What does the experiment demonstrate about keeping the final
    decision outside the LLM?

## Limitations

Explicitly discuss:

-   Dataset realism and size.
-   Synthetic-data limitations if applicable.
-   Limited attack families.
-   Local LLM/model-specific behavior.
-   Stochastic LLM outputs.
-   XAI limitations.
-   MITRE mapping limitations.
-   Single-analyst limitations if only the student performs human
    decisions.
-   Generalizability.
-   Hardware/resource limitations.
-   Any experimental assumptions.

## Future Work

Possible future work:

-   NVIDIA Morpheus integration.
-   Kafka/streaming telemetry.
-   Additional detectors.
-   Additional LLMs.
-   Larger red-team attack suite.
-   RAG security experiments.
-   Multi-analyst evaluation.
-   Automated policy engines.
-   Additional telemetry sources.

------------------------------------------------------------------------

# 20. Final Written Report (Option B)

**Optional alternative to the Project Presentation:** select this report **or** the presentation as the third submission artifact. No mandatory report template was specified. If selected, use the following proposed structure, covering the lecturer-required content:

## 1. Introduction

-   Cybersecurity/SOC problem.
-   Motivation for AI assistance.
-   AI as both defensive tool and attack surface.

## 2. Problem Statement

-   Exact problem being addressed.
-   Why anomaly detection alone is insufficient.
-   Why AI reasoning security matters.

## 3. Research Question

-   Central research question.
-   Supporting questions/hypotheses if used.

## 4. Background

-   SOC.
-   Security telemetry.
-   Anomaly detection.
-   Isolation Forest.
-   Autoencoder.
-   XAI.
-   MITRE ATT&CK.
-   Local LLMs in SOC.
-   Responsible AI / Human-in-the-Loop.
-   Prompt injection / adversarial context.

## 5. System Architecture

-   Full architecture diagram.
-   Component responsibilities.
-   Trust boundaries.
-   Data flow.

## 6. Technologies

Document all technologies actually used, for example: - Python. - ML
framework/libraries. - XAI library/method. - Ollama/local Llama. -
UI/demo technology. - Docker if used. - NVIDIA Morpheus if eventually
added.

## 7. Dataset and Data Analysis

-   Dataset source.
-   Schema.
-   Ground truth.
-   EDA.
-   Preprocessing.
-   Feature engineering.
-   Limitations.

## 8. Anomaly Detection

-   IF implementation.
-   AE implementation.
-   Threshold selection.
-   Metrics.
-   Comparison.

## 9. XAI and Evidence

-   Methods.
-   Examples.
-   Interpretation.
-   Limitations.

## 10. MITRE ATT&CK Mapping

-   Mapping methodology.
-   Evidence requirements.
-   Examples.

## 11. LLM SOC Assistant

-   Input/output architecture.
-   Prompting strategy.
-   Role limitations.
-   Structured recommendation.

## 12. Responsible AI

-   Human-in-the-loop design.
-   RAI policy.
-   Decision sovereignty.
-   Logging separation.

## 13. Security Threat Model

-   What component is attacked?
-   Attacker goal.
-   Trusted/untrusted inputs.
-   Prompt injection.
-   Indirect injection.
-   Authority manipulation.

## 14. Experimental Design

-   Baseline.
-   Adversarial.
-   Defended.
-   Controlled variables.
-   Number of incidents/runs.
-   Success criteria.

## 15. Defensive Architecture

-   Trust separation.
-   Evidence validation.
-   RAI controls.
-   Human approval.

## 16. Results

-   Detection metrics.
-   Attack metrics.
-   Defense comparison.
-   Human-decision observations.
-   Tables/graphs.

## 17. Discussion

-   Interpret results.
-   Explain unexpected results.
-   Relate findings to the research question.

## 18. Limitations

-   Clearly state what the project does not prove.

## 19. Conclusions

-   Direct answer to the research question.
-   Main findings.

## 20. Future Work

-   Logical extensions.

## 21. References

-   Course material.
-   MITRE ATT&CK.
-   Documentation.
-   Academic/technical sources used.

## 22. Appendix

As appropriate: - Configuration. - Additional metrics. - Prompt
templates. - Attack templates. - Extended results. - Reproduction
instructions.

------------------------------------------------------------------------

# 21. Final Presentation (Option A)

**Optional alternative to the Final Project Report:** select this presentation **or** the report as the third submission artifact. No mandatory presentation template was specified.

Suggested structure:

1.  **Title**
2.  **Problem / Motivation**
3.  **Research Question**
4.  **Architecture**
5.  **Dataset / Telemetry**
6.  **Anomaly Detection**
7.  **XAI + MITRE**
8.  **LLM + RAI / Human-in-the-Loop**
9.  **Threat Model**
10. **Three Experimental Conditions**
11. **Baseline vs Adversarial Results**
12. **Defense Architecture**
13. **Before vs After Defense Results**
14. **Demo**
15. **Conclusions**
16. **Limitations / Future Work**

Keep the presentation focused on the experiment and findings rather than
spending most of the time explaining implementation details.

------------------------------------------------------------------------

# 22. Final Demo

The course requires a demonstration of results.

The final demo should demonstrate, at minimum:

-   [ ] Security telemetry enters the system.
-   [ ] IF and AE produce detection results.
-   [ ] Supporting evidence/XAI is displayed.
-   [ ] MITRE mapping is displayed where supported.
-   [ ] Local LLM produces an analyst recommendation.
-   [ ] Recommendation and evidence are visibly separate.
-   [ ] Human decision is recorded separately.
-   [ ] Baseline condition.
-   [ ] At least one successful/meaningful adversarial attempt or
    representative attack behavior.
-   [ ] Defended condition using the same telemetry and attack.
-   [ ] Result comparison.

Prepare screenshots/recorded results as a backup for any live-demo
dependency.

------------------------------------------------------------------------

# 23. Final Submission Package — Confirmed Artifact Rules

The lecturer's clarification confirms **two mandatory artifacts and one choice**:

- [ ] **Project Summary Form** (mandatory): complete the supplied Word template. Prepare Word and PDF provisionally because the earlier email requests both, although the template says Word only; verify the final upload format.
- [ ] **Project Poster** (mandatory): follow the supplied B1 poster template and guidelines; deliver **PPTX + PDF**.
- [ ] **One of the following** (mandatory choice):
  - [ ] **Option A — Project Presentation:** PDF + PPTX, per the earlier artifact email.
  - [ ] **Option B — Final Project Report:** PDF + Word, per the earlier artifact email.

For the chosen Option A/B, the lecturer requires a clear professional structure covering **problem and objectives, approach/methodology, implementation, results/evaluation, and conclusions**. Neither has an additional mandatory template.

The integrated SOC Lite **demo** remains a project implementation/assessment goal. The latest artifact clarification does not establish a separate demo-file upload requirement. Keep reproducibility material, source code, experimental records, figures, and demo backup organized; the precise repository/archive submission procedure remains to be confirmed.

## Proposed Working Submission Layout (not an official required folder structure)

```text
submission/
├── Summary_Form/         # Word; provisional PDF too
├── Poster/               # PPTX + PDF
├── Presentation_or_Report/  # choose one, with its required formats
├── Demo_Backup/          # if needed for assessment
└── Reproducibility/      # instructions, code/results references
```

**Decision pending:** select Presentation or Report before preparing final artifacts; do not mark both as mandatory.

------------------------------------------------------------------------

# 24. Final Quality Checklist

## Scientific / Experimental

-   [ ] Research question is explicitly answered.
-   [ ] Ground truth is documented.
-   [ ] Detection metrics are calculated correctly.
-   [ ] Threshold selection is documented.
-   [ ] Baseline/Adversarial/Defended use paired identical telemetry.
-   [ ] Attack-success criteria were defined before final analysis.
-   [ ] Experimental run count is documented.
-   [ ] LLM variability is considered.
-   [ ] No fabricated or selectively reported results.

## Security

-   [ ] Trusted and untrusted information are separated.
-   [ ] LLM cannot overwrite original evidence.
-   [ ] MITRE mappings are evidence-based.
-   [ ] LLM output is treated as a recommendation.
-   [ ] Human decision is independent.
-   [ ] Defenses are evaluated using the same attacks used against the
    undefended system.

## Reproducibility

-   [ ] Requirements documented.
-   [ ] Versions documented.
-   [ ] Random seeds/configuration documented where relevant.
-   [ ] Model thresholds documented.
-   [ ] Prompt templates saved.
-   [ ] Attack templates saved.
-   [ ] Experimental records saved.
-   [ ] Instructions to reproduce main results exist.

## Submission

-   [ ] Project Summary Form completed (verify Word/PDF upload requirement).
-   [ ] Project Poster completed in PPTX and PDF using the official template.
-   [ ] Choose either Project Presentation or Final Project Report and complete it in the specified formats.
-   [ ] Architecture diagram completed.
-   [ ] Results tables/figures completed.
-   [ ] Chosen Presentation/Report covers objectives, methodology, implementation, results/evaluation, and conclusions.
-   [ ] Demo tested.
-   [ ] Demo backup prepared.
-   [ ] README completed.
-   [ ] References checked.
-   [ ] Final conclusions match actual measured results.

------------------------------------------------------------------------

# 25. Recommended Implementation Order

Do not build all components simultaneously.

``` text
01. Repository + Environment
          ↓
02. Dataset + Ground Truth
          ↓
03. EDA + Preprocessing
          ↓
04. Isolation Forest
          ↓
05. Autoencoder
          ↓
06. Detection Evaluation
          ↓
07. XAI + Evidence Format
          ↓
08. MITRE Mapping
          ↓
09. Local Llama Integration
          ↓
10. Baseline SOC
          ↓
11. RAI + Human Decision Logging
          ↓
12. Freeze Experimental Protocol
          ↓
13. Adversarial Condition
          ↓
14. Trust Separation + Evidence Validation
          ↓
15. Defended Condition
          ↓
16. Full Experimental Evaluation
          ↓
17. Integrated Demo
          ↓
18. Summary Form + Poster
          ↓
19. Chosen Presentation OR Final Report
          ↓
20. Optional Morpheus Extension
```

**Morpheus is deliberately last.** If the core experiment is not
complete, do not start the optional extension.

------------------------------------------------------------------------

# 26. Project Milestones

## Milestone 1 --- Data Ready

Dataset, ground truth, EDA, preprocessing and feature definitions are
complete.

## Milestone 2 --- Detection Ready

Isolation Forest and Autoencoder are implemented and evaluated.

## Milestone 3 --- Explainable SOC Core

Detection + XAI/evidence + MITRE mapping work end-to-end.

## Milestone 4 --- AI-Assisted SOC

Local Llama produces structured analyst recommendations from controlled
evidence.

## Milestone 5 --- Baseline Ready

RAI/Human-in-the-Loop and separate logging of evidence, AI
recommendation and human decision are complete.

## Milestone 6 --- AI Attack Evaluation

Baseline and Adversarial conditions are complete.

## Milestone 7 --- Defense Evaluation

Defended condition and before/after comparison are complete.

## Milestone 8 --- Final System

Integrated SOC Lite demo works end-to-end.

## Milestone 9 --- Submission Ready

Mandatory Summary Form and Poster, the chosen Presentation or Report,
demo readiness, results, and reproducibility materials are finalized.

------------------------------------------------------------------------

# 27. Definition of Done

The project is complete when we can demonstrate and experimentally
support the following chain:

> **The system receives security telemetry, detects suspicious behavior
> using Isolation Forest and Autoencoder, exposes understandable
> supporting evidence, maps supported behavior to MITRE ATT&CK, uses a
> local LLM to assist the SOC analyst, keeps the final decision with the
> human, demonstrates whether adversarial context can manipulate the AI
> recommendation while telemetry remains unchanged, applies defensive
> controls, and quantitatively compares the system before and after
> those controls.**

The selected final Presentation or Report must use measured results to answer
the approved central research question rather than merely describing the
software implementation.
