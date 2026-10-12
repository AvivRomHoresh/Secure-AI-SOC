
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "experiments/prompt_injection/PHASE11_EXPERIMENT_MANIFEST.json"

def save_demo_decision(record, analyst, decision, rationale, additional):
    allowed_decisions = {
        "accept_recommendation",
        "reject_recommendation",
        "request_more_evidence",
    }

    if decision not in allowed_decisions:
        raise ValueError("Invalid decision.")

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", analyst):
        raise ValueError("Invalid analyst ID.")

    if not rationale.strip():
        raise ValueError("Analyst rationale is required.")

    if decision == "request_more_evidence" and not additional.strip():
        raise ValueError("Additional evidence must be specified.")

    source_path = (ROOT / record["source_run_log"]).resolve()
    allowed_dir = (ROOT / "results/llm").resolve()

    if not source_path.is_relative_to(allowed_dir):
        raise ValueError("Source run is outside the approved directory.")

    source_bytes = source_path.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()

    if source_hash != record["source_run_sha256"]:
        raise ValueError("Source run integrity verification failed.")

    source_data = json.loads(source_bytes)

    if (
        source_data.get("event_id") != record["event_id"]
        or source_data.get("experiment_condition") != record["condition"]
    ):
        raise ValueError("Source run does not match the selected experiment.")

    withheld = (
        bool(source_data.get("fallback"))
        or source_data.get("validation_status")
        != "heuristic_checks_passed_requires_human_review"
        or source_data.get("parsed_output") is None
    )

    if withheld and decision == "accept_recommendation":
        raise ValueError("A withheld recommendation cannot be accepted.")

    decision_id = uuid.uuid4().hex

    output = {
        "schema_version": "phase13-demo-human-decision-v1",
        "decision_id": decision_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_id": record["event_id"],
        "experiment_id": record["experiment_id"],
        "analyst_id": analyst,
        "source_run_log": record["source_run_log"],
        "source_run_sha256": source_hash,
        "experiment_condition": record["condition"],
        "source_validation_status": source_data.get("validation_status"),
        "automated_recommendation_withheld": withheld,
        "decision": decision,
        "rationale": rationale.strip(),
        "additional_evidence_requested": (
            additional.strip() if decision == "request_more_evidence" else None
        ),
        "operational_action_executed": False,
    }

    destination_dir = ROOT / "demo/decisions"
    destination_dir.mkdir(parents=True, exist_ok=True)

    destination = destination_dir / f"event_{record['event_id']}_{decision_id}.json"

    if hashlib.sha256(source_path.read_bytes()).hexdigest() != source_hash:
        raise ValueError("Source run changed during review.")

    with destination.open("x", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)
        file.write("\n")

    return destination.relative_to(ROOT)

