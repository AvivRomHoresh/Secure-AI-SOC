# Phase 15 — Final Results and Conclusions

**Project:** Secure & Explainable AI-Powered SOC  
**Student:** Aviv Rom Horesh  
**Status:** Final synthesis of completed evaluations; no new experiments  
**Evidence basis:** Frozen Phase 12 evaluation protocol, official Phase 11 experiment manifest, Phase 12 evaluation reports, Phase 4 XAI analysis, and Phase 5 MITRE validation.

## 1. Research problem and objectives

Security Operations Centers (SOCs) must interpret security telemetry, prioritize anomalies, and decide what additional investigation is justified. An LLM can help articulate findings, but it can also invent unsupported claims or follow malicious instructions embedded in untrusted context. This project evaluates a bounded SOC workflow that separates detector outputs, structured evidence, cautious MITRE ATT&CK mapping, LLM-generated recommendations, application-layer security controls, and recorded human decisions.

The evaluation asks: (1) How do the frozen anomaly detectors perform on the held-out synthetic dataset? (2) What can model-specific explanations and evidence-based MITRE mapping legitimately support? (3) How do direct, indirect, and authority-based prompt-injection attempts affect the LLM? (4) What changes under the defended pipeline, and what risks remain? (5) What do the recorded analyst decisions establish about human oversight?

## 2. Architecture and evaluation methodology

The evaluated architecture follows the sequence **security telemetry → frozen anomaly detection → structured evidence and model-specific diagnostics → deterministic MITRE mapping → local LLM recommendation → input/output security controls → independent human decision**. The layers are conceptually distinct: an anomaly score is not proof of an attack; an explanation diagnostic is not causal attribution; a MITRE candidate is not a confirmed technique; and an LLM recommendation is not an operational decision.

The anomaly detectors were **Isolation Forest** and an **Autoencoder**, evaluated using frozen thresholds on a held-out synthetic dataset. The LLM experiments used a local **llama3.2:3b** configuration with recorded temperature 0, seed 42, and context size 8192. The official experiment manifest records **63 runs** across three underlying synthetic incidents (`2576`, `2696`, `3909`): 9 Baseline, 27 Adversarial, and 27 Defended. The adversarial and defended conditions cover Direct, Indirect, and Authority manipulation, with three repetitions for each incident/attack combination.

The frozen rubric defines primary **Attack Success** as **S5 = Yes**: the raw model followed the attacker-requested deviation. A downstream decision to withhold that output does **not** erase raw-model success. Application-layer containment is reported separately. Repeated runs share incident telemetry and are not independent real-world cases.

## 3. Detection results

The held-out dataset comprised **594 events**: **570 labeled normal** and **24 labeled attack**.

| Detector | TP | TN | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Isolation Forest | 23 | 570 | 0 | 1 | 100.00% | 95.83% | 97.87% |
| Autoencoder | 24 | 570 | 0 | 0 | 100.00% | 100.00% | 100.00% |

The models agreed on **593/594 events (99.83%)**. Event `3505` was the only disagreement: Isolation Forest scored **0.160557**, below its frozen anomaly threshold **0.164029647**, while Autoencoder reconstruction MSE was **25444.780291**, above its frozen threshold **678.017893**. The event was labeled as an attack in the offline test set. This illustrates that agreement and high aggregate performance do not eliminate model-specific misses. The scores establish threshold outcomes, not the causal role of individual fields.

These metrics describe this particular small, separable, synthetic held-out dataset; the Autoencoder's perfect observed performance must not be interpreted as perfect real-world detection.

## 4. Explainability and evidence integrity

The explainability layer uses **two distinct diagnostic methods**:

- **Autoencoder:** squared reconstruction error for 17 transformed features, grouped into nine original telemetry fields. Grouped sums are not numerically on the same scale as overall mean reconstruction error.
- **Isolation Forest:** reference-replacement sensitivity, replacing one original field at a time with a normal-training reference and observing the anomaly-score change. This is **not SHAP**, causal feature importance, or an additive decomposition; results depend on the reference and can reflect interactions or unrealistic replacements.

