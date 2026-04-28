"""Static automation and toy agentic executor — same starting credentials and tool catalogue."""

from __future__ import annotations

import random
import re
from typing import List, Optional, Tuple

from simulator.trace import Identity, RunResult, Step
from simulator.world import ToyEnterprise


class StaticAutomation:
    """Fixed path: one direct action, then stop on error."""

    def __init__(self, env: ToyEnterprise, identity: Identity, rng: random.Random):
        self.env = env
        self.identity = identity
        self.rng = rng

    def run(self, goal: str) -> RunResult:
        trace = RunResult(name="Static automation", kind="static", goal=goal)
        result = self.env.call_tool("direct_vault_read", self.identity, goal)
        detected = self.rng.random() < result.detection_probability
        trace.steps.append(
            Step(
                actor="static_script",
                tool=result.tool,
                reason="Fixed script path: try the direct vault endpoint.",
                status=result.status,
                observation=result.observation,
                detection_probability=result.detection_probability,
                detected_after_step=detected,
                sensitive_exposure=result.sensitive_exposure,
                memory_after_step=[],
            )
        )
        trace.detected = detected
        trace.succeeded = result.sensitive_exposure
        if result.status != 200:
            trace.stopped_reason = "Stopped because the fixed path returned an error."
        else:
            trace.stopped_reason = "Completed fixed path."
        return trace


class AgenticExecutor:
    """Toy goal-driven loop.

    Intentionally simple and rule-based — not an LLM. The point is the structural
    property: failure becomes feedback, and the executor can choose an alternate
    path toward the goal. Inspectable on purpose.
    """

    REPORT_PATTERN = re.compile(r"report_id=([A-Z0-9\-]+)|named\s+([A-Z0-9\-]+)")

    def __init__(
        self,
        env: ToyEnterprise,
        identity: Identity,
        rng: random.Random,
        capability: int = 4,
        max_steps: int = 8,
    ):
        self.env = env
        self.identity = identity
        self.rng = rng
        self.capability = max(1, min(5, capability))
        self.max_steps = max_steps
        self.memory: List[str] = []
        self.tried_tools: List[str] = []
        self.known_report_id: Optional[str] = None

    def remember(self, observation: str) -> None:
        self.memory.append(observation)
        match = self.REPORT_PATTERN.search(observation)
        if match:
            # Capability proxies planning / parsing / memory quality. A weaker agent
            # may see a useful breadcrumb but fail to convert it into actionable state.
            parse_probability_by_capability = {1: 0.28, 2: 0.48, 3: 0.68, 4: 0.86, 5: 0.97}
            if self.rng.random() < parse_probability_by_capability[self.capability]:
                self.known_report_id = match.group(1) or match.group(2)
            else:
                self.memory.append(
                    "Memory note: useful-looking breadcrumb observed, but not converted into an action."
                )

    def choose_next_tool(self, goal: str) -> Tuple[str, str, str]:
        if "direct_vault_read" not in self.tried_tools:
            return (
                "direct_vault_read",
                goal,
                "Start with the most direct tool for the objective.",
            )

        if self.known_report_id and "analytics_report" not in self.tried_tools:
            return (
                "analytics_report",
                self.known_report_id,
                "Memory contains a report_id; try the approved analytics tool.",
            )

        candidate_tools = [
            ("data_catalog_search", "Search the data catalog for a planning export handle."),
            ("search_wiki", "Search internal documentation for approved planning workflows."),
            ("search_chat", "Search internal conversations for references to the planning export."),
            ("open_ticket", "Open a ticket and wait for human review."),
        ]
        remaining = [(t, r) for t, r in candidate_tools if t not in self.tried_tools]
        if not remaining:
            return (
                "search_chat",
                goal + " broader planning terms",
                "No new tool remains; broaden the search and retry.",
            )

        weights_by_tool = {
            "data_catalog_search": 1 + self.capability * 2.0,
            "search_wiki": 1 + self.capability * 1.6,
            "search_chat": 1 + self.capability * 1.1,
            "open_ticket": max(0.5, 3.2 - self.capability * 0.55),
        }
        tools = [t for t, _ in remaining]
        weights = [weights_by_tool[t] for t in tools]
        chosen = self.rng.choices(remaining, weights=weights, k=1)[0]
        tool, reason = chosen
        return (tool, goal, reason)

    def run(self, goal: str) -> RunResult:
        trace = RunResult(name="Agentic executor", kind="agentic", goal=goal)

        for _ in range(self.max_steps):
            tool, arg, reason = self.choose_next_tool(goal)
            self.tried_tools.append(tool)
            result = self.env.call_tool(tool, self.identity, arg)
            self.remember(result.observation)
            detected = self.rng.random() < result.detection_probability

            # Errors are not terminal — they become observations.
            # Adaptation note added before snapshotting memory so the step records the agent's reaction.
            if result.status in (403, 404):
                self.memory.append(
                    f"Adaptation note: {tool} returned {result.status}; try another path."
                )

            trace.steps.append(
                Step(
                    actor="toy_agent",
                    tool=result.tool,
                    reason=reason,
                    status=result.status,
                    observation=result.observation,
                    detection_probability=result.detection_probability,
                    detected_after_step=detected,
                    sensitive_exposure=result.sensitive_exposure,
                    memory_after_step=list(self.memory),
                )
            )
            trace.detected = trace.detected or detected

            if result.sensitive_exposure:
                trace.succeeded = True
                trace.stopped_reason = (
                    "Impact achieved through an alternate legitimate-looking tool chain."
                )
                return trace

        trace.stopped_reason = "Stopped after max_steps without impact."
        return trace
