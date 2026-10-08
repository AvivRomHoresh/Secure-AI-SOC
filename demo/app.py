
import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "experiments/prompt_injection/PHASE11_EXPERIMENT_MANIFEST.json"

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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Telemetry",
    "Detection & XAI",
    "MITRE",
    "AI Analyst",
    "Security & RAI",
    "Experiment Comparison",
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

st.divider()
st.caption(
    "Replay of frozen experiment records. "
    "No models are retrained, no thresholds are changed, "
    "and no experiment logs are modified."
)