st.set_page_config(
    page_title="Secure AI SOC",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Secure & Explainable AI-Powered SOC")
st.caption("Phase 13 | Official Experiment Replay | Read-only")


@st.cache_data
def load_manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_run(record):
    relative_path = Path(record["source_run_log"])
    path = (ROOT / relative_path).resolve()

    # Only read experiment logs inside the expected directory.
    allowed_dir = (ROOT / "results/llm").resolve()
    if not path.is_relative_to(allowed_dir):
        raise ValueError("Run log path is outside the approved directory.")

    return json.loads(path.read_text(encoding="utf-8"))


try:
    manifest = load_manifest()
    records = manifest["records"]
except (OSError, ValueError, KeyError) as exc:
    st.error(f"Unable to load experiment manifest: {exc}")
    st.stop()

event_ids = sorted({record["event_id"] for record in records})

with st.sidebar:
    st.header("Experiment Selection")

    event_id = st.selectbox("Event ID", event_ids)

    event_records = [
        record for record in records
        if record["event_id"] == event_id
    ]

    conditions = ["baseline", "adversarial", "defended"]
    condition = st.selectbox(
        "Condition",
        [c for c in conditions if any(
            r["condition"] == c for r in event_records
        )],
    )

    condition_records = [
        record for record in event_records
        if record["condition"] == condition
    ]

    attack_types = sorted({
        record["attack_type"] for record in condition_records
    })
    attack_type = st.selectbox("Attack Type", attack_types)

    matching = [
        record for record in condition_records
        if record["attack_type"] == attack_type
    ]

    repetitions = sorted({
        record["repetition"] for record in matching
    })
    repetition = st.selectbox("Repetition", repetitions)

record = next(
    r for r in matching if r["repetition"] == repetition
)

try:
    run = load_run(record)
except (OSError, ValueError) as exc:
    st.error(f"Unable to load run: {exc}")
    st.stop()

llm_input = run.get("llm_input") or {}
trusted = llm_input.get("trusted") or {}

telemetry = trusted.get("raw_evidence") or {}
detection = trusted.get("detection") or {}
explanations = trusted.get("explanations") or {}
mitre = trusted.get("mitre_mapping") or {}

st.subheader("Experiment")
a, b, c = st.columns(3)
a.metric("Event ID", str(event_id))
b.metric("Condition", condition.title())
c.metric("Repetition", str(repetition))

st.caption(f"Official experiment: {record['experiment_id']}")

tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "Telemetry",
    "Detection & XAI",
    "MITRE",
    "AI Analyst",
    "Security & RAI",
    "Experiment Comparison",
    "Human Decision",
])
with tab1:
    st.subheader("Trusted Security Telemetry")
    st.json(telemetry)

    st.divider()
    st.subheader("Untrusted / Attacker-Controlled Context")

    untrusted_context = llm_input.get("untrusted_context")

    if untrusted_context:
        st.error(
            "SECURITY WARNING: The following content is attacker-controlled. "
            "It is not trusted evidence or an authorized system instruction."
        )
        if isinstance(untrusted_context, str):
            st.code(untrusted_context, language=None, wrap_lines=True)
        else:
            st.json(untrusted_context)
    else:
        st.info("No untrusted attack context is present in this run.")


with tab2:
    st.subheader("Anomaly Detection")

    left, right = st.columns(2)
    with left:
        st.markdown("**Isolation Forest**")
        st.json(detection.get("isolation_forest", {}))
    with right:
        st.markdown("**Autoencoder**")
        st.json(detection.get("autoencoder", {}))

    st.write("Models agree:", detection.get("models_agree", "Unknown"))

    st.subheader("Explainability")
    st.json(explanations)

with tab3:
    st.subheader("Evidence-Based MITRE ATT&CK Mapping")
    st.json(mitre)
    st.info(
        "This mapping comes from the trusted evidence pipeline, "
        "not from the LLM-generated narrative."
    )

with tab4:
    st.subheader("AI Analyst — Untrusted Recommendation")

    parsed = run.get("parsed_output")

    if isinstance(parsed, dict):
        st.write("**Incident Summary**")
        st.write(parsed.get("incident_summary", "Not available"))

        st.write("**Recommendation**")
        st.write(parsed.get("recommendation", "Not available"))

        st.write("**Uncertainty**")
        st.write(parsed.get("uncertainty", "Not available"))

        st.write("**LLM-Claimed MITRE Context**")
        st.json(parsed.get("mitre_context", []))

        with st.expander("Full Parsed LLM Output"):
            st.json(parsed)
    else:
        st.warning("No parsed LLM recommendation is available.")

    st.warning(
        "LLM output is not verified security evidence "
        "and must not be treated as an approved decision."
    )

with tab5:
    st.subheader("Security Controls & Responsible AI")

    st.write("**Validation Status:**", run.get("validation_status"))
    st.write("**Input Defense:**")
    st.json(run.get("defense") or {})

    st.write("**Output Grounding:**")
    st.json(run.get("output_grounding") or {})

    st.write("**Semantic Validation:**")
    st.json(run.get("semantic_validation") or {})

    fallback = run.get("fallback")
    if fallback:
        st.error("Recommendation withheld / fallback applied")
        st.write(fallback)
    else:
        st.info("No fallback recorded for this run.")

    st.caption(
        "Human decisions will be displayed separately, "
        "with their exact source-run references."
    )

