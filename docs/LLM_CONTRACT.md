# Phase 6 — Local LLM Input/Output Contract (Draft v0.1)

**Project:** Secure & Explainable AI-Powered SOC
**Model selected:** `llama3.2:3b` via Ollama `0.34.4` (local observed model ID prefix: `a80c4f17acd5`).
**Status:** Design contract only; integration and validation not yet implemented.

## 1. Trust boundary

The local LLM is an **advisory** component. It must not modify original telemetry, frozen detector outputs, XAI diagnostics, or deterministic MITRE mappings, and must not record the final human decision. Ground truth (`is_attack`) is for offline evaluation only and is never included in the operational prompt. All LLM output is untrusted until validated by application code.

Input fields are labeled by provenance. The application must assemble trusted structured fields from saved evidence and mapping objects, not from free-form user-supplied narrative. A later adversarial experiment may append an explicitly labeled **untrusted_context** field, which must not overwrite any trusted field.

## 2. Input contract

The application constructs one request for a single event:

```json
{
  "schema_version": "1.0",
  "event_id": 3505,
  "trusted": {
    "raw_evidence": {},
    "detection": {},
    "explanations": {},
    "mitre_mapping": {}
  },
  "untrusted_context": null
}
```

- `raw_evidence`, `detection`, and `explanations` are copied from the Phase 4 evidence record; `mitre_mapping` is loaded separately from the Phase 5 mapping record.
- Validate both records' schema versions and matching event IDs before constructing the request. Validate required nested fields and allowed value types before implementation is considered complete.
- Do **not** pass evidence object's `mitre_mapping`, `llm_recommendation`, or `human_decision` placeholders as independent facts. Do **not** pass ground-truth labels.
- The application must retain source-file references and cryptographic hashes of the exact serialized input and raw output in its experiment log. These are future implementation requirements, not existing guarantees.

## 3. Output contract

The model should return **one JSON object** with exactly these fields:

```json
{
  "incident_summary": "Short evidence-grounded summary",
  "risk_assessment": "Qualitative assessment with uncertainty",
  "evidence_used": ["Explicit observations and detector results"],
  "mitre_context": ["Only mappings supplied by the trusted MITRE module, preserving their status"],
  "recommendation": "Advisory next step for a human analyst",
  "uncertainty": "Limitations, disagreements, and missing corroboration",
  "additional_evidence_needed": ["Specific follow-up logs or checks"]
}
```

Validation requirements: strict JSON parsing; exactly the required keys; string/list-of-string types; sensible field-length limits; no fabricated MITRE technique IDs or claims of confirmation when mapping says `insufficient_evidence` or `no_mapping`. Application-level consistency checks are required: valid JSON alone does not establish factual correctness. Invalid outputs must produce an explicit validation failure/fallback, never silently become a trusted recommendation.

## 4. Experimental safeguards

- Keep the same frozen telemetry, detector scores, XAI evidence, and MITRE result across paired baseline/adversarial/defended conditions.
- Store model name, exact local model digest (retrieve with `ollama show` if available), Ollama version, generation settings, prompt version, exact assembled prompt, raw response, parsed response, validation outcome, and run timestamp.
- Keep supporting evidence, LLM recommendation, and final human decision in **separate** records.
- The three Phase 4/5 saved cases (3216, 2624, 3505) are development illustrations, **not** an untouched independent final LLM evaluation set.
- Current synthetic telemetry is strongly separable; the MITRE failed-attempt threshold of 5 is exploratory and not production-validated. `insufficient_evidence` is not a confirmed ATT&CK technique.

## 5. Next implementation steps

1. Freeze the input/output schema and system-prompt text in versioned files.
2. Implement input validation and deterministic assembly from Phase 4 and Phase 5 artifacts.
3. Connect to the local Ollama HTTP API with explicit model/settings and a JSON response constraint.
4. Implement strict response validation, logging, fallback, and automated tests including malicious untrusted context.
