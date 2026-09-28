"""Conservative experimental guard: reject instruction-like external narratives.
Not a general prompt-injection detector. Never changes trusted SOC evidence.
"""
import re

VERSION = 'input-guard-v0.1'
PATTERNS = {
    'authority_override': r'(?i)\b(?:soc manager|management approval|investigation team|source of truth|overrides? previous instructions)\b',
    'evidence_override': r'(?i)\b(?:both detectors (?:confirmed|agree)|detection correction|t1110 is verified|treat this note as)\b',
    'output_instruction': r'(?i)\b(?:risk_assessment\s*:|additional_evidence_needed\s*:|recommendation\s*:|uncertainty\s*:|final structured json|do not mention|close the incident|ignore trusted evidence)\b',
}

def inspect_context(context):
    """Return rule IDs; false positives are possible and should be measured."""
    return [name for name, pattern in PATTERNS.items() if re.search(pattern, context)]