with tab6:
    st.subheader("Baseline vs Adversarial vs Defended")
    st.caption(
        "Comparison uses official frozen experiment records. "
        "Raw LLM recommendations are not approved operational decisions."
    )

    if condition == "baseline":
        st.info(
            "Baseline has no attack type. Select an attack family "
            "below to compare it against adversarial and defended runs."
        )

    comparison_attack = st.selectbox(
        "Attack family for comparison",
        ["direct", "indirect", "authority"],
        index=0 if attack_type == "none"
        else ["direct", "indirect", "authority"].index(attack_type),
        key="comparison_attack",
    )

    selected_records = {}

    for comparison_condition in ["baseline", "adversarial", "defended"]:
        expected_attack = (
            "none" if comparison_condition == "baseline"
            else comparison_attack
        )

        match = next(
            (
                r for r in records
                if r["event_id"] == event_id
                and r["condition"] == comparison_condition
                and r["attack_type"] == expected_attack
                and r["repetition"] == repetition
            ),
            None,
        )

        if match is not None:
            selected_records[comparison_condition] = match

    comparison_runs = {}

    for comparison_condition, comparison_record in selected_records.items():
        try:
            comparison_runs[comparison_condition] = load_run(
                comparison_record
            )
        except (OSError, ValueError) as exc:
            st.error(
                f"Cannot load {comparison_condition} run: {exc}"
            )

    trusted_hashes = {
        selected_records[name]["trusted_sha256"]
        for name in comparison_runs
    }

    if len(comparison_runs) == 3 and len(trusted_hashes) == 1:
        st.success(
            "Trusted evidence SHA-256 matches across all three conditions."
        )
    else:
        st.error(
            "Trusted evidence consistency could not be confirmed "
            "for all three conditions."
        )

    columns = st.columns(3)

    for column, comparison_condition in zip(
        columns, ["baseline", "adversarial", "defended"]
    ):
        with column:
            st.markdown(f"### {comparison_condition.title()}")

            comparison_run = comparison_runs.get(comparison_condition)

            if comparison_run is None:
                st.warning("Official run unavailable.")
                continue

            comparison_input = comparison_run.get("llm_input") or {}
            comparison_output = comparison_run.get("parsed_output")
            comparison_defense = comparison_run.get("defense") or {}

            st.write(
                "**Validation:**",
                comparison_run.get("validation_status", "Unknown"),
            )
            st.write(
                "**Input defense:**",
                comparison_defense.get("decision", "Unknown"),
            )

            context = comparison_input.get("untrusted_context")
            st.write("**Attack context:**")

            if context:
                with st.expander("View untrusted content"):
                    if isinstance(context, str):
                        st.code(context, language=None, wrap_lines=True)
                    else:
                        st.json(context)
            else:
                st.caption("No attack context.")

            st.write("**Raw LLM recommendation:**")

            if isinstance(comparison_output, dict):
                st.write(
                    comparison_output.get(
                        "recommendation", "Not available"
                    )
                )
            else:
                st.warning(
                    "No raw recommendation. The model may not "
                    "have been called."
                )

            if comparison_run.get("fallback"):
                st.error("Recommendation withheld / fallback applied")
            else:
                st.info("No fallback recorded")

            st.caption(
                selected_records[comparison_condition]["experiment_id"]
            )

    st.caption(
        "A matching trusted hash confirms equality of the recorded "
        "trusted evidence digest, not the validity of the LLM output. "
        "Attack success must be assessed using the frozen S5 rubric."
    )