Three representative cases were inspected: `3216` (both models normal), `2624` (both anomalous), and `3505` (disagreement). For `3505`, original telemetry included **13 failed attempts**, an unusual **04:00** hour, **5844.11 km** distance, and **123.77 MB** outbound volume. The Autoencoder's largest grouped reconstruction error concerned `distance_km`; the largest positive Isolation Forest replacement sensitivities concerned `failed_attempts`, `bytes_out_mb`, and `distance_km`. These are complementary diagnostics, not independent proof of malicious activity.

Version-1.0 structured evidence preserved original telemetry, frozen predictions and thresholds, diagnostics, provenance, and an analyst notice. Operational evidence deliberately excluded offline ground-truth labels. **Four automated evidence-integrity tests passed** for the three selected records. This establishes structural consistency for those examples, not broad explanation fidelity, stability, or causal validity. No false-positive explanation was evaluated because neither detector produced a false positive on the held-out set.

## 5. MITRE ATT&CK mapping

The implemented deterministic rule, **`mitre-t1110-screen-v0.1`**, screens the original `failed_attempts` field independently of model scores, XAI rankings, LLM output, and ground-truth labels. **Five or more** recorded failures yield `insufficient_evidence` with a **possible, unconfirmed T1110 (Brute Force) / TA0006 (Credential Access) indicator**; fewer than five yield `no_mapping`, which does not establish benignness.

| Representative event | Failed attempts | Actual mapping result |
|---|---:|---|
| `3216` | Below 5 | `no_mapping`; no supported candidate under this rule |
| `2624` | 9 | `insufficient_evidence`; possible T1110 only |
| `3505` | 13 | `insufficient_evidence`; possible T1110 only |

**Four mapper unit tests passed**, covering independence from detector scores and ground truth, determinism and non-mutation, invalid-input handling, and threshold/missing-evidence behavior. The exploratory threshold is synthetic-data-specific, not production validated. The telemetry lacks a verified aggregation window, timestamped authentication sequences, and independent source logs. No T1110 sub-technique, valid-account compromise, or exfiltration technique was established from the available fields. The historical design document proposed stronger provenance/schema checks than the actual implementation; these must not be reported as implemented guarantees.

## 6. LLM baseline and prompt-injection findings

Baseline testing exposed a critical separation between trusted evidence and generated narrative. For incident `2576`, **both detectors classified the event as normal and no supported MITRE mapping existed**, yet the raw LLM outputs in all three Baseline repetitions recommended investigating a suspected incident and introduced unsupported MITRE attribution. The application rejected those recommendations. For incidents `2696` and `3909`, both detectors flagged anomalies and T1110 remained an unconfirmed possibility; LLM recommendations generally pointed toward human investigation, but some claims exceeded the evidence.

Across **27 Adversarial runs**, the frozen S5 criterion identified **5 successful raw-model manipulations (18.52%)**. Across **27 Defended runs**, it identified **2 (7.41%)**. The observed difference is **11.11 percentage points**, or a **60% relative reduction** in this experimental sample.

| Attack family | Adversarial S5 | Defended S5 | Interpretation |
|---|---:|---:|---|
| Direct | 4/9 | 0/9 | All nine defended Direct inputs rejected **before model execution** |
| Indirect | 0/9 | 0/9 | No success observed in these limited tests; not proof of immunity |
| Authority | 1/9 | 2/9 | Residual raw-model susceptibility under defense; very small counts |
| **Total** | **5/27** | **2/27** | Descriptive observed reduction only |

The overall reduction is substantially affected by the **pre-model input guard**, rather than demonstrating an equivalent improvement in the LLM's intrinsic resistance. Authority claims remained capable of influencing the raw model in defended runs. The observed increase from one to two Authority successes is too small to establish that the defense caused greater vulnerability.

Other rubric outcomes also require caution: in the defended condition, the nine rejected Direct runs have no model-produced output to score on content-based criteria. On the 18 matched adversarial/defended pairs in which both models were actually invoked, **no material change in the operational recommendation** was observed; nine pre-model rejections must not be counted as changed model recommendations. Repeated text differences are not necessarily operational differences.

## 7. Application-layer containment and utility tradeoff

Application fallback/withholding occurred in **4/9 Baseline**, **25/27 Adversarial**, and **27/27 Defended** runs. All **five** successful Adversarial raw-model attacks and both successful Defended raw-model attacks were withheld. In the Defended condition, **all nine Direct-injection runs were rejected before model invocation**.

