"""Conservative, deterministic ATT&CK context for version-1.0 SOC evidence.

Run from the repository root:
    python src/mitre/map_evidence.py --event-id 3505

The synthetic generator does not specify the observation window for
failed_attempts. Elevated counts therefore yield a possible indicator and
insufficient evidence, NEVER an established ATT&CK technique.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULE_VERSION = 'mitre-t1110-screen-v0.1'
SCREENING_COUNT = 5  # Exploratory synthetic-data rule, NOT a production threshold.


def map_evidence(evidence):
    if not isinstance(evidence, dict) or evidence.get('schema_version') != '1.0':
        raise ValueError('Expected evidence schema_version 1.0')
    event_id = evidence.get('event_id')
    if type(event_id) is not int or event_id < 0:
        raise ValueError('Invalid event_id')
    raw = evidence.get('raw_evidence')
    if not isinstance(raw, dict):
        raise ValueError('Missing raw_evidence')
    count = raw.get('failed_attempts')
    if type(count) is not int or count < 0:
        raise ValueError('failed_attempts must be a nonnegative integer')

    candidate = []
    if count >= SCREENING_COUNT:
        status = 'insufficient_evidence'
        rationale = ('Recorded failure count meets the exploratory screening rule; '
                     'the generator does not establish an observation window or '
                     'independently verified authentication-attempt sequence.')
        candidate.append({
            'technique_id': 'T1110',
            'technique_name': 'Brute Force',
            'tactic_id': 'TA0006',
            'tactic_name': 'Credential Access',
            'assessment': 'possible_indicator_not_confirmed',
            'observed_fields': {'failed_attempts': count},
            'rationale': rationale,
            'missing_evidence': [
                'confirmed observation/aggregation window',
                'timestamped authentication failures',
                'source identifier and authentication logs',
            ],
        })
    else:
        status = 'no_mapping'
        rationale = ('Recorded failure count is below the exploratory screening '
                     'rule. This does not establish that the event is benign.')

    return {
        'schema_version': '1.0',
        'event_id': event_id,
        'mapping_status': status,
        'candidate_techniques': candidate,
        'unmapped_observations': [
            'country', 'device', 'hour', 'distance_km',
            'session_minutes', 'bytes_out_mb', 'protocol',
        ],
        'rationale': rationale,
        'rule_version': RULE_VERSION,
        'screening_threshold': SCREENING_COUNT,
        'screening_threshold_scope': 'exploratory_synthetic_only',
        'llm_generated': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event-id', required=True, type=int)
    args = parser.parse_args()
    source = ROOT / 'results/explainability/evidence' / f'event_{args.event_id}_evidence.json'
    with source.open(encoding='utf-8') as f:
        evidence = json.load(f)
    result = map_evidence(evidence)
    target_dir = ROOT / 'results/mitre'
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f'event_{args.event_id}_mitre.json'
    with target.open('w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
    print(f'Event: {result["event_id"]}')
    print(f'Mapping status: {result["mapping_status"]}')
    print(f'Candidates: {len(result["candidate_techniques"])}')
    print(f'Saved: {target}')


if __name__ == '__main__':
    main()
