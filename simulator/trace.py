"""Data classes for the toy simulation. No I/O, no behavior — pure data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal


@dataclass(frozen=True)
class Identity:
    """A fictional enterprise identity used by the toy actors."""

    name: str
    role: str
    scopes: frozenset[str]


@dataclass
class ToolResult:
    """Result returned by a fictional internal tool."""

    tool: str
    status: int
    observation: str
    detection_probability: float
    sensitive_exposure: bool = False


@dataclass
class Step:
    """One step in an execution trace."""

    actor: str
    tool: str
    reason: str
    status: int
    observation: str
    detection_probability: float
    detected_after_step: bool
    sensitive_exposure: bool = False
    memory_after_step: List[str] = field(default_factory=list)


@dataclass
class RunResult:
    """Execution trace plus outcome."""

    name: str
    kind: Literal["static", "agentic"]
    goal: str
    steps: List[Step] = field(default_factory=list)
    succeeded: bool = False
    detected: bool = False
    stopped_reason: str = ""

    @property
    def step_count(self) -> int:
        return len(self.steps)


@dataclass
class MonteCarloRow:
    """One capability bucket of aggregated runs."""

    capability: int
    static_success_rate: float
    agent_success_rate: float
    static_detection_rate: float
    agent_detection_rate: float
    static_avg_steps: float
    agent_avg_steps: float


@dataclass
class MonteCarloResult:
    """Full capability sweep result envelope."""

    runs: int
    max_steps: int
    rows: List[MonteCarloRow]