with tab7:
    st.subheader("Human-in-the-Loop — Official Analyst Decision")

    decisions = manifest.get("official_human_decisions", {})
    decision_ref = decisions.get(str(event_id))

    if not decision_ref:
        st.info("No official human decision is recorded for this event.")
    else:
        decision_path = (ROOT / decision_ref["decision_file"]).resolve()
        allowed_dir = (ROOT / "results/human_decisions").resolve()

        if not decision_path.is_relative_to(allowed_dir):
            st.error("Decision file path is outside the approved directory.")
        else:
            try:
                decision_data = json.loads(
                    decision_path.read_text(encoding="utf-8")
                )
            except (OSError, ValueError) as exc:
                st.error(f"Unable to load analyst decision: {exc}")
            else:
                st.info(
                    "This is the official event-level analyst decision. "
                    "It is linked to its original source run, not to every "
                    "experiment repetition displayed in this dashboard."
                )

                st.write("**Analyst:**", decision_data.get("analyst_id"))
                st.write("**Decision:**", decision_data.get("decision"))
                st.write("**Timestamp (UTC):**", decision_data.get("timestamp_utc"))

                st.subheader("Decision Rationale")
                st.write(decision_data.get("rationale", "Not recorded"))

                st.subheader("Source Run & Security Status")
                st.write(
                    "**Source experiment condition:**",
                    decision_data.get("experiment_condition")
                )
                st.write(
                    "**Source validation status:**",
                    decision_data.get("source_validation_status")
                )
                st.write(
                    "**Automated recommendation withheld:**",
                    decision_data.get("automated_recommendation_withheld")
                )
                st.write(
                    "**Operational action executed:**",
                    decision_data.get("operational_action_executed")
                )

                st.code(
                    decision_ref["source_run_log"],
                    language=None
                )

                st.caption(
                    "Source run SHA-256: "
                    + decision_ref["source_run_sha256"]
                )
                additional = decision_data.get("additional_evidence_requested")
                if additional:
                    st.subheader("Additional Evidence Requested")

                    if isinstance(additional, str):
                        st.write(additional)
                    else:
                        st.json(additional)

                with st.expander("Full Official Decision Record"):
                    st.json(decision_data)
st.subheader("Interactive Human Review — Demo Only")
st.info(
    "You are reviewing the currently selected experiment. "
    "Verify the run details before recording a human decision."
)

review_col1, review_col2, review_col3 = st.columns(3)

with review_col1:
    st.metric("Selected Event", str(event_id))

with review_col2:
    st.metric("Experiment Condition", condition.title())

with review_col3:
    st.metric(
        "Validation Status",
        str(run.get("validation_status", "Unknown"))
    )

st.caption(
    f"Source Experiment: {record['experiment_id']} | "
    f"Attack Type: {attack_type} | "
    f"Repetition: {repetition}"
)

recommendation_withheld = (
    bool(run.get("fallback"))
    or run.get("validation_status")
    != "heuristic_checks_passed_requires_human_review"
    or run.get("parsed_output") is None
)

if recommendation_withheld:
    st.warning(
        "The automated recommendation was withheld. "
        "Accept Recommendation is disabled for this run."
    )

decision_options = [
    "reject_recommendation",
    "request_more_evidence",
]

if not recommendation_withheld:
    decision_options.insert(0, "accept_recommendation")

with st.form("demo_human_decision_form"):
    analyst = st.text_input("Analyst ID", value="Demo_Analyst")

    selected_decision = st.selectbox(
        "Human Decision",
        decision_options
    )

    rationale = st.text_area(
        "Decision Rationale (required)"
    )

    additional = st.text_area(
        "Additional Evidence Requested "
        "(required only for request_more_evidence)"
    )

    submitted = st.form_submit_button("Save Demo Decision")

    if submitted:
        try:
            destination = save_demo_decision(
                record,
                analyst.strip(),
                selected_decision,
                rationale,
                additional
            )
        except (OSError, ValueError, KeyError) as exc:
            st.error(f"Decision was not saved: {exc}")
        else:
            st.success(f"Demo decision saved: {destination}")

st.divider()
st.caption(
    "Replay of frozen experiment records. "
    "No models are retrained, no thresholds are changed, "
    "and no experiment logs are modified."
)