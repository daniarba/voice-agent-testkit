"""CLI: python -m voice_agent_testkit --demo  or  --cases scenarios.json --endpoint URL."""

import argparse
import json
import sys

from .models import Case
from .runner import HTTPTurnAgent, ScriptedAgent, run_all


def fmt(res) -> str:
    lines = [f"[{'PASS' if res.passed else 'FAIL'}] {res.name}"]
    for s in res.steps:
        lines.append(f"  step {s.index + 1}: caller={s.caller!r} latency={s.latency_ms:.0f}ms "
                     f"{'ok' if s.passed else 'FAIL: ' + (s.failure or '')}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="voice-agent-testkit")
    ap.add_argument("--demo", action="store_true", help="run on the built-in scripted agent")
    ap.add_argument("--cases", help="JSON file with a list of cases")
    ap.add_argument("--endpoint", help="live agent endpoint; POSTs each turn as JSON")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    if args.demo:
        cases = DEMO_CASES
        agent = ScriptedAgent(replies=[
            "We can book you for Tuesday at 3 PM. What is the name for the appointment?",
            "Booked, Tuesday 3 PM. A confirmation is on its way to your phone.",
        ])
    elif args.cases:
        raw = json.load(open(args.cases))
        cases = [Case.from_dict(c) for c in raw]
        if not args.endpoint:
            ap.error("--cases needs --endpoint URL (or use --demo)")
        agent = HTTPTurnAgent(args.endpoint)
    else:
        ap.error("pass --demo or --cases file + --endpoint url")
        return 2

    report = run_all(cases, agent)
    if args.json:
        import dataclasses
        out = {k: v for k, v in report.items() if k != "cases"}
        out["cases"] = [dataclasses.asdict(c) for c in report["cases"]]
        print(json.dumps(out, indent=2))
    else:
        for r in report["cases"]:
            print(fmt(r))
        print(f"\n{report['passed']}/{report['total']} cases passed")
    return 0 if report["ok"] else 1


DEMO_CASES = [
    Case(name="booking_happy_path", steps=[
        __import__("voice_agent_testkit.models", fromlist=["Step"]).Step(
            caller="I need a dentist appointment",
            expect_contains="tuesday",
            capture="offer",
            max_latency_ms=500),
        __import__("voice_agent_testkit.models", fromlist=["Step"]).Step(
            caller="Tuesday works",
            expect_contains="booked",
            expect_not_contains="transfer",
            max_latency_ms=500),
    ]),
]

if __name__ == "__main__":
    sys.exit(main())
