# Project Scope

## Secure & Explainable AI-Powered SOC

**Student:** Aviv Rom Horesh\
**Status:** Approved by lecturer\
**Project type:** Integrated AI-Cybersecurity final project

------------------------------------------------------------------------

## 1. Project Overview

The project will develop and evaluate a lightweight, explainable
AI-assisted Security Operations Center (SOC).

The system will use security telemetry to detect suspicious behavior
using machine-learning-based anomaly detection. It will then generate
supporting evidence and explanations, map supported behavior to MITRE
ATT&CK, and use a local Large Language Model (LLM) as an assistant that
produces a human-readable SOC recommendation.

The final security decision remains with the human analyst.

A second major part of the project is the security evaluation of the AI
component itself. The LLM reasoning layer will be treated as part of the
attack surface. The project will evaluate whether adversarial context
can manipulate the LLM recommendation while the underlying security
telemetry remains unchanged.

Defensive controls will then be introduced and evaluated using the same
telemetry and attacks.

------------------------------------------------------------------------

## 2. Central Research Question

> **How effectively can a lightweight, explainable AI-assisted SOC
> support security analysis while remaining robust against adversarial
> manipulation of its AI reasoning layer?**

------------------------------------------------------------------------

## 3. Approved Core Architecture

``` text
Security Telemetry
        ↓
Anomaly Detection
(Isolation Forest + Autoencoder)
        ↓
XAI / Evidence
        ↓
MITRE ATT&CK Mapping
        ↓
Local LLM
        ↓
Analyst Recommendation
        ↓
Human Decision
```

The initial SOC Lite architecture should remain focused.

------------------------------------------------------------------------

## 4. Anomaly Detection Scope

The approved anomaly-detection component will use:

-   **Isolation Forest**
-   **Autoencoder**

These two models are sufficient for the core anomaly-detection
component. Their outputs should be preserved separately and evaluated
using appropriate metrics. Additional models are not required merely to
increase complexity.

------------------------------------------------------------------------

## 5. Explainability and Evidence

Detection results must be accompanied by supporting evidence.

The XAI/evidence layer should help explain:

-   Why an event was considered anomalous.
-   Which features or observations contributed to detection.
-   What security evidence supports the interpretation.
-   Where uncertainty or disagreement exists.

Model explanations and original security evidence should remain
distinguishishable.

------------------------------------------------------------------------

## 6. MITRE ATT&CK Mapping

Supported observed behavior will be mapped to relevant MITRE ATT&CK
tactics, techniques, and/or sub-techniques where sufficient evidence
exists.

Mapping must be grounded in observable behavior and supporting evidence
rather than solely in an anomaly score or unsupported LLM
interpretation.

The system should permit an **insufficient evidence / no reliable
mapping** outcome.

------------------------------------------------------------------------

## 7. Local LLM Role

A local LLM will act as an AI assistant for the SOC analyst.

It may consume controlled context including:

-   Detection results
-   Supporting evidence
-   XAI output
-   MITRE ATT&CK context

and produce a structured, human-readable analyst recommendation.

The LLM is **not** the primary anomaly detector and is **not** the final
decision maker.

``` text
Security Evidence
        ↓
AI Recommendation
        ↓
Human Decision
```

------------------------------------------------------------------------

## 8. Responsible AI and Human-in-the-Loop

The project follows the principle:

> **AI assists. Humans decide.**

The final security decision remains with the human analyst.

Responsible AI controls should ensure that AI recommendations remain
advisory, supporting evidence remains visible, uncertainty is not
hidden, and the analyst can accept, reject, or question an AI
recommendation.

------------------------------------------------------------------------

## 9. AI Component as an Attack Surface

A major research component is evaluating the AI-assisted SOC itself as
an attack surface.

The key experimental rule is:

> **The underlying security telemetry remains unchanged while
> adversarial AI-visible context is introduced.**

This allows manipulation of the LLM reasoning layer to be evaluated
independently of changes in the actual security incident.

------------------------------------------------------------------------

## 10. Experimental Conditions

### Condition 1 --- Baseline

Normal evidence-based SOC analysis without intentionally introduced
adversarial context.

### Condition 2 --- Adversarial

The **same underlying telemetry** is used while adversarial context is
introduced.

Approved attack categories include:

-   Prompt injection
-   Indirect prompt injection
-   Authority manipulation

The objective is to determine whether the LLM recommendation can be
manipulated even though the security evidence has not changed.

### Condition 3 --- Defended

The same telemetry and attacks are evaluated again after defensive
controls are introduced.

The approved defensive concepts include:

-   Trust separation
-   Evidence validation
-   Responsible AI controls

------------------------------------------------------------------------

