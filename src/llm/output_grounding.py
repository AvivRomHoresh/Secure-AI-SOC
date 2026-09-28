"""Conservative, deterministic field-specific grounding flags; not proof of truth."""
import re

VERSION = 'output-grounding-v0.1'


def inspect_output(trusted, output):
    """Return review flags; never rewrite evidence or generated output."""
    issues = []
    mapping = trusted.get('mitre_mapping', {})
    detection = trusted.get('detection', {})
    summary = output['incident_summary']
    risk = output['risk_assessment']
    uncertainty = output['uncertainty']
    mitre = ' '.join(output['mitre_context'])
    recommendation = output['recommendation']
    decision_text = ' '.join((summary, risk, uncertainty, recommendation))

    if mapping.get('mapping_status') == 'insufficient_evidence':
        # Check qualification *where the technique is asserted*, not elsewhere.
        for field, text in (('incident_summary', summary), ('mitre_context', mitre)):
            if re.search(r'\b(brute[ -]?force|T1110)\b', text, re.I):
                confirmed = re.search(r'\b(confirmed|verified|proven|established|detected|identified)\b', text, re.I)
                qualified = re.search(r'\b(possible|potential|suspected|candidate|unconfirmed|not confirmed|not verified|insufficient evidence|may|might)\b', text, re.I)
                if confirmed and not qualified:
                    issues.append(f'Unsupported confirmed technique claim in {field}')
        if re.search(r'\b(no uncertainty|uncertainty:\s*none|false positive (?:confirmed|verified)|known false positive)\b', decision_text, re.I):
            issues.append('Unsupported certainty or false-positive claim')

    if detection.get('models_agree') is False:
        if re.search(r'\b(detectors?|models?)\s+(?:both\s+)?(?:agree|concur)\b|\bboth detectors? confirmed\b', decision_text, re.I):
            issues.append('Output contradicts trusted detector disagreement')

    if re.fullmatch(r'\s*(low|medium|moderate|high|critical)(?:\s+risk)?\s*', risk, re.I):
        issues.append('Risk label has no field-local rationale')

    if re.search(r'\b(close (?:the |this )?incident|no (?:further |additional )?investigation (?:is )?(?:needed|required))\b', recommendation, re.I):
        if mapping.get('mapping_status') == 'insufficient_evidence' or detection.get('models_agree') is False:
            issues.append('Closure recommendation unsupported by incomplete evidence')
    return issues
