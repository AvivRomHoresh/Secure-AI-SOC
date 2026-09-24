# Phase 5 — Evidence-Based MITRE ATT&CK Mapping Design

**Project:** Secure & Explainable AI-Powered SOC  
**Status:** Design proposal; mapping code and tests not yet implemented.  
**ATT&CK domain:** Enterprise ATT&CK (official MITRE pages reviewed September 2026).

## 1. Objective and trust boundary

Translate **observed telemetry** into appropriately qualified ATT&CK context. An anomaly prediction, reconstruction error, or XAI feature ranking **must never independently establish an ATT&CK technique**. The mapping module is deterministic, operates before the LLM, and must support `insufficient_evidence` and `no_mapping` outcomes.

Keep three distinct concepts:

1. **Observed facts:** values directly present in `raw_evidence`.
2. **Detection context:** frozen model scores/predictions; useful for prioritization, not technique proof.
3. **Technique assessment:** an evidence-based hypothesis with explicit missing corroboration; not confirmation that an attacker used the technique.

The synthetic `is_attack` label is **not** available to operational mapping.

## 2. Available telemetry and its limits

Current version-1.0 evidence objects preserve nine fields: `user`, `country`, `device`, `protocol`, `hour`, `failed_attempts`, `distance_km`, `session_minutes`, and `bytes_out_mb`. Each object also preserves detector outputs and model-specific explanations.

**Critical limitation:** The project has no per-attempt authentication timestamps, source IP, authentication outcome sequence, known-good geographic/device baseline, account compromise confirmation, network destination, command history, or process telemetry. The meaning and aggregation window of `failed_attempts` must be established from the data generator before interpreting it as a sequence. `distance_km` alone does not prove impossible travel; `bytes_out_mb` alone does not prove exfiltration.

## 3. Candidate mappings and minimum evidence

| Observed pattern | Candidate ATT&CK mapping | Current evidence | Required corroboration | Current permitted outcome |
|---|---|---|---|---|
| Elevated `failed_attempts` for an account | T1110 — Brute Force; Credential Access | Count only; `user` and `protocol` context | Confirmed authentication failures and their aggregation window; preferably timestamped attempts tied to account/source | **Potential T1110 indicator only**, never confirmed technique |
| Repeated password guesses against one account | T1110.001 — Password Guessing | Not directly recorded | Per-attempt logs establishing repeated guesses/attempt pattern | **Insufficient evidence** for sub-technique |
| Same password tried across multiple accounts | T1110.003 — Password Spraying | Not recorded | Correlated multi-account attempts and repeated password/pattern evidence | **Insufficient evidence** |
| Unusual country, device, hour, or distance | T1078 — Valid Accounts (consideration only) | Contextual anomaly, no confirmed account misuse | Authentication outcome, account ownership/authorized activity, identity-provider logs and corroborated unauthorized account use | **No technique mapping** |
| High `bytes_out_mb` | Exfiltration technique (unspecified) | Outbound volume only | Destination, transfer content/context, process/network evidence and evidence of unauthorized transfer | **No technique mapping** |
| `protocol=VPN` or other service | Remote-access technique (unspecified) | Protocol label only | Evidence of adversarial use and relevant session details | **No technique mapping** |

**Scope decision:** Phase 5's initial implementation will support *T1110 as a qualified candidate* only when an explicit, documented failed-attempts rule is met. It will not assert T1110.001 or other sub-techniques from the current dataset. If the aggregation semantics cannot be confirmed, even the T1110 candidate must return `insufficient_evidence` until that limitation is resolved.

## 4. Proposed deterministic decision policy (not yet implemented)

1. Validate evidence schema, event ID, numeric ranges, and provenance; reject malformed inputs.
2. Read **only** `raw_evidence` for behavior assessment. Keep model scores/XAI as separately labeled context.
3. Determine whether `failed_attempts` represents actual counted authentication failures within a defined observation window. If unknown, return `insufficient_evidence` for T1110.
4. If semantics are verified, apply a **documented project-specific screening threshold** selected without inspecting held-out test labels. Above-threshold counts may yield `candidate_mapping` for T1110, explicitly marked *suspected/indicator*; below-threshold counts yield `no_mapping` (not proof of safety).
5. Never map T1110 sub-techniques, T1078, or exfiltration solely from the nine available fields.
6. Always attach exact raw field/value references, the rule version, the outcome rationale, and the additional evidence needed. The LLM may explain but cannot edit the mapping result.

**Threshold is intentionally unspecified here:** first inspect and document the generator's `failed_attempts` semantics and the project's training/validation distributions. A numerical threshold chosen after examining test labels would contaminate the held-out evaluation.

## 5. Proposed output contract

```json
{
  "schema_version": "1.0",
  "event_id": 3505,
  "mapping_status": "insufficient_evidence",
  "candidate_techniques": [
    {
      "technique_id": "T1110",
      "technique_name": "Brute Force",
      "tactic_id": "TA0006",
      "tactic_name": "Credential Access",
      "assessment": "possible_indicator_not_confirmed",
      "observed_fields": {"failed_attempts": 13, "user": "analyst01"},
      "rationale": "Elevated recorded failure count may warrant investigation, but the event lacks an independently verified attempt sequence and observation window.",
      "missing_evidence": ["authentication attempt timestamps", "source identifier", "confirmed aggregation window"]
    }
  ],
  "unmapped_observations": ["distance_km", "bytes_out_mb"],
  "rule_version": "design-only",
  "llm_generated": false
}
```

This is an **illustrative design object, not an executed mapping result**. An implemented module must define whether candidates are returned when the input fails validation, and ensure `candidate_techniques` remains empty when no evidence-backed candidate is permitted.

## 6. Representative case expectations

- **3216 — normal detector agreement:** inspect its raw evidence without using the offline label. Normal model predictions alone do not determine mapping.
- **2624 — anomalous detector agreement:** high anomaly scores alone cannot assign an ATT&CK technique. Evaluate actual raw failed-attempt evidence under the documented rule.
- **3505 — model disagreement:** `failed_attempts=13` may prompt a *qualified* T1110 review **only if** field semantics and screening rule are validated; `country=SG` and `distance_km=5844.11` do not establish T1078, and `bytes_out_mb=123.77` does not establish exfiltration.

## 7. Validation checklist for implementation

- Same raw evidence + same rule version produces identical mapping regardless of model score, XAI ranking, or LLM narrative.
- Ground truth and downstream recommendation fields are ignored by mapping.
- Malformed/missing evidence is rejected or yields a documented `insufficient_evidence` result; never a fabricated technique.
- Every candidate includes source field/value, rationale, uncertainty, and missing corroboration.
- Negative tests: high anomaly score with low/unknown failure count; high bytes alone; foreign country alone; prompt-injected strings in untrusted text; model disagreement.
- The original evidence object remains immutable; mapping is stored as a separate result and may later populate `mitre_mapping` in a *derived* record with provenance.

## 8. Official references

- MITRE ATT&CK, T1110 Brute Force: https://attack.mitre.org/techniques/T1110/
- MITRE ATT&CK, T1110.001 Password Guessing: https://attack.mitre.org/techniques/T1110/001/
- MITRE ATT&CK, T1110.003 Password Spraying: https://attack.mitre.org/techniques/T1110/003/
- MITRE ATT&CK, T1078 Valid Accounts: https://attack.mitre.org/techniques/T1078/
- MITRE ATT&CK, DET0463 Brute Force Authentication Failures: https://attack.mitre.org/detectionstrategies/DET0463/
