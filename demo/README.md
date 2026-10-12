\# Secure AI SOC — Integrated SOC Lite Dashboard



\## Overview



This Streamlit dashboard provides an interactive demonstration of the Secure \& Explainable AI-Powered SOC final project.



The dashboard replays recorded security experiments and presents detection results, explainability evidence, MITRE ATT\&CK mappings, AI analyst outputs, security validation, and human review decisions.



\## Requirements



\- Python virtual environment

\- Dependencies listed in the project-root `requirements.txt`

\- Existing Phase 11 experiment manifest and recorded run logs



\## Installation



From the project root:



```cmd

.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



\## Run the Dashboard



From the project root:



```cmd

.venv\\Scripts\\python.exe -m streamlit run demo\\app.py

```



Open http://localhost:8501 in a browser.



\## Dashboard Sections



1\. \*\*Telemetry\*\* — Recorded security event and trusted telemetry.

2\. \*\*Detection \& XAI\*\* — Isolation Forest and Autoencoder results, agreement, and explainability evidence.

3\. \*\*MITRE\*\* — Evidence-based MITRE ATT\&CK mapping.

4\. \*\*AI Analyst\*\* — Recorded LLM output, recommendation, validation status, and fallback information.

5\. \*\*Security \& RAI\*\* — Prompt-injection defenses, validation, and responsible-AI controls.

6\. \*\*Experiment Comparison\*\* — Baseline, adversarial, and defended results for matching telemetry.

7\. \*\*Human Decision\*\* — Official event-level analyst decisions and their supporting evidence.



An additional interactive human-review form supports demonstration decisions without changing official experimental results.



\## Offline Replay



The dashboard uses existing local Phase 11 experiment records rather than requiring a live LLM or retraining the detection models.



The recorded dataset contains 63 official runs:

\- 9 baseline

\- 27 adversarial

\- 27 defended



The manifest is located at:



`experiments/prompt\_injection/PHASE11\_EXPERIMENT\_MANIFEST.json`



Recorded run logs are stored under:



`results/llm/`



Offline replay requires these files to remain available locally. This is not a standalone packaged dataset.



\## Human-in-the-Loop



Official analyst decisions are read from:



`results/human\_decisions/`



The interactive demonstration form writes new decisions separately to:



`demo/decisions/`



Demo decisions must not be included in official experiment counts or evaluation metrics.



The form records the analyst ID, decision, rationale, source-run reference, SHA-256 hash, validation status, and whether an automated recommendation was withheld.



Accepting a withheld recommendation is blocked. Requests for additional evidence require an explanation of the evidence needed.



The dashboard does not execute operational SOC actions.



\## Security and Research Limitations



\- The dashboard replays previously recorded outputs; it does not independently generate new LLM responses.

\- Prompt-injection results are specific to the recorded synthetic experiments and are not generalizable performance guarantees.

\- Model fallback or recommendation withholding must not be interpreted as proof that the underlying model resisted an attack.

\- The official Phase 11 manifest, logs, and Phase 12 evaluations are not modified by interactive demo decisions.

\- SHA-256 integrity was checked during project validation; the dashboard's normal replay view should not be treated as a comprehensive automatic integrity audit.



\## Reproducibility



Use the recorded manifest, experiment IDs, source-run references, model settings, and evaluation reports to reproduce the documented comparisons.



Relevant evaluation reports are located under:



`experiments/prompt\_injection/`



The interactive dashboard is a presentation and review interface, not a replacement for the frozen experimental evaluation.



