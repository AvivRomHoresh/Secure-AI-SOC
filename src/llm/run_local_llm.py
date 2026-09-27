"""Phase 6 local Ollama advisory runner. Run from the repository root.

python src/llm/run_local_llm.py --event-id 3505
Writes new logs only; never changes upstream evidence or previous run logs.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from build_llm_input import ROOT, assemble
from validate_llm_output import check_run

MODEL = 'llama3.2:3b'
EXPECTED_DIGEST = 'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
API = 'http://127.0.0.1:11434'
PROMPT_PATH = Path(__file__).with_name('system_prompt_v1.txt')
FIELDS = {
    'incident_summary': 'string',
    'risk_assessment': 'string',
    'evidence_used': 'array',
    'mitre_context': 'array',
    'recommendation': 'string',
    'uncertainty': 'string',
    'additional_evidence_needed': 'array',
}
OUTPUT_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': list(FIELDS),
    'properties': {
        key: ({'type': 'string', 'maxLength': 2500} if kind == 'string'
              else {'type': 'array', 'items': {'type': 'string', 'maxLength': 600}, 'maxItems': 20})
        for key, kind in FIELDS.items()
    },
}


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def sha256(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def get_json(path, timeout=15):
    with urllib.request.urlopen(API + path, timeout=timeout) as response:
        return json.load(response)


def validate(result, source):
    """Structural checks and a narrow whitelist for ATT&CK technique IDs."""
    errors = []
    if type(result) is not dict or set(result) != set(FIELDS):
        return ['Response must be an object with exactly the seven required fields']
    for key, kind in FIELDS.items():
        value = result[key]
        if kind == 'string':
            if type(value) is not str or len(value) > 2500:
                errors.append(f'Invalid {key}: expected string of at most 2500 characters')
        elif type(value) is not list or len(value) > 20 or any(
                type(x) is not str or len(x) > 600 for x in value):
            errors.append(f'Invalid {key}: expected up to 20 short strings')
    if errors:
        return errors
    mapping = source['trusted']['mitre_mapping']
    allowed = {item['technique_id'].upper() for item in mapping['candidate_techniques']}
    mentioned = {x.upper() for x in re.findall(r'\bT\d{4}(?:\.\d{3})?\b', compact(result), re.I)}
    if mentioned - allowed:
        errors.append('Response mentions MITRE technique IDs absent from trusted mapping')
    if mapping['mapping_status'] == 'no_mapping' and result['mitre_context']:
        errors.append('MITRE context must be empty when there is no mapping')
    return errors


def assess_response(log):
    """Run semantic heuristics only after structural validation; never rewrite output."""
    if log['validation_status'] == 'failed':
        log['semantic_validation'] = {'status': 'not_run', 'issues': []}
        return
    issues = check_run(log)
    log['semantic_validation'] = {
        'status': ('requires_human_review' if issues else
                   'heuristic_checks_passed_requires_human_review'),
        'issues': issues,
        'note': 'Heuristics do not prove factual correctness or prompt-injection resistance.',
    }
    if issues:
        log['validation_status'] = 'semantic_review_required'
        log['fallback'] = ('Automated LLM recommendation withheld due to semantic issues; '
                           'inspect original evidence and MITRE mapping manually.')
    else:
        log['validation_status'] = 'heuristic_checks_passed_requires_human_review'


def load_untrusted_context(path):
    """Read bounded UTF-8 experimental narrative, never trusted evidence."""
    if path is None:
        return None
    raw = Path(path).read_bytes()
    if not raw or len(raw) > 4096:
        raise ValueError('Untrusted context file must contain 1-4096 bytes')
    content = raw.decode('utf-8')
    if len(content) > 2000 or not content.strip():
        raise ValueError('Untrusted context must contain 1-2000 nonblank characters')
    return content


def run(event_id, condition='baseline', untrusted_context_file=None):
    if condition not in ('baseline', 'adversarial'):
        raise ValueError('Only baseline and adversarial are implemented; defended is pending')
    if (condition == 'baseline') != (untrusted_context_file is None):
        raise ValueError('Baseline must have no context; adversarial requires a context file')
    source = assemble(event_id)
    trusted_hash = sha256(compact(source['trusted']))
    context = load_untrusted_context(untrusted_context_file)
    if context is not None:
        # assemble() always supplies None; modify only the isolated request copy.
        source['untrusted_context'] = context
    prompt = PROMPT_PATH.read_text(encoding='utf-8')
    source_json = compact(source)
    log = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'event_id': event_id, 'model': MODEL, 'expected_digest': EXPECTED_DIGEST,
        'experiment_condition': condition, 'trusted_sha256': trusted_hash,
        'untrusted_context_sha256': sha256(context) if context is not None else None,
        'prompt_version': 'soc-system-v1.0', 'system_prompt': prompt,
        'llm_input': source, 'llm_input_sha256': sha256(source_json),
        'system_prompt_sha256': sha256(prompt),
        'settings': {'temperature': 0, 'seed': 42, 'num_ctx': 8192, 'stream': False},
        'validation_status': 'not_run', 'raw_output': None, 'parsed_output': None,
        'semantic_validation': {'status': 'not_run', 'issues': []},
        'errors': [], 'fallback': None,
    }
    try:
        tags = get_json('/api/tags')
        match = next((x for x in tags.get('models', []) if x.get('name') == MODEL), None)
        if not match or match.get('digest') != EXPECTED_DIGEST:
            raise ValueError('Installed model digest does not match recorded experiment model')
        log['observed_digest'] = match['digest']
        request = {
            'model': MODEL, 'stream': False, 'format': OUTPUT_SCHEMA,
            'options': {'temperature': 0, 'seed': 42, 'num_ctx': 8192},
            'messages': [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': source_json},
            ],
        }
        log['request_sha256'] = sha256(compact(request))
        req = urllib.request.Request(
            API + '/api/chat', data=compact(request).encode('utf-8'),
            headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=240) as response:
            api_result = json.load(response)
        log['ollama_metrics'] = {k: api_result.get(k) for k in
                                 ('total_duration', 'load_duration', 'prompt_eval_count', 'eval_count')}
        raw = api_result['message']['content']
        if type(raw) is not str:
            raise ValueError('Missing textual model response')
        log['raw_output'] = raw
        log['raw_output_sha256'] = sha256(raw)
        parsed = json.loads(raw)
        log['parsed_output'] = parsed
        errors = validate(parsed, source)
        if errors:
            log['errors'] = errors
            log['validation_status'] = 'failed'
        else:
            log['validation_status'] = 'structurally_valid_requires_human_review'
            assess_response(log)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError,
            urllib.error.URLError) as exc:
        log['validation_status'] = 'failed'
        log['errors'].append(f'{type(exc).__name__}: {exc}')
    if log['validation_status'] == 'failed':
        log['fallback'] = ('LLM recommendation unavailable; inspect original '
                           'evidence and MITRE mapping manually.')
    outdir = ROOT / 'results' / 'llm'
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / (f'event_{event_id}_'
                        f'{datetime.now(timezone.utc):%Y%m%dT%H%M%S}_{uuid4().hex[:8]}.json')
    with outfile.open('x', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({
        'status': log['validation_status'],
        'semantic_validation': log['semantic_validation'],
        'errors': log['errors'], 'fallback': log['fallback'],
        'log_path': str(outfile),
    }, ensure_ascii=False, indent=2))
    # A review-required result is not an approved recommendation, but the runner
    # completed normally; nonzero exit is reserved for structural/runtime failure.
    return log['validation_status'] != 'failed'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event-id', type=int, required=True)
    parser.add_argument('--condition', choices=('baseline', 'adversarial'), default='baseline')
    parser.add_argument('--untrusted-context-file', type=Path)
    args = parser.parse_args()
    sys.exit(0 if run(args.event_id, args.condition, args.untrusted_context_file) else 1)
