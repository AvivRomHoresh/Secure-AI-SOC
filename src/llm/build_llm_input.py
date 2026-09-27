"""Phase 6: deterministic, read-only assembly of a single local-LLM input.

Run from the repository root: python src/llm/build_llm_input.py --event-id 3505
No model calls, file writes, or ground-truth labels occur here.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_RAW = {
    "user": str, "country": str, "device": str, "protocol": str,
    "hour": int, "failed_attempts": int, "distance_km": (int, float),
    "session_minutes": (int, float), "bytes_out_mb": (int, float),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_object(path):
    with path.open("r", encoding="utf-8") as stream:
        obj = json.load(stream)
    require(type(obj) is dict, f"Expected JSON object: {path}")
    return obj


def assemble(event_id, root=ROOT):
    """Assemble from versioned research artifacts; does not attest file authenticity."""
    require(type(event_id) is int and event_id >= 0, "event_id must be a nonnegative integer")
    evidence = read_object(root / "results/explainability/evidence" / f"event_{event_id}_evidence.json")
    mapping = read_object(root / "results/mitre" / f"event_{event_id}_mitre.json")

    for name, obj in (("evidence", evidence), ("mapping", mapping)):
        require(obj.get("schema_version") == "1.0", f"Unsupported {name} schema_version")
        require(type(obj.get("event_id")) is int and obj["event_id"] == event_id,
                f"{name} event_id mismatch")

    raw = evidence.get("raw_evidence")
    require(type(raw) is dict and set(raw) == set(REQUIRED_RAW), "Invalid raw_evidence fields")
    for key, allowed in REQUIRED_RAW.items():
        value = raw[key]
        require(type(value) in (allowed if isinstance(allowed, tuple) else (allowed,)),
                f"Invalid raw_evidence.{key} type")
    require(0 <= raw["hour"] <= 23 and raw["failed_attempts"] >= 0,
            "Invalid raw_evidence hour or failed_attempts")
    for key in ("distance_km", "session_minutes", "bytes_out_mb"):
        require(0 <= raw[key] < float("inf"), f"Invalid raw_evidence.{key}")

    detection = evidence.get("detection")
    require(type(detection) is dict and type(detection.get("models_agree")) is bool,
            "Invalid detection structure")
    for name, score_key in (("isolation_forest", "anomaly_score"),
                            ("autoencoder", "reconstruction_mse")):
        model = detection.get(name)
        require(type(model) is dict, f"Missing detection.{name}")
        require(model.get("prediction") in ("normal", "anomaly"), f"Invalid {name} prediction")
        for key in (score_key, "validation_selected_threshold"):
            value = model.get(key)
            require(type(value) in (int, float) and -float("inf") < value < float("inf"),
                    f"Invalid {name}.{key}")
    require(detection["models_agree"] ==
            (detection["isolation_forest"]["prediction"] ==
             detection["autoencoder"]["prediction"]), "Inconsistent models_agree")

    explanations = evidence.get("explanations")
    require(type(explanations) is dict and
            all(type(explanations.get(k)) is dict for k in ("autoencoder", "isolation_forest")),
            "Missing explanations")
    require(mapping.get("mapping_status") in ("insufficient_evidence", "no_mapping"),
            "Unsupported MITRE mapping_status")
    candidates = mapping.get("candidate_techniques")
    require(type(candidates) is list, "Invalid candidate_techniques")
    if mapping["mapping_status"] == "no_mapping":
        require(not candidates, "no_mapping must not include candidate techniques")
    for item in candidates:
        require(type(item) is dict and item.get("assessment") == "possible_indicator_not_confirmed"
                and item.get("technique_id") == "T1110" and item.get("tactic_id") == "TA0006",
                "Unexpected or unconfirmed MITRE candidate")
    require(mapping.get("llm_generated") is False, "Mapping must be deterministic")

    # Explicit allowlist: excludes provenance placeholders, is_attack, and other labels.
    return {
        "schema_version": "1.0", "event_id": event_id,
        "trusted": {
            "raw_evidence": raw,
            "detection": detection,
            "explanations": explanations,
            "mitre_mapping": mapping,
        },
        "untrusted_context": None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-id", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(assemble(args.event_id), ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
