import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "llm"
HUMAN_DECISIONS = ROOT / "results" / "human_decisions"
OUT = ROOT / "experiments" / "prompt_injection" / "PHASE11_EXPERIMENT_MANIFEST.json"


OFFICIAL_HUMAN_DECISIONS = {
    2576: "event_2576_3cd33cb8a9ac49c5a247abe238623541.json",
    2696: "event_2696_6037268c31ad4d7687fb787a69faac56.json",
    3909: "event_3909_57eaa6f5c99541e4a2464163d403fd3a.json",
}


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_human_decisions():
    decisions = {}

    for event_id, filename in OFFICIAL_HUMAN_DECISIONS.items():
        path = HUMAN_DECISIONS / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing official human decision: {path}"
            )

        data = json.loads(path.read_text(encoding="utf-8"))

        if data.get("schema_version") != "phase7-human-decision-v1":
            raise ValueError(
                f"{filename}: unexpected human decision schema"
            )

        if int(data.get("event_id")) != event_id:
            raise ValueError(
                f"{filename}: human decision event_id mismatch"
            )

        if data.get("experiment_condition") != "defended":
            raise ValueError(
                f"{filename}: human decision must reference defended condition"
            )

        source_run = ROOT / Path(
            data["source_run_log"].replace("\\", "/")
        )

        if not source_run.exists():
            raise FileNotFoundError(
                f"{filename}: missing referenced source run {source_run}"
            )

        actual_source_sha256 = file_sha256(source_run)

        if actual_source_sha256 != data.get("source_run_sha256"):
            raise ValueError(
                f"{filename}: referenced source SHA-256 mismatch"
            )

        decisions[event_id] = {
            "decision_id": data["decision_id"],
            "decision": data["decision"],
            "decision_file": str(
                path.relative_to(ROOT)
            ).replace("\\", "/"),
            "decision_file_sha256": file_sha256(path),
            "source_run_log": data["source_run_log"].replace("\\", "/"),
            "source_run_sha256": data["source_run_sha256"],
            "analyst_id": data["analyst_id"],
            "timestamp_utc": data["timestamp_utc"],
        }

    return decisions


HUMAN_DECISION_MAP = load_human_decisions()


def add_record(records, filename, condition, attack_type, repetition):
    path = RESULTS / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing run log: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if str(data.get("event_id")) != filename.split("_")[1]:
        raise ValueError(f"{filename}: event_id mismatch")

    if data.get("experiment_condition") != condition:
        raise ValueError(
            f"{filename}: expected condition={condition}, "
            f"got {data.get('experiment_condition')}"
        )

    event_id = int(data["event_id"])

    records.append({
        "experiment_id": (
            f"P11-{condition[0].upper()}-"
            f"{event_id}-{attack_type.upper()}-R{repetition}"
        ),
        "event_id": event_id,
        "condition": condition,
        "attack_type": attack_type,
        "repetition": repetition,
        "source_run_log": str(
            path.relative_to(ROOT)
        ).replace("\\", "/"),
        "source_run_sha256": file_sha256(path),
        "trusted_sha256": data.get("trusted_sha256"),
        "untrusted_context_sha256": data.get(
            "untrusted_context_sha256"
        ),
        "validation_status": data.get("validation_status"),
        "defense_decision": (
            data.get("defense") or {}
        ).get("decision"),
        "model": data.get("model"),
        "model_settings": data.get("settings"),
        "prompt_version": data.get("prompt_version"),
        "human_decision_reference": (
            HUMAN_DECISION_MAP.get(event_id)
        ),
    })


records = []

# Phase 8 - official baseline archive
with zipfile.ZipFile(ROOT / "phase8_baseline_logs.zip") as z:
    names = z.namelist()

for i, filename in enumerate(names):
    repetition = i % 3 + 1

    add_record(
        records,
        filename,
        "baseline",
        "none",
        repetition,
    )


# Phase 9 - official adversarial archive
attack_types = ["direct", "indirect", "authority"]

with zipfile.ZipFile(
    ROOT / "phase9_adversarial_official_logs.zip"
) as z:
    names = z.namelist()

for i, filename in enumerate(names):
    attack_type = attack_types[(i % 9) // 3]
    repetition = i % 3 + 1

    add_record(
        records,
        filename,
        "adversarial",
        attack_type,
        repetition,
    )


# Phase 10 - official defended matrix
phase10 = (
    ROOT
    / "experiments"
    / "prompt_injection"
    / "PHASE10_DEFENDED_RESULTS.md"
)

text = phase10.read_text(encoding="utf-8")

rows = re.findall(
    r"\|(\d+)\|(Direct|Indirect|Authority)\|(\d+)\|\s*`([^`]+)`\|",
    text,
)

if len(rows) != 27:
    raise ValueError(
        f"Expected 27 official Phase 10 rows, got {len(rows)}"
    )

for event_id, attack_type, repetition, filename in rows:
    add_record(
        records,
        filename,
        "defended",
        attack_type.lower(),
        int(repetition),
    )


if len(records) != 63:
    raise ValueError(
        f"Expected 63 official records, got {len(records)}"
    )


expected_counts = {
    "baseline": 9,
    "adversarial": 27,
    "defended": 27,
}

actual_counts = {}

for record in records:
    condition = record["condition"]
    actual_counts[condition] = (
        actual_counts.get(condition, 0) + 1
    )

if actual_counts != expected_counts:
    raise ValueError(
        f"Unexpected condition counts: {actual_counts}"
    )


experiment_ids = [
    record["experiment_id"]
    for record in records
]

if len(experiment_ids) != len(set(experiment_ids)):
    raise ValueError("Duplicate experiment_id detected")


source_logs = [
    record["source_run_log"]
    for record in records
]

if len(source_logs) != len(set(source_logs)):
    raise ValueError("Duplicate official source run detected")


manifest = {
    "schema_version": "phase11-experimental-manifest-v1",
    "description": (
        "Audit manifest for the frozen Phase 8 baseline, "
        "Phase 9 adversarial, and Phase 10 defended official runs."
    ),
    "human_decision_scope": (
        "One independent final human analyst decision per official "
        "evaluated incident. The same incident-level decision reference "
        "is linked to all official repetitions and conditions for that "
        "event; it does not represent a separate human decision for "
        "each experimental run."
    ),
    "official_run_counts": {
        "baseline": 9,
        "adversarial": 27,
        "defended": 27,
        "total": 63,
    },
    "official_human_decision_count": len(HUMAN_DECISION_MAP),
    "official_human_decisions": HUMAN_DECISION_MAP,
    "excluded_runs": [
        {
            "source_run_log": (
                "results/llm/"
                "event_2576_20261005T195321_e9745e2e.json"
            ),
            "condition": "defended",
            "attack_type": "indirect",
            "reason": (
                "Additional preserved run excluded from the "
                "predefined three-repetition denominator."
            ),
        }
    ],
    "records": records,
}


OUT.write_text(
    json.dumps(
        manifest,
        indent=2,
        ensure_ascii=False,
    ) + "\n",
    encoding="utf-8",
)


print(f"Created: {OUT}")
print(f"Official records: {len(records)}")
print(f"Counts: {actual_counts}")
print(
    "Official human decisions: "
    f"{len(HUMAN_DECISION_MAP)}"
)