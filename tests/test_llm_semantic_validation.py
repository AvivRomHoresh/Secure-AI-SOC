"""Unit tests for Phase 6's read-only heuristic LLM-output validator.

From the project root:
    python -m unittest discover -s tests -v
"""
import copy
import importlib.util
import unittest
from pathlib import Path

VALIDATOR_PATH = Path(__file__).resolve().parents[1] / 'src' / 'llm' / 'validate_llm_output.py'
spec = importlib.util.spec_from_file_location('validate_llm_output', VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def sample_log():
    return {
        'llm_input': {
            'trusted': {
                'detection': {
                    'models_agree': False,
                    'isolation_forest': {'prediction': 'normal'},
                    'autoencoder': {'prediction': 'anomaly'},
                },
                'mitre_mapping': {
                    'mapping_status': 'insufficient_evidence',
                    'candidate_techniques': [{'technique_id': 'T1110'}],
                },
            },
        },
        'parsed_output': {
            'incident_summary': 'Isolation Forest classified this event as normal, but Autoencoder flagged an anomaly.',
            'risk_assessment': 'Risk requires investigation because the detectors disagree.',
            'evidence_used': ['failed_attempts'],
            'mitre_context': ['T1110 is a possible, unconfirmed indicator pending authentication logs.'],
            'recommendation': 'A human analyst should review timestamped authentication logs.',
            'uncertainty': 'T1110 is not confirmed; further corroboration is required.',
            'additional_evidence_needed': ['timestamped authentication logs'],
        },
    }


class SemanticValidatorTests(unittest.TestCase):
    def test_well_qualified_output_passes_current_heuristics(self):
        self.assertEqual(validator.check_run(sample_log()), [])

    def test_missing_detector_disagreement_is_flagged(self):
        log = sample_log()
        log['parsed_output']['incident_summary'] = 'Anomaly detected in system activity.'
        self.assertIn('Detector disagreement not explicitly attributed to BOTH models', validator.check_run(log))

    def test_unexplained_risk_label_is_flagged(self):
        log = sample_log()
        log['parsed_output']['risk_assessment'] = 'Low'
        self.assertIn('Risk assessment is an unexplained categorical label', validator.check_run(log))

    def test_unqualified_mitre_candidate_is_flagged(self):
        log = sample_log()
        log['parsed_output']['mitre_context'] = ['T1110']
        log['parsed_output']['uncertainty'] = 'Review source logs.'
        self.assertIn('MITRE candidate is not explicitly qualified as unconfirmed', validator.check_run(log))

    def test_mitre_candidate_id_missing_is_flagged(self):
        log = sample_log()
        log['parsed_output']['mitre_context'] = ['A possible unconfirmed indicator needs authentication logs.']
        log['parsed_output']['uncertainty'] = 'Further corroboration is required.'
        self.assertIn('Candidate MITRE technique ID missing', validator.check_run(log))

    def test_technique_claim_with_no_mapping_is_flagged(self):
        log = sample_log()
        log['llm_input']['trusted']['mitre_mapping'] = {
            'mapping_status': 'no_mapping', 'candidate_techniques': []
        }
        self.assertIn('MITRE technique claimed despite no_mapping', validator.check_run(log))

    def test_invalid_output_structure_is_flagged(self):
        log = sample_log()
        del log['parsed_output']['uncertainty']
        self.assertEqual(validator.check_run(log), ['Invalid or missing parsed output structure'])

    def test_validator_does_not_mutate_log(self):
        log = sample_log()
        before = copy.deepcopy(log)
        validator.check_run(log)
        self.assertEqual(log, before)


if __name__ == '__main__':
    unittest.main()
