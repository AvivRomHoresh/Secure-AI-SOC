"""Phase 4: validate saved operational evidence against frozen test results.

Run from repository root:
    python -m unittest discover -s tests -p "test_evidence.py" -v

No retraining, threshold tuning, or modification of saved evidence.
"""
import json
import math
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVENTS = {3216: (0, 0), 2624: (1, 1), 3505: (0, 1)}


def read_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


class EvidenceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = read_json(ROOT / "config/project_config.json")
        cls.predictions = pd.read_csv(ROOT / "results/detection_comparison/test_predictions.csv")
        cls.raw = pd.read_csv(ROOT / "data/processed/splits/test.csv")
        cls.if_threshold = read_json(ROOT / "results/isolation_forest/threshold_selection.json")["threshold"]
        cls.ae_threshold = read_json(ROOT / "results/autoencoder/threshold_selection.json")["selected_threshold"]
        cls.fields = set(cls.config["preprocessing"]["categorical_features"] + cls.config["preprocessing"]["numerical_features"])
        cls.base = ROOT / "results/explainability"

    def test_saved_records_match_frozen_predictions(self):
        for event_id, expected in EVENTS.items():
            with self.subTest(event_id=event_id):
                record = read_json(self.base / "evidence" / f"event_{event_id}_evidence.json")
                rows = self.predictions.loc[self.predictions.event_id.eq(event_id)]
                self.assertEqual(len(rows), 1)
                p = rows.iloc[0]
                self.assertEqual(record["schema_version"], "1.0")
                self.assertEqual(record["event_id"], event_id)
                det = record["detection"]
                self.assertAlmostEqual(det["isolation_forest"]["anomaly_score"], p.isolation_forest_score, places=6)
                self.assertAlmostEqual(det["autoencoder"]["reconstruction_mse"], p.autoencoder_reconstruction_mse, places=6)
                self.assertAlmostEqual(det["isolation_forest"]["validation_selected_threshold"], self.if_threshold)
                self.assertAlmostEqual(det["autoencoder"]["validation_selected_threshold"], self.ae_threshold)
                if_pred = int(p.isolation_forest_score >= self.if_threshold)
                ae_pred = int(p.autoencoder_reconstruction_mse >= self.ae_threshold)
                self.assertEqual((if_pred, ae_pred), expected)
                self.assertEqual((if_pred, ae_pred), (int(p.isolation_forest_pred), int(p.autoencoder_pred)))
                self.assertEqual(det["isolation_forest"]["prediction"], "anomaly" if if_pred else "normal")
                self.assertEqual(det["autoencoder"]["prediction"], "anomaly" if ae_pred else "normal")
                self.assertEqual(det["models_agree"], if_pred == ae_pred)

    def test_raw_fields_match_original_events(self):
        for event_id in EVENTS:
            with self.subTest(event_id=event_id):
                record = read_json(self.base / "evidence" / f"event_{event_id}_evidence.json")
                rows = self.raw.loc[self.raw.event_id.eq(event_id)]
                self.assertEqual(len(rows), 1)
                row = rows.iloc[0]
                self.assertEqual(set(record["raw_evidence"]), self.fields)
                for field in self.fields:
                    actual = record["raw_evidence"][field]
                    expected = row[field]
                    if isinstance(actual, (float, int)) and not isinstance(actual, bool):
                        self.assertTrue(math.isclose(actual, float(expected), rel_tol=1e-9, abs_tol=1e-9), field)
                    else:
                        self.assertEqual(actual, expected)

    def test_explanations_cover_original_fields(self):
        for event_id in EVENTS:
            with self.subTest(event_id=event_id):
                record = read_json(self.base / "evidence" / f"event_{event_id}_evidence.json")
                explanations = record["explanations"]
                grouped = explanations["autoencoder"]["grouped_squared_reconstruction_error"]
                sensitivities = explanations["isolation_forest"]["feature_sensitivity"]
                self.assertEqual(set(grouped), self.fields)
                self.assertTrue(all(math.isfinite(float(v)) and float(v) >= 0 for v in grouped.values()))
                self.assertEqual(len(sensitivities), len(self.fields))
                self.assertEqual({item["field"] for item in sensitivities}, self.fields)
                for item in sensitivities:
                    self.assertAlmostEqual(
                        item["original_anomaly_score"] - item["replaced_anomaly_score"],
                        item["score_drop_when_replaced"], places=8,
                    )
                self.assertIn("not causal", explanations["autoencoder"]["interpretation"].lower())
                self.assertIn("not causal", explanations["isolation_forest"]["interpretation"].lower())

    def test_no_ground_truth_or_premature_decisions(self):
        forbidden = {"is_attack", "actual_label", "ground_truth", "true_label"}
        for event_id in EVENTS:
            with self.subTest(event_id=event_id):
                record = read_json(self.base / "evidence" / f"event_{event_id}_evidence.json")
                self.assertTrue(forbidden.isdisjoint(record.keys()))
                self.assertTrue(forbidden.isdisjoint(record["raw_evidence"].keys()))
                self.assertTrue(forbidden.isdisjoint(record["detection"].keys()))
                self.assertTrue(forbidden.isdisjoint(record["explanations"].keys()))
                self.assertIsNone(record["mitre_mapping"])
                self.assertIsNone(record["llm_recommendation"])
                self.assertIsNone(record["human_decision"])
                self.assertIn("not proof", record["analyst_notice"].lower())


if __name__ == "__main__":
    unittest.main()