## 11. Controlled Experimental Comparison

``` text
                         SAME TELEMETRY
                               |
               +---------------+---------------+
               |               |               |
               v               v               v
           BASELINE       ADVERSARIAL       DEFENDED
               |               |               |
               v               v               v
       LLM Recommendation LLM Recommendation LLM Recommendation
               |               |               |
               +---------------+---------------+
                               |
                               v
                       Compare Results
```

Relevant controlled variables must be preserved so differences can be
attributed to adversarial context and/or defensive controls rather than
changes in the incident.

------------------------------------------------------------------------

## 12. Mandatory Logging Separation

The following must be logged separately:

### A. Supporting Evidence

Security facts and evidence supporting the analysis.

### B. LLM Recommendation

The recommendation produced by the AI reasoning layer.

### C. Final Human Analyst Decision

The final decision made by the human analyst.

``` text
Supporting Evidence ≠ LLM Recommendation ≠ Human Decision
```

This separation is required so the project can evaluate detection
performance, attack success, and whether AI recommendations remain
grounded in actual security evidence.

------------------------------------------------------------------------

## 13. Evaluation Scope

### Detection Performance

Where supported by ground truth, evaluate metrics such as:

-   Precision
-   Recall
-   F1-score
-   False Positive Rate
-   False Negative Rate
-   Model agreement/disagreement

### AI Security

Evaluate whether adversarial manipulation affects the LLM
recommendation. Candidate measurements include:

-   Attack Success Rate
-   Recommendation Change Rate
-   Evidence grounding/contradiction measures
-   Results by attack category

Exact definitions should be fixed before final experimental runs.

### Defensive Effectiveness

Compare Adversarial and Defended conditions using the same attacks and
underlying telemetry.

### Human Decision

Compare the AI recommendation with the separately logged human analyst
decision. Avoid broad claims about human performance unless the
experimental design supports them.

------------------------------------------------------------------------

## 14. Trust Model

The project will explicitly distinguish trusted and untrusted
information.

Potentially trusted controlled upstream information may include:

-   Validated original telemetry
-   Detection results
-   XAI/evidence output
-   Validated MITRE mapping

Potentially untrusted context may include:

-   Free-form external text
-   Retrieved content
-   User-provided narrative
-   Content containing instructions to the LLM
-   Unverified authority claims

The final classification will be defined during architecture and
experimental design.

------------------------------------------------------------------------

## 15. Defensive Scope

### Trust Separation

Trusted evidence and untrusted narrative/context must remain
distinguishable.

### Evidence Validation

The system should evaluate whether an AI recommendation is supported by
actual upstream security evidence.

### Responsible AI Controls

Policy and human-review controls should prevent the LLM from
independently overriding security facts or authorizing high-impact
actions.

------------------------------------------------------------------------

## 16. NVIDIA Morpheus

NVIDIA Morpheus is an **optional extension**.

It is not required for completion of the approved core project and
should only be considered after the core pipeline and
Baseline/Adversarial/Defended experiment are operational and evaluated.

------------------------------------------------------------------------

## 17. Core Project Boundary

The approved core project consists of:

``` text
Security Telemetry
        ↓
Isolation Forest + Autoencoder
        ↓
XAI / Supporting Evidence
        ↓
MITRE ATT&CK Mapping
        ↓
Local LLM
        ↓
Responsible AI Controls
        ↓
Human Decision
```

together with:

``` text
Baseline
   vs
Adversarial
   vs
Defended
```

and an evaluation of the resulting behavior.

------------------------------------------------------------------------

## 18. Known Final Deliverables

Based on the project instructions currently available, the final project
requires:

1.  **Written Report**
2.  **Short Presentation**
3.  **Demo of Results**

The repository, source code, experiment records, configuration, results,
and reproducibility documentation will be maintained as supporting
project materials.

Additional submission requirements received later from the lecturer must
be added to the project documentation.

------------------------------------------------------------------------

## 19. Source of Scope

This is a working scope summary based on:

1.  The final-project requirements provided for the course.
2.  The project proposal submitted by Aviv Rom Horesh.
3.  The lecturer's approval and implementation guidance.

Original lecturer/course materials must be preserved separately under
`docs/official/` without modification.

**This document does not replace the original official material.**

------------------------------------------------------------------------

## 20. Scope Change Rule

Significant changes to the following should be documented before
implementation:

-   Central research question
-   Core architecture
-   Detection models
-   Three experimental conditions
-   Main attack categories
-   Defensive-control strategy
-   Required deliverables

Minor implementation choices may evolve without changing the approved
project direction.

------------------------------------------------------------------------

**Current status:** Approved --- ready for architecture and
experimental-design implementation.
