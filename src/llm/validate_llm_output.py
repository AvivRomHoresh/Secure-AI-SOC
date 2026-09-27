"""Phase 6: deterministic semantic checks of a logged SOC LLM recommendation.

Run from the project root:
    python src/llm/validate_llm_output.py results/llm/<run-log>.json

These checks are conservative heuristics, not proof of factual correctness.
They never modify upstream evidence, the LLM response, or the run log.
"""
import argparse
import json
import re
from pathlib import Path

OUTPUT_FIELDS = {
    'incident_summary', 'risk_assessment', 'evidence_used', 'mitre_context',
    'recommendation', 'uncertainty', 'additional_evidence_needed',
}

def mentions(text, term):
    return re.search(r'(?<!\w)' + re.escape(term) + r'(?!\w)', text, re.I) is not None

def check_run(log):
    issues = []
    data = log.get('llm_input', {})
    trusted = data.get('trusted', {})
    detection = trusted.get('detection', {})
    mapping = trusted.get('mitre_mapping', {})
    output = log.get('parsed_output')
    if not isinstance(output, dict) or set(output) != OUTPUT_FIELDS:
        return ['Invalid or missing parsed output structure']
    narrative = ' '.join(str(output[k]) for k in
                         ('incident_summary', 'risk_assessment', 'recommendation', 'uncertainty'))
    full_text = ' '.join([narrative] + [str(x) for x in output['mitre_context']])

    if detection.get('models_agree') is False:
        # Requiring explicit model names and differing decisions avoids treating
        # a generic "anomaly detected" statement as sufficient disclosure.
        if not re.search(r'isolation[ _-]*forest', narrative, re.I) or not re.search(r'autoencoder', narrative, re.I):
            issues.append('Detector disagreement not explicitly attributed to BOTH models')
        else:
            if not re.search(r'\b(normal|not anomalous|non.anomalous)\b', narrative, re.I) or not re.search(r'\b(anomaly|anomalous|flagged)\b', narrative, re.I):
                issues.append('Detector disagreement lacks the two different predictions')

    if mapping.get('mapping_status') == 'insufficient_evidence':
        candidates = mapping.get('candidate_techniques', [])
        if candidates:
            ids = [x.get('technique_id', '') for x in candidates]
            if not all(mentions(full_text, x) for x in ids):
                issues.append('Candidate MITRE technique ID missing')
            if not re.search(r'\b(unconfirmed|not confirmed|possible|candidate|insufficient evidence|not established)\b', full_text, re.I):
                issues.append('MITRE candidate is not explicitly qualified as unconfirmed')
            if not re.search(r'\b(auth|timestamp|observation window|source|corroborat)', full_text, re.I):
                issues.append('MITRE candidate lacks mention of corroborating evidence')
    elif mapping.get('mapping_status') == 'no_mapping':
        if re.search(r'\bT\d{4}(?:\.\d{3})?\b', full_text, re.I):
            issues.append('MITRE technique claimed despite no_mapping')

    risk = output['risk_assessment']
    # A bare risk label without rationale is not a substantiated assessment.
    if re.fullmatch(r'\s*(low|medium|moderate|high|critical)\s*', risk, re.I):
        issues.append('Risk assessment is an unexplained categorical label')

    return issues

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_log', type=Path, help='Existing JSON run log (read-only)')
    args = parser.parse_args()
    with args.run_log.open(encoding='utf-8') as f:
        log = json.load(f)
    issues = check_run(log)
    result = {
        'event_id': log.get('event_id'),
        'semantic_status': 'requires_human_review' if issues else 'heuristic_checks_passed_requires_human_review',
        'issues': issues,
        'note': 'Heuristic checks only. Passing does not prove groundedness or prompt-injection resistance.'
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if issues else 0

if __name__ == '__main__':
    raise SystemExit(main())
