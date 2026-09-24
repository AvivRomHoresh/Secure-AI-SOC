# Secure & Explainable AI-Powered SOC

**Student:** Aviv Rom Horesh  
**Course:** AI-Guided / AI-Enhanced Cybersecurity  
**Project type:** Integrated final project (Type 2)  
**Status:** Approved; initial environment setup in progress

> **Core principle:** AI assists. Humans decide.

## Overview

This project aims to develop and experimentally evaluate a lightweight, explainable AI-assisted Security Operations Center (SOC). It combines anomaly detection, supporting evidence, MITRE ATT&CK mapping, and a local LLM that provides recommendations to a human analyst.

The project also evaluates the security of its own AI reasoning layer: can adversarial context manipulate the LLM's recommendation while the underlying security telemetry remains unchanged, and can defensive controls reduce that manipulation?

## Research Question

**How effectively can a lightweight, explainable AI-assisted SOC support security analysis while remaining robust against adversarial manipulation of its AI reasoning layer?**

## Planned Architecture

```text
Security Telemetry
       |
       v
Data Preparation / Feature Engineering
       |
       v
Anomaly Detection (Isolation Forest + Autoencoder)
       |
       v
XAI / Supporting Evidence
       |
       v
MITRE ATT&CK Mapping
       |
       v
Local LLM (advisory role)
       |
       v
Analyst Recommendation
       |
       v
Human Decision
```

Model explanations and original security evidence will remain distinguishable. MITRE mappings must be supported by observable evidence; insufficient evidence is a valid outcome. The LLM does not make final security decisions.

## Experimental Design

Three controlled conditions will be compared for the **same underlying security telemetry**:

1. **Baseline:** Normal evidence-based LLM analysis.
2. **Adversarial:** The same telemetry with malicious AI-visible context (including prompt injection, indirect injection, and authority manipulation).
3. **Defended:** The same telemetry and attacks, with trust separation, evidence validation, and Responsible AI controls.

Supporting security evidence, the LLM recommendation, and the final human decision will be logged separately. Evaluation will cover detection performance and the effect of attacks and defenses using predefined measures.

## Current Status

The Git repository, initial folder structure, Python virtual environment, and initial data-science dependencies have been set up. An initial Isolation Forest smoke test passed on synthetic example values. **This is an environment check, not a project experiment or measured research result.** The dataset, full detection pipeline, LLM integration, and controlled experiments have not yet been implemented.

NVIDIA Morpheus is an optional extension, not a dependency of the core project.

## Initial Setup

See [docs/SETUP.md](docs/SETUP.md) for Windows/Python setup and dependency installation. Python 3.12.10 is the initial development version; package versions are pinned in `requirements.txt`.

## Documentation

- [Project scope](docs/PROJECT_SCOPE.md)
- [Project work plan](docs/PROJECT_PLAN.md)
- [Environment setup](docs/SETUP.md)

Official lecturer correspondence, guidelines, and templates are preserved separately under `docs/official/`.

## Reproducibility

The project will record dataset provenance, preprocessing, configuration, model and LLM versions, random seeds where applicable, attack templates, experimental settings, and evaluation results as implementation progresses. Do not treat planned components as completed functionality.
