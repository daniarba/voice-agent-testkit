"""Data models: a case is a scripted caller, a result is what the agent said back."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Step:
    caller: str            # what the simulated caller says
    expect_contains: Optional[str] = None   # agent reply must include this
    expect_not_contains: Optional[str] = None
    capture: Optional[str] = None           # remember this reply under a slot name
    max_latency_ms: Optional[float] = None  # reply must answer within this


@dataclass
class Case:
    name: str
    steps: List[Step] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "Case":
        steps = [Step(**s) for s in d.get("steps", [])]
        return cls(name=d["name"], steps=steps)


@dataclass
class StepResult:
    index: int
    caller: str
    reply: str
    latency_ms: float
    passed: bool
    failure: Optional[str] = None


@dataclass
class CaseResult:
    name: str
    passed: bool
    steps: List[StepResult] = field(default_factory=list)