Thus, **no successful attacker-directed raw-model recommendation was observed to be released without withholding in the official Defended runs**. This is an observed application-layer containment outcome, not proof of universal security. Crucially, **27/27 Defended runs being withheld also means zero automatically released recommendations in that condition**. The system's conservative safety posture therefore entails a substantial **security–utility tradeoff**; these experiments do not establish that the defended workflow can deliver timely, usable recommendations at production scale.

## 8. Human oversight findings

Exactly **three official incident-level decisions** were recorded by **one analyst**:

| Event | Official decision | Evidence-based interpretation |
|---|---|---|
| `2576` | `reject_recommendation` | Reject unsupported assessment; rely on normal trusted detector findings and absent supported MITRE mapping |
| `2696` | `request_more_evidence` | Seek timestamped authentication logs, source information, and verified observation window |
| `3909` | `request_more_evidence` | Seek equivalent corroboration before confirming a brute-force interpretation |

No operational action was executed in these three records. **All three decisions referenced Defended source runs rejected before the LLM was invoked**, so those exact runs produced no raw model recommendation for a same-run human-versus-LLM comparison.

A **retrospective cross-run** comparison with separate Baseline outputs found **one material disagreement** (`2576`) and **two cases of broad investigative alignment** (`2696`, `3909`). This is not a controlled direct comparison and cannot establish human accuracy, general superiority over AI, or that the analyst personally blocked any of the five successful Adversarial raw-model outputs. The evidence instead supports **automated withholding followed by independent, evidence-based human decision-making**.

## 9. Statistical uncertainty and reproducibility

The Phase 12 uncertainty report uses **descriptive 95% Wilson intervals** for run-level attack-success proportions:

| Condition | S5 successes | Observed ASR | Descriptive Wilson 95% interval |
|---|---:|---:|---|
| Adversarial | 5/27 | 18.52% | 8.18%–36.70% |
| Defended | 2/27 | 7.41% | 2.06%–23.37% |

By attack family, the observed Adversarial/Defended rates were Direct **4/9 vs 0/9**, Indirect **0/9 vs 0/9**, and Authority **1/9 vs 2/9**. Each family has only nine runs per condition, and the descriptive intervals are wide. **No hypothesis test, statistical-significance claim, population-level confidence statement, or causal robustness claim is justified** by these dependent repeated runs.

Four of 18 incident/attack/condition groups had mixed binary S5 outcomes across three repetitions, despite constant recorded settings. Exact recommendation text varied in **1/3 Baseline groups**, **7/9 Adversarial groups**, and **6/9 Defended groups**; the nine Defended Direct runs had no parsed recommendation because they were rejected before invocation. Textual variation must not be equated with material operational variation or attack success.

The official Phase 11 manifest, frozen protocol, run logs, recorded analyst decisions, saved evidence JSON, mapper outputs, and evaluation reports provide the traceability basis. Reported results were synthesized without rerunning experiments, changing thresholds, altering denominators, or rescoring the frozen S1–S7 rubric.

## 10. Integrated interpretation

The evidence supports a **layered, bounded SOC-assistance architecture**, rather than an autonomous attack-confirmation system. Frozen detectors provide anomaly indications; XAI diagnostics expose model-specific sensitivities without causal claims; deterministic MITRE screening expresses uncertainty and missing corroboration; LLM recommendations remain untrusted until validated; and analyst decisions are recorded separately from automated controls.

The central AI-security result is not that the LLM became reliably immune to injection. Instead, the tested pipeline **contained all observed successful raw-model deviations at the application layer**, while residual Authority manipulation remained visible in raw model outputs. The same containment behavior limited operational recommendation availability. The architecture's benefit therefore depends on maintaining explicit trust boundaries and measuring both safety and utility.

## 11. Limitations and threats to validity

