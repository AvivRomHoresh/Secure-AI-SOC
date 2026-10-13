# Secure AI SOC — Integrated SOC Lite Dashboard

## Overview

This Streamlit dashboard is an **offline replay and review interface** for the Secure & Explainable AI-Powered SOC project. It presents recorded telemetry, detector predictions, explanation diagnostics, MITRE ATT&CK screening, LLM recommendations, defense outcomes, and human decisions.

It does **not** execute live operational SOC actions or automatically retrain detectors or rerun LLM experiments.

## Run on Windows CMD

From the project root, after installing dependencies:

```cmd
.venv\Scripts\activate
python -m streamlit run demo/app.py
```

Open `http://localhost:8501`.

## Dashboard sections

1. **Telemetry** — trusted security event data.
2. **Detection & XAI** — frozen detector outputs, disagreement, supporting diagnostics.
3. **MITRE** — conservative evidence-based ATT&CK screening.
4. **AI Analyst** — recorded LLM output, validation and fallback.
5. **Security & RAI** — attack-defense controls and human-oversight rules.
6. **Experiment Comparison** — matched Baseline, Adversarial and Defended conditions.
7. **Human Decision** — official event-level decisions and a separate interactive review form.

## Experiment provenance and fallback

The official experiment contains **63 runs**: 9 Baseline, 27 Adversarial and 27 Defended, spanning **three underlying incidents**. The primary manifest is:

`experiments/prompt_injection/PHASE11_EXPERIMENT_MANIFEST.json`

Recorded run logs are under `results/llm/`. The `demo/fallback/` directory contains a copy of the manifest and recorded logs to support replay if primary files are unavailable. Run logs are checked against SHA-256 hashes recorded in the selected manifest; this does **not** independently authenticate a fallback manifest.

Interactive analyst decisions are saved under `demo/decisions/` and **must not be included in official experiment counts**. Official decisions are under `results/human_decisions/`. The form prevents acceptance of withheld recommendations; additional-evidence requests require a rationale.

## Limitations

- Replay is not a new experimental execution.
- Prompt-injection outcomes are descriptive and specific to the synthetic experiment.
- Downstream withholding does not mean the raw LLM resisted manipulation.
- The dashboard is a research and presentation tool, not a production SOC.

See the [root README](../README.md) for final findings and [setup instructions](../docs/SETUP.md).
