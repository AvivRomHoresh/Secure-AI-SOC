# Phase 7 — Responsible AI & Human-in-the-Loop Policy

**Project:** Secure & Explainable AI-Powered SOC  
**Status:** Proposed implementation policy (review before implementation)  
**Scope:** Advisory SOC analysis and controlled Baseline / Adversarial / Defended experiments.

## 1. Purpose and authority

The local LLM is an **advisory component**, not the primary detector or the final decision-maker. A human analyst retains responsibility for the final security decision. The system must preserve three independent records for every evaluated incident:

1. **Supporting Security Evidence** — trusted telemetry, separate Isolation Forest and Autoencoder results, XAI evidence, and evidence-qualified MITRE mapping.
2. **LLM Recommendation** — original model output, its uncertainty, validation findings, defense status, and fallback, if any.
3. **Final Human Analyst Decision** — analyst's explicit choice and rationale, stored independently.

## 2. Permitted and prohibited actions

**The LLM may:** summarize supplied evidence, explain detector agreement or disagreement, discuss supported MITRE candidates with their limitations, recommend further investigation, and identify missing evidence.

**The LLM must not:** modify trusted evidence, declare an unsupported MITRE candidate confirmed, treat untrusted narratives as verified facts, approve or close an incident autonomously, or execute containment, account blocking, notifications, or other security actions.

All operational actions and final incident dispositions require explicit human authorization. This phase records decisions; it does **not** execute operational security actions.

## 3. Mandatory human review

Human review is required for **every** evaluated incident, including outputs that pass structural and heuristic checks. Review is especially important when:

- The two anomaly detectors disagree.
- Evidence is incomplete or a MITRE mapping is marked insufficient.
- Structural or semantic validation fails, or output-grounding checks raise flags.
- The input guard rejects untrusted context or the runner returns a fallback.
- The LLM's assertions are not supported by independently recorded evidence.

A successful heuristic check is not proof of factual correctness or prompt-injection resistance. An automatic fallback is not proof that a specific attack was detected.

## 4. Analyst decision options

The analyst selects exactly one of:

- `accept_recommendation` — agrees with the recorded LLM recommendation, **not** permission to execute it automatically.
- `reject_recommendation` — disagrees with the recorded recommendation.
- `request_more_evidence` — cannot reach a supported decision from the available evidence.

Every decision requires a nonempty analyst rationale. For rejection or additional-evidence requests, the rationale should identify the relevant evidence gap or disagreement. The analyst may disagree with the model even when validation checks pass.

## 5. Evidence presentation and trust boundaries

- Present trusted evidence and the two detector outputs separately from the LLM narrative.
- Preserve original uncertainty, model disagreement, missing source records, and tentative MITRE status.
- Label externally supplied narrative as **untrusted**, even if it claims prior analyst, management, or enrichment-service authority.
- Display the original model output and all validation/defense findings without rewriting them to match the human decision.
- Do not expose synthetic ground-truth labels to the LLM as part of experimental analysis.

## 6. Record design and integrity

**Implementation design:** Keep the existing `results/llm/*.json` run logs unchanged. Write each analyst decision as a **new** JSON record in a separate directory (proposed: `results/human_decisions/`). The decision record should contain:

- A unique `decision_id`, UTC timestamp, `event_id`, and non-sensitive analyst identifier.
- The exact source run-log path or run identifier **and its SHA-256 digest** to bind the decision to an immutable snapshot.
- The original experimental condition (`baseline`, `adversarial`, or `defended`) for analysis, not as a substitute for evidence.
- The selected decision option and analyst rationale.
- Optional requested-evidence description when `request_more_evidence` is selected.

Do not copy the analyst's decision into the original LLM log or overwrite an earlier decision. If a decision is revised, create a new linked record and preserve the prior record. Avoid claiming that a file hash alone prevents tampering; it enables later integrity checks against the captured source file.

## 7. Phase 7 acceptance checks

- [ ] Document the RAI policy and human-review triggers.
- [ ] Define and validate a separate human-decision JSON schema.
- [ ] Implement a minimal CLI to inspect a run and record one of the three decisions.
- [ ] Require rationale and bind each decision to a source-log digest.
- [ ] Verify that recording a decision leaves source evidence and LLM logs byte-for-byte unchanged.
- [ ] Test missing/malformed logs, invalid decision values, missing rationale, and revision behavior.
- [ ] Document how analyst disagreement and additional-evidence requests are recorded.
- [ ] Update `docs/PROJECT_PLAN.md` only after the implementation and tests are verified.

## 8. Evaluation limitations

A human-decision record demonstrates decision separation, not necessarily decision quality. Do not infer general human performance or defense effectiveness from a single analyst, incident, or small repeated-run set. Preserve matched telemetry across experimental conditions when comparing AI outputs.
