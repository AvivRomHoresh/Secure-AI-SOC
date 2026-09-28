"""Isolated Phase 7 acceptance-branch test. No real LLM run is relabeled or edited.

From repository root:
    python -m unittest discover -s tests -p test_phase7_acceptance.py -v

Place this file in tests/test_phase7_acceptance.py.
"""

import contextlib
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "rai" / "human_review.py"
spec = importlib.util.spec_from_file_location("phase7_human_review", MODULE_PATH)
human_review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(human_review)


def synthetic_run(status, fallback=None):
    """Clearly synthetic fixture, not a real passed model/security evaluation."""
    return {
        "fixture_only": True,
        "event_id": 999999,
        "experiment_condition": "baseline",
        "llm_input": {
            "trusted": {
                "raw_evidence": {"failed_attempts": 1},
                "detection": {
                    "isolation_forest": {"prediction": "normal"},
                    "autoencoder": {"prediction": "normal"},
                    "models_agree": True,
                },
                "explanations": {"note": "synthetic test evidence"},
                "mitre_mapping": {"mapping_status": "no_mapping", "candidate_techniques": []},
            },
            "untrusted_context": None,
        },
        "parsed_output": {
            "recommendation": "Human analyst may inspect source logs if needed.",
            "uncertainty": "Synthetic fixture; no real incident is established.",
        },
        "validation_status": status,
        "semantic_validation": {"status": "synthetic_test_only"},
        "defense": {"decision": "synthetic_test_only"},
        "output_grounding": {"status": "synthetic_test_only"},
        "errors": [],
        "fallback": fallback,
    }


class HumanReviewAcceptanceTests(unittest.TestCase):
    def run_fixture(self, data, answers):
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            fixture_path = temporary_root / "synthetic_fixture.json"
            fixture_path.write_text(json.dumps(data), encoding="utf-8")
            before = fixture_path.read_bytes()
            with patch.object(human_review, "ROOT", temporary_root), \
                 patch("builtins.input", side_effect=answers), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                saved_path = human_review.review(fixture_path, "Test_Analyst")
            self.assertEqual(before, fixture_path.read_bytes(), "Source fixture was modified")
            self.assertIsNotNone(saved_path)
            record = json.loads(saved_path.read_text(encoding="utf-8"))
            self.assertEqual(record["source_run_sha256"], hashlib.sha256(before).hexdigest())
            self.assertFalse(record["operational_action_executed"])
            return record, output.getvalue()

    def test_synthetic_passed_status_enables_human_acceptance(self):
        # Mock status exercises UI branch only; does not certify any real LLM output.
        data = synthetic_run("heuristic_checks_passed_requires_human_review")
        record, output = self.run_fixture(data, ["1", "Synthetic UI acceptance branch test only"])
        self.assertEqual(record["decision"], "accept_recommendation")
        self.assertFalse(record["automated_recommendation_withheld"])
        self.assertIn("1. accept_recommendation", output)

    def test_semantic_review_blocks_acceptance_even_when_typed(self):
        data = synthetic_run("semantic_review_required", "Synthetic recommendation withheld")
        record, output = self.run_fixture(data, ["1", "2", "Synthetic rejected output"])
        self.assertEqual(record["decision"], "reject_recommendation")
        self.assertTrue(record["automated_recommendation_withheld"])
        self.assertIn("Invalid selection", output)
        self.assertNotIn("1. accept_recommendation", output)

    def test_fallback_blocks_acceptance_even_with_passed_status(self):
        data = synthetic_run("heuristic_checks_passed_requires_human_review", "Synthetic fallback")
        record, output = self.run_fixture(data, ["1", "3", "Need independent evidence", "Source logs"])
        self.assertEqual(record["decision"], "request_more_evidence")
        self.assertTrue(record["automated_recommendation_withheld"])
        self.assertEqual(record["additional_evidence_requested"], "Source logs")
        self.assertIn("Invalid selection", output)


if __name__ == "__main__":
    unittest.main()
