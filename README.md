# Secure & Explainable AI-Powered SOC

**Student:** Aviv Rom Horesh  
**Course:** AI-Guided / AI-Enhanced Cybersecurity  
**Project type:** Integrated final project (Type 2)  
**Status:** Phases 1–5 implemented; Phase 6 local LLM installed, integration pending

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

Phases 1–5 are implemented: reproducible synthetic authentication telemetry (3,960 events), normal-only preprocessing, frozen Isolation Forest and Autoencoder detection, diagnostic XAI and structured evidence, and conservative deterministic MITRE ATT&CK T1110 screening. On the held-out synthetic test partition (594 events), Isolation Forest detected 23/24 labeled attacks (0 false positives); Autoencoder detected 24/24 (0 false positives); detector agreement was 593/594. These unusually strong results reflect a strongly separable synthetic dataset and do not establish real-world performance. Eight Phase 4/5 automated tests and a read-only detection reproduction check passed. Ollama 0.34.4 and `llama3.2:3b` are installed and passed a basic CLI smoke test; structured LLM integration and the baseline/adversarial/defended experiments remain unimplemented. See `docs/PROJECT_PLAN.md` for limitations and remaining work.

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
