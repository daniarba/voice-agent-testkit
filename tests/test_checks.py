import unittest

from voice_agent_testkit.checks import check
from voice_agent_testkit.models import Step


class CheckTests(unittest.TestCase):
    def test_contains_passes_case_insensitive(self):
        self.assertIsNone(check(Step(caller="hi", expect_contains="TUESDAY"), "See you Tuesday!", 100, {}))

    def test_contains_failure_reason(self):
        r = check(Step(caller="hi", expect_contains="tuesday"), "Let me check.", 100, {})
        self.assertIn("missing 'tuesday'", r)

    def test_not_contains(self):
        r = check(Step(caller="hi", expect_not_contains="transfer"), "Transferring you.", 100, {})
        self.assertIn("must not contain", r)

    def test_latency_budget(self):
        r = check(Step(caller="hi", max_latency_ms=500), "ok", 812.0, {})
        self.assertIn("over budget", r)

    def test_capture_slot(self):
        captured = {}
        check(Step(caller="hi", capture="offer"), "Tuesday at 3", 100, captured)
        self.assertEqual(captured["offer"], "Tuesday at 3")


if __name__ == "__main__":
    unittest.main()
