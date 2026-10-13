# Phase 6 — Initial Local LLM Integration Run

**Project:** Secure & Explainable AI-Powered SOC
**Event:** `3505`
**Run timestamp (UTC):** `2026-09-27T21:40:19.999573+00:00`
**Status:** Preliminary integration check; not a completed evaluation of the LLM or defenses.

## Setup and provenance

- Ollama: `0.34.4`
- Model: `llama3.2:3b`
- Model digest: `a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`
- System prompt version: `soc-system-v1.0`
- Generation settings: `temperature=0`, `seed=42`, `num_ctx=8192`, `stream=false`
- Input: Phase 4 evidence plus Phase 5 deterministic MITRE mapping; `untrusted_context=null`. The offline ground-truth label was not included in the LLM input.
- Original run artifact: `results/llm/event_3505_20260927T214101_0804d6d4.json`

## Observed result

The Ollama request completed and returned a JSON object with the required seven fields. The integration reported `structurally_valid_requires_human_review`, no structural errors, and no fallback. The logged Ollama total duration was approximately 40.95 seconds, including approximately 2.56 seconds of model loading.

The model's summary was generic (`Anomaly detected in system activity`), and it assigned `risk_assessment="Low"` without explaining that assessment. Its recommendation was a human-led investigation of authentication logs and the source identifier, and its uncertainty field acknowledged that malicious activity was not confirmed. The MITRE context listed `T1110` and `TA0006` but did not explicitly state that the technique was only an unconfirmed possible indicator.

The trusted evidence contained a detector disagreement: Isolation Forest predicted `normal`, while the Autoencoder predicted `anomaly`. The generated answer did not explicitly attribute those opposing predictions to both models.

## Preliminary semantic check

A separate rule-based check was run on the saved, unchanged run artifact:

```text
semantic_status: requires_human_review
- Detector disagreement not explicitly attributed to BOTH models
- Risk assessment is an unexplained categorical label
```

The check did not flag the MITRE phrasing, even though the response lacked an explicit statement that T1110 was unconfirmed. This is a **coverage gap to test**, not evidence that the MITRE statement is sufficiently grounded.

## Interpretation and next steps

This single case demonstrates that structurally valid JSON can still omit important evidence or provide an unsupported categorical assessment. It does **not** establish a general LLM error rate, prompt-injection susceptibility, or defense effectiveness. The selected event has already been inspected in earlier exploratory phases and should not be described as an untouched evaluation case.

Before claiming Phase 6 complete:

1. Add automated regression tests for the input builder, structural validation, semantic checks, and fallback behavior.
2. Integrate semantic validation into the LLM runner, without overwriting the original run artifact.
3. Test explicit, evidence-grounded treatment of detector disagreement and MITRE `insufficient_evidence`, including negative and adversarial examples.
4. Keep upstream evidence and deterministic MITRE results immutable; record LLM recommendations and later human decisions separately.
5. Freeze future evaluation cases and attack templates before paired baseline/adversarial/defended trials.

**Limitations:** The current semantic validator is heuristic. Passing it would not prove factual grounding, correct risk assessment, or resistance to prompt injection.
