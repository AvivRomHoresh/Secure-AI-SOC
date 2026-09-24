# Phase 5 — MITRE ATT&CK Mapping Validation

## Scope and design

The current deterministic mapper (`src/mitre/map_evidence.py`, rule `mitre-t1110-screen-v0.1`) evaluates the original `failed_attempts` telemetry field. A count of **5 or more** creates a **possible** MITRE ATT&CK T1110 (Brute Force), tactic TA0006 (Credential Access), candidate. The result remains `insufficient_evidence` because the synthetic telemetry does not establish an observation window or independently verified sequence of authentication attempts. Counts below 5 produce `no_mapping`, **not** a conclusion that the event is benign. The threshold is exploratory and synthetic-data-specific; it is not a production detection threshold.

The mapper operates on structured operational evidence independently of LLM output, detector predictions, and held-out ground-truth labels. Other observed fields remain explicitly unmapped because this telemetry does not establish additional ATT&CK techniques.

## Verified example outputs

| Event ID | Recorded failed attempts | Mapping status | Candidate | Interpretation |
|---|---:|---|---|---|
| 3216 | Below 5 | `no_mapping` | None | No supported mapping under this exploratory rule; benignness is not established. |
| 2624 | 9 | `insufficient_evidence` | T1110 / TA0006 | Possible indicator only; supporting authentication sequence and time window missing. |
| 3505 | 13 | `insufficient_evidence` | T1110 / TA0006 | Possible indicator only; supporting authentication sequence and time window missing. |

Saved outputs:

- `results/mitre/event_3216_mitre.json`
- `results/mitre/event_2624_mitre.json`
- `results/mitre/event_3505_mitre.json`

## Automated validation

Command:

```cmd
python -m unittest discover -s tests -p "test_mitre_mapping.py" -v
```

Observed result: **4 tests passed**:

1. `test_detection_scores_and_ground_truth_do_not_drive_mapping`
2. `test_deterministic_and_does_not_mutate_input`
3. `test_invalid_inputs_rejected`
4. `test_threshold_boundary_and_missing_evidence`

These tests establish the checked behaviors of this limited mapper, **not** comprehensive ATT&CK coverage or real-world accuracy.

## Evidence gaps and limitations

- No defined observation/aggregation window for `failed_attempts`.
- No timestamped authentication-attempt sequence or independent source authentication logs.
- No validated source identifier or confirmed adversarial intent.
- A high anomaly score alone cannot establish an ATT&CK technique.
- The threshold of five follows the intentionally separable synthetic dataset; do not interpret this as a validated production rule.
- Only a cautious T1110 screening candidate is currently supported. No sub-technique is asserted.

## Reproduction

From the repository root:

```cmd
python src\mitre\map_evidence.py --event-id 3216
python src\mitre\map_evidence.py --event-id 2624
python src\mitre\map_evidence.py --event-id 3505
python -m unittest discover -s tests -p "test_mitre_mapping.py" -v
```

Keep the mapping result distinct from the original security evidence, XAI diagnostics, future LLM recommendations, and the eventual human analyst decision.
