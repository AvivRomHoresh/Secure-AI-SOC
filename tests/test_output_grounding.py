import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'llm'))
from output_grounding import inspect_output

TRUSTED={'mitre_mapping':{'mapping_status':'insufficient_evidence'},'detection':{'models_agree':False}}

def output(**kw):
    value={'incident_summary':'Anomalous activity merits review', 'risk_assessment':'Moderate due to 13 failed attempts and detector disagreement', 'mitre_context':['T1110 is a possible unconfirmed candidate'], 'uncertainty':'Evidence insufficient', 'recommendation':'Review authentication logs', 'evidence_used':[], 'additional_evidence_needed':[]}
    value.update(kw)
    return value

class OutputGroundingTests(unittest.TestCase):
    def test_benign_qualified(self):
        self.assertEqual(inspect_output(TRUSTED,output()),[])
    def test_confirmed_attack_summary_even_with_disclaimer_elsewhere(self):
        self.assertIn('Unsupported confirmed technique claim in incident_summary',inspect_output(TRUSTED,output(incident_summary='Brute-force attack detected')))
    def test_unqualified_confirmed_mitre_context(self):
        self.assertIn('Unsupported confirmed technique claim in mitre_context',inspect_output(TRUSTED,output(mitre_context=['T1110 brute force confirmed'])))
    def test_bare_moderate_risk(self):
        self.assertIn('Risk label has no field-local rationale',inspect_output(TRUSTED,output(risk_assessment='Moderate risk')))
    def test_false_agreement(self):
        self.assertIn('Output contradicts trusted detector disagreement',inspect_output(TRUSTED,output(incident_summary='Both detectors confirmed the anomaly')))
    def test_unwarranted_closure(self):
        self.assertIn('Closure recommendation unsupported by incomplete evidence',inspect_output(TRUSTED,output(recommendation='Close the incident')))
    def test_uncertainty_false_positive(self):
        self.assertIn('Unsupported certainty or false-positive claim',inspect_output(TRUSTED,output(uncertainty='Known false positive')))
    def test_qualified_possible_brute_force(self):
        self.assertEqual(inspect_output(TRUSTED,output(incident_summary='Possible brute force, not confirmed')),[])

if __name__=='__main__':unittest.main()
