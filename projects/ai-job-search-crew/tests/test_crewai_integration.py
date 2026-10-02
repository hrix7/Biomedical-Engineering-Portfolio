"""Optional: actual CrewAI orchestration with a simulated model, no network/model required."""
import importlib.util
import unittest
from local_ai import run_crewai, decode


@unittest.skipUnless(importlib.util.find_spec('crewai'), 'Optional CrewAI dependency not installed')
class CrewIntegrationTest(unittest.TestCase):
    def test_three_agents_use_the_explicit_local_adapter(self):
        class FakeClient:
            model='test-local-model'
            calls=0
            def call(self,messages):
                self.calls+=1
                return 'Final Answer: {"cover_letter":"A simulated response for adapter testing only.","evidence_ids":["EXP3.1"],"reviewer_notes":["Simulated test only"]}'
        client=FakeClient()
        result=decode(run_crewai('Simulated data; not a real candidate.',client))
        self.assertEqual(result['evidence_ids'],['EXP3.1'])
        self.assertEqual(client.calls,3)


if __name__=='__main__':unittest.main()
