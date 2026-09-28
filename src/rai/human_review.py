"""Phase 7: human review of existing SOC LLM logs (no operational actions).

Usage from repository root:
    python src/rai/human_review.py results/llm/<run_log>.json
"""

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHOICES = {
    "1": "accept_recommendation",
    "2": "reject_recommendation",
    "3": "request_more_evidence",
}


def read_log(path):
    original = path.read_bytes()
    data = json.loads(original)
    if not isinstance(data, dict) or not isinstance(data.get("llm_input"), dict):
        raise ValueError("Not a valid SOC LLM run log")
    trusted = data["llm_input"].get("trusted")
    if not isinstance(trusted, dict) or not all(
        key in trusted for key in ("raw_evidence", "detection", "explanations", "mitre_mapping")
    ):
        raise ValueError("Run log lacks required trusted evidence")
    if not isinstance(data.get("event_id"), int) or data.get("experiment_condition") not in (
        "baseline", "adversarial", "defended"
    ):
        raise ValueError("Run log has invalid event ID or experiment condition")
    return data, hashlib.sha256(original).hexdigest()


def pretty(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


def review(path, analyst):
    data, source_hash = read_log(path)
    trusted = data["llm_input"]["trusted"]
    print("\n=== A. SUPPORTING SECURITY EVIDENCE (upstream records) ===")
    for name in ("raw_evidence", "detection", "explanations", "mitre_mapping"):
        print(f"\n{name}:\n{pretty(trusted[name])}")
    print("\n=== UNTRUSTED NARRATIVE (NOT evidence or authority) ===")
    print(data["llm_input"].get("untrusted_context") or "[none]")
    print("\n=== B. LLM OUTPUT (unverified advisory narrative) ===")
    print(pretty(data.get("parsed_output")) if data.get("parsed_output") is not None
          else str(data.get("raw_output") or "[no output]"))
    for name in ("validation_status", "semantic_validation", "defense", "output_grounding", "errors", "fallback"):
        print(f"{name}: {pretty(data.get(name))}")

    # Runner may withhold the recommendation even when parsed_output contains text.
    withheld = bool(data.get("fallback")) or data.get("validation_status") != "heuristic_checks_passed_requires_human_review"
    if data.get("parsed_output") is None:
        withheld = True
    if withheld:
        print("\nWARNING: Automated recommendation WITHHELD. Raw model text is not an approved recommendation.")
        allowed = {"2": CHOICES["2"], "3": CHOICES["3"]}
    else:
        print("\nOutput passed implemented checks; human review is still mandatory.")
        allowed = CHOICES
    print("\n=== C. INDEPENDENT HUMAN ANALYST DECISION ===")
    for key, choice in allowed.items():
        print(f"  {key}. {choice}")
    while True:
        selected = input("Decision number (or q to cancel): ").strip().lower()
        if selected == "q":
            print("Cancelled; no decision saved.")
            return None
        if selected in allowed:
            break
        print("Invalid selection; choose an available option.")
    while True:
        rationale = input("Analyst rationale (required): ").strip()
        if rationale:
            break
        print("A nonempty rationale is required.")
    requested = None
    if selected == "3":
        while True:
            requested = input("Specific additional evidence requested (required): ").strip()
            if requested:
                break
            print("Describe the missing evidence.")

    # Source log is read only. Decision record is new and exclusive-create.
    output_dir = ROOT / "results" / "human_decisions"
    output_dir.mkdir(parents=True, exist_ok=True)
    decision_id = uuid.uuid4().hex
    record = {
        "schema_version": "phase7-human-decision-v1",
        "decision_id": decision_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_id": data["event_id"],
        "analyst_id": analyst,
        "source_run_log": str(path.resolve().relative_to(ROOT)) if path.resolve().is_relative_to(ROOT) else str(path.resolve()),
        "source_run_sha256": source_hash,
        "experiment_condition": data["experiment_condition"],
        "source_validation_status": data.get("validation_status"),
        "automated_recommendation_withheld": withheld,
        "decision": allowed[selected],
        "rationale": rationale,
        "additional_evidence_requested": requested,
        "operational_action_executed": False,
    }
    destination = output_dir / f"event_{data['event_id']}_{decision_id}.json"
    with destination.open("x", encoding="utf-8") as file:
        json.dump(record, file, indent=2, ensure_ascii=False)
        file.write("\n")
    # Detect a concurrent source modification after review; do not misrepresent integrity.
    if hashlib.sha256(path.read_bytes()).hexdigest() != source_hash:
        print("WARNING: Source log changed during review; do not rely on this decision binding.", file=sys.stderr)
    print(f"Decision saved: {destination.relative_to(ROOT)}")
    print(f"Original source SHA-256: {source_hash}")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_log", type=Path, help="Existing results/llm/*.json file")
    parser.add_argument("--analyst", help="Non-sensitive analyst identifier")
    args = parser.parse_args()
    analyst = args.analyst or input("Analyst ID (non-sensitive): ").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", analyst):
        parser.error("Analyst ID must be 1-64 letters, digits, _ or -")
    try:
        review(args.run_log, analyst)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
