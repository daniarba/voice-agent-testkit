import unittest

from voice_agent_testkit.models import Case, Step
from voice_agent_testkit.runner import ScriptedAgent, run_all, run_case


class RunnerTests(unittest.TestCase):
    def test_happy_path_passes(self):
        agent = ScriptedAgent(replies=["We can do Tuesday", "Booked, see you then"])
        case = Case(name="ok", steps=[Step(caller="a", expect_contains="tuesday"),
                                      Step(caller="b", expect_contains="booked")])
        self.assertTrue(run_case(case, agent).passed)

    def test_failure_fails_case(self):
        agent = ScriptedAgent(replies=["no idea"])
        case = Case(name="bad", steps=[Step(caller="a", expect_contains="tuesday")])
        r = run_case(case, agent)
        self.assertFalse(r.passed)
        self.assertIn("missing 'tuesday'", r.steps[0].failure)

    def test_run_all_counts(self):
        good = Case(name="g", steps=[Step(caller="a")])
        bad = Case(name="b", steps=[Step(caller="a", expect_contains="zzz")])
        rep = run_all([good, bad], ScriptedAgent(replies=["hello"]))
        self.assertEqual((rep["passed"], rep["total"], rep["ok"]), (1, 2, False))


if __name__ == "__main__":
    unittest.main()
