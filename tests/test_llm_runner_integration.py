"""Phase 6 runner-level tests using a mocked local Ollama API.

Place in tests/ and run: python -m unittest discover -s tests -v
No real model calls; no existing research artifacts or logs are modified.
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src' / 'llm'))
import run_local_llm as runner


class FakeHTTPResponse:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, *args):
        return json.dumps(self.value).encode('utf-8')


class RunnerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.event_id = 3505
        self.source = {
            'schema_version': '1.0', 'event_id': self.event_id,
            'trusted': {
                'raw_evidence': {'failed_attempts': 7},
                'detection': {'models_agree': True},
                'explanations': {},
                'mitre_mapping': {'mapping_status': 'no_mapping', 'candidate_techniques': []},
            },
            'untrusted_context': None,
        }
        self.original_source = copy.deepcopy(self.source)
        self.output = {
            'incident_summary': 'Investigate the observed event.',
            'risk_assessment': 'Uncertain pending additional authentication evidence.',
            'evidence_used': ['failed_attempts'],
            'mitre_context': [],
            'recommendation': 'Human analyst should review authentication records.',
            'uncertainty': 'Additional evidence is needed.',
            'additional_evidence_needed': ['Timestamped authentication records'],
        }

    def _run(self, api_reply=None, fail_api=False):
        before = hashlib.sha256(json.dumps(self.source, sort_keys=True).encode()).hexdigest()
        calls = []

        def fake_urlopen(request, timeout=15):
            url = request if isinstance(request, str) else request.full_url
            calls.append(url)
            if url.endswith('/api/tags'):
                return FakeHTTPResponse({'models': [
                    {'name': runner.MODEL, 'digest': runner.EXPECTED_DIGEST}]})
            if url.endswith('/api/chat'):
                if fail_api:
                    raise OSError('Simulated Ollama failure')
                reply = api_reply if api_reply is not None else json.dumps(self.output)
                return FakeHTTPResponse({'message': {'content': reply},
                                         'total_duration': 1, 'load_duration': 1,
                                         'prompt_eval_count': 1, 'eval_count': 1})
            raise AssertionError(f'Unexpected API request: {url}')

        with patch.object(runner, 'ROOT', self.root), \
             patch.object(runner, 'assemble', return_value=self.source), \
             patch.object(runner.urllib.request, 'urlopen', side_effect=fake_urlopen), \
             patch.object(runner, 'PROMPT_PATH', ROOT / 'src' / 'llm' / 'system_prompt_v1.txt'):
            success = runner.run(self.event_id)
        after = hashlib.sha256(json.dumps(self.source, sort_keys=True).encode()).hexdigest()
        self.assertEqual(before, after, 'Runner mutated its assembled source evidence')
        self.assertEqual(self.source, self.original_source)
        logs = list((self.root / 'results' / 'llm').glob('*.json'))
        self.assertEqual(len(logs), 1, 'Expected exactly one new run log')
        with logs[0].open(encoding='utf-8') as f:
            log = json.load(f)
        self.assertEqual(log['llm_input'], self.original_source)
        self.assertEqual(log['event_id'], self.event_id)
        return success, log, calls

    def test_valid_mocked_response_is_logged_without_mutating_evidence(self):
        success, log, calls = self._run()
        self.assertTrue(success)
        self.assertEqual(log['validation_status'],
                         'heuristic_checks_passed_requires_human_review')
        self.assertIsNone(log['fallback'])
        self.assertEqual(len(calls), 2)

    def test_malformed_json_triggers_fallback_and_preserves_evidence(self):
        success, log, _ = self._run(api_reply='not json')
        self.assertFalse(success)
        self.assertEqual(log['validation_status'], 'failed')
        self.assertIsNotNone(log['fallback'])

    def test_unsupported_mitre_technique_triggers_fallback(self):
        bad = copy.deepcopy(self.output)
        bad['mitre_context'] = ['Confirmed T9999']
        success, log, _ = self._run(api_reply=json.dumps(bad))
        self.assertFalse(success)
        self.assertEqual(log['validation_status'], 'failed')
        self.assertTrue(any('MITRE' in error for error in log['errors']))

    def test_ollama_failure_triggers_fallback_and_preserves_evidence(self):
        success, log, _ = self._run(fail_api=True)
        self.assertFalse(success)
        self.assertEqual(log['validation_status'], 'failed')
        self.assertIsNotNone(log['fallback'])

    def test_semantic_failure_withholds_automated_recommendation(self):
        bad = copy.deepcopy(self.output)
        bad['risk_assessment'] = 'Low'
        success, log, _ = self._run(api_reply=json.dumps(bad))
        self.assertTrue(success, 'Review-required is not a runtime error')
        self.assertEqual(log['validation_status'], 'semantic_review_required')
        self.assertIsNotNone(log['fallback'])
        self.assertTrue(log['semantic_validation']['issues'])


if __name__ == '__main__':
    unittest.main()