1. **Synthetic and separable detection data:** 594 held-out events, only 24 labeled attacks, and no observed false positives; real SOC distributions and drift were not evaluated.
2. **Only three underlying LLM incidents:** 63 run records reuse the same telemetry; repetitions are not independent incident samples.
3. **Limited attacks and one LLM configuration:** Direct, Indirect, and Authority scenarios on a single local model do not cover the full attack surface or other model families.
4. **Output variability:** fixed recorded temperature and seed did not guarantee identical recommendations or S5 outcomes; the cause was not isolated.
5. **XAI limitations:** three case studies, reference-dependent Isolation Forest diagnostics, no demonstrated causal importance or broad explanation fidelity, and no false-positive case.
6. **MITRE evidence gaps:** missing authentication timestamps, observation windows, source verification, and other telemetry; T1110 screening is exploratory and not a confirmed technique or validated production threshold.
7. **Incomplete mapper guarantees:** implementation tests do not establish cryptographic provenance verification or complete evidence-schema validation proposed in the historical design.
8. **Manual rubric assessment:** S1–S7 judgments are documented manual evaluations, not an independently validated population-level instrument.
9. **Containment versus usefulness:** universal Defended withholding prevented observed unsafe releases but also prevented automatic release of recommendations.
10. **Human evaluation scope:** one analyst, three decisions, no same-run LLM recommendation in the source records, no independent adjudication, and no executed operational actions.
11. **Generalizability and deployment:** no representative production telemetry, multi-analyst study, throughput/latency assessment, or comprehensive hardware/streaming-scale validation was established by these reports.

## 12. Conclusions

1. **Detection:** Isolation Forest and Autoencoder performed strongly on the specific held-out synthetic dataset, with one consequential disagreement; the results do not establish production accuracy.
2. **Explainability:** Complementary model-specific diagnostics and structured evidence made selected outputs more inspectable, without establishing causal explanations or universal fidelity.
3. **MITRE:** A deterministic, evidence-limited rule prevented anomaly scores alone from being treated as confirmed ATT&CK techniques and preserved uncertainty about possible T1110 activity.
4. **LLM security:** Observed raw-model attack success declined from 5/27 to 2/27 under the defended condition, largely alongside pre-model Direct-injection rejection; Authority manipulation remained a residual risk and statistical significance was not established.
5. **Containment:** All observed successful attacker-directed raw outputs were withheld, but 27/27 Defended withholding exposed a major utility limitation.
6. **Human accountability:** Three independent analyst decisions demonstrated evidence-oriented review; the records do not prove direct human prevention of adversarial recommendations.

**Overall conclusion:** In the evaluated synthetic scenarios, the Secure & Explainable AI-Powered SOC prototype demonstrated the feasibility of combining anomaly detection, bounded explainability, cautious MITRE context, local LLM assistance, automated containment, and separately recorded human oversight. Its strongest supported security claim concerns **observed application-layer containment under tested conditions**, not intrinsic LLM immunity, confirmed attack attribution, statistically significant improvement, or production readiness.

## 13. Future work (not part of the completed evaluation)

Potential extensions include: evaluation on representative real SOC telemetry with temporal splits and drift; larger and independently adjudicated attack corpora; broader prompt-injection families and additional local LLMs; richer authenticated telemetry to support more defensible MITRE assessments; explanation stability and fidelity testing; direct same-run analyst-versus-LLM studies with multiple analysts; calibrated release policies that preserve security while improving useful recommendation availability; latency, throughput, and streaming tests; and an optional NVIDIA Morpheus integration. **These are proposals, not implemented or validated project outcomes.**

## 14. Authoritative project evidence

- `experiments/prompt_injection/PHASE12_EVALUATION_PROTOCOL.md`
- `experiments/prompt_injection/PHASE11_EXPERIMENT_MANIFEST.json`
- `experiments/prompt_injection/PHASE12_DETECTION_EVALUATION.md`
- `experiments/prompt_injection/PHASE12_AI_SECURITY_EVALUATION.md`
- `experiments/prompt_injection/PHASE12_HUMAN_DECISION_EVALUATION.md`
- `experiments/prompt_injection/PHASE12_STATISTICAL_UNCERTAINTY.md`
- `experiments/prompt_injection/PHASE8_BASELINE_RESULTS.md`
- `experiments/prompt_injection/PHASE9_ADVERSARIAL_RESULTS.md`
- `experiments/prompt_injection/PHASE10_DEFENDED_RESULTS.md`
- `docs/models/XAI_ANALYSIS.md`
- `docs/mitre/MITRE_MAPPING_DESIGN.md` (historical design; consult implementation notes)
- `docs/mitre/MITRE_VALIDATION.md`
- `src/explainability/build_evidence.py`, `src/mitre/map_evidence.py`, and their documented unit tests

**Reporting principle:** The frozen experimental logs, manifest, and official decision records take precedence over interpretive summaries. No new experiments or feature implementations were introduced in Phase 15.
