"""Run cases against any AgentAdapter. The agent under test stays pluggable."""

from typing import List, Optional

from .checks import check
from .models import Case, CaseResult, StepResult


class AgentAdapter:
    """One method: send the caller utterance, get the agent's reply."""

    def send(self, utterance: str) -> dict:
        raise NotImplementedError


class ScriptedAgent(AgentAdapter):
    """A canned agent for demos and tests: replies are a list, one per turn."""

    def __init__(self, replies=None, latency_ms: float = 250.0):
        self.replies = list(replies or [])
        self.latency_ms = latency_ms
        self.i = 0

    def send(self, utterance: str) -> dict:
        reply = self.replies[min(self.i, len(self.replies) - 1)]
        self.i += 1
        return {"reply": reply, "latency_ms": self.latency_ms}


class HTTPTurnAgent(AgentAdapter):
    """POST {"utterance": ...} to a live agent endpoint and read {"reply", "latency_ms"}."""

    def __init__(self, url: str, headers: dict = None):
        import json
        import urllib.request
        self._json = json
        self._request = urllib.request.Request
        self._urlopen = urllib.request.urlopen
        self.url = url
        self.headers = headers or {}

    def send(self, utterance: str) -> dict:
        data = self._json.dumps({"utterance": utterance}).encode()
        req = self._request(self.url, data=data, method="POST",
                            headers={"Content-Type": "application/json", **self.headers})
        with self._urlopen(req, timeout=30) as resp:
            return self._json.loads(resp.read().decode())


def run_case(case: Case, agent: AgentAdapter) -> CaseResult:
    captured: dict = {}
    result = CaseResult(name=case.name, passed=True)
    for i, step in enumerate(case.steps):
        out = agent.send(step.caller)
        reply, latency = out["reply"], out.get("latency_ms", 0.0)
        failure = check(step, reply, latency, captured)
        sr = StepResult(index=i, caller=step.caller, reply=reply,
                        latency_ms=latency, passed=failure is None, failure=failure)
        result.steps.append(sr)
        if failure:
            result.passed = False
    return result


def run_all(cases: List[Case], agent: AgentAdapter) -> dict:
    results = [run_case(c, agent) for c in cases]
    passed = sum(1 for r in results if r.passed)
    return {"passed": passed, "total": len(results),
            "ok": passed == len(results), "cases": results}
