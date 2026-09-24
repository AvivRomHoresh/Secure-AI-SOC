"""Unit tests for the conservative Phase 5 ATT&CK evidence mapper.

Run from the project root:
    python -m unittest discover -s tests -p "test_mitre_mapping.py" -v
"""
import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mitre_map_evidence", ROOT / "src" / "mitre" / "map_evidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def evidence(count):
    return {
        "schema_version": "1.0",
        "event_id": 42,
        "raw_evidence": {"failed_attempts": count, "country": "IL"},
        "detection": {"autoencoder": {"prediction": "anomaly"}},
    }


class MitreMappingTests(unittest.TestCase):
    def test_threshold_boundary_and_missing_evidence(self):
        for count in (0, 4):
            with self.subTest(count=count):
                result = MODULE.map_evidence(evidence(count))
                self.assertEqual(result["mapping_status"], "no_mapping")
                self.assertEqual(result["candidate_techniques"], [])
        for count in (5, 17):
            with self.subTest(count=count):
                result = MODULE.map_evidence(evidence(count))
                self.assertEqual(result["mapping_status"], "insufficient_evidence")
                self.assertEqual(len(result["candidate_techniques"]), 1)
                candidate = result["candidate_techniques"][0]
                self.assertEqual(candidate["technique_id"], "T1110")
                self.assertEqual(candidate["tactic_id"], "TA0006")
                self.assertEqual(candidate["assessment"], "possible_indicator_not_confirmed")
                self.assertEqual(candidate["observed_fields"], {"failed_attempts": count})
                self.assertTrue(candidate["missing_evidence"])

    def test_invalid_inputs_rejected(self):
        invalid = [
            None,
            {},
            {**evidence(5), "schema_version": "2.0"},
            {**evidence(5), "event_id": -1},
            {**evidence(5), "event_id": True},
            {**evidence(5), "raw_evidence": None},
        ]
        for count in (-1, 5.0, True, "5", None):
            invalid.append(evidence(count))
        for item in invalid:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    MODULE.map_evidence(item)

    def test_detection_scores_and_ground_truth_do_not_drive_mapping(self):
        original = evidence(5)
        alternate = copy.deepcopy(original)
        alternate["detection"] = {"autoencoder": {"prediction": "normal"}}
        alternate["is_attack"] = 0
        alternate["raw_evidence"]["country"] = "SG"
        self.assertEqual(MODULE.map_evidence(original), MODULE.map_evidence(alternate))

    def test_deterministic_and_does_not_mutate_input(self):
        item = evidence(9)
        snapshot = copy.deepcopy(item)
        self.assertEqual(MODULE.map_evidence(item), MODULE.map_evidence(item))
        self.assertEqual(item, snapshot)
        result = MODULE.map_evidence(item)
        self.assertFalse(result["llm_generated"])
        self.assertEqual(result["screening_threshold_scope"], "exploratory_synthetic_only")
        self.assertNotIn("is_attack", str(result))


if __name__ == "__main__":
    unittest.main()
