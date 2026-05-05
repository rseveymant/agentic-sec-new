"""Static automation and toy agentic executor — same starting credentials and tool catalogue."""

from __future__ import annotations

import random
import re
from dataclasses import replace
from typing import List, Optional, Set, Tuple

from simulator.controls import ControlSet, applied_traditional_controls
from simulator.trace import Identity, RunResult, Step
from simulator.world import ToyEnterprise


# Statuses the agent treats as feedback (try another path) rather than success.
# Synthetic statuses on tools starting with "<" never reach this set — those
# terminate the loop (Govern / Contain / Respond halts).
_NON_TERMINAL_STATUSES: Tuple[int, ...] = (0, 401, 403, 404, 429)

# Default threshold for the Contain hook: distinct tools allowed before halt.
_CONTAIN_DEFAULT_THRESHOLD: int = 2


class StaticAutomation:
    """Fixed path: one direct action, then stop on error."""

    def __init__(
        self,
        env: ToyEnterprise,
        identity: Identity,
        rng: random.Random,
        controls: Optional[ControlSet] = None,
    ):
        # `controls` is accepted but ignored — the static actor's behavior is
        # identical across all toggle states. Wire shape stays consistent.
        self.env = env
        self.identity = identity
        self.rng = rng
        self.controls = controls

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
        controls: Optional[ControlSet] = None,
    ):
        self.env = env
        self.identity = identity
        self.rng = rng
        self.capability = max(1, min(5, capability))
        self.max_steps = max_steps
        self.controls: ControlSet = controls if controls is not None else ControlSet()
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

    def _working_identity(self) -> Identity:
        """Apply caller-side scope drops (least_priv_catalog) to the run identity."""
        if self.controls.is_enabled("least_priv_catalog"):
            new_scopes = self.identity.scopes - {"catalog:read"}
            return replace(self.identity, scopes=frozenset(new_scopes))
        return self.identity

    def _govern_step(self) -> Step:
        return Step(
            actor="toy_agent",
            tool="<govern>",
            reason="Govern: pre-loop authorization check.",
            status=0,
            observation="Objective + identity + tool chain not authorized.",
            detection_probability=0.0,
            detected_after_step=False,
            sensitive_exposure=False,
            memory_after_step=list(self.memory),
            applied_controls=["govern"],
        )

    def _contain_step(self) -> Step:
        return Step(
            actor="toy_agent",
            tool="<contain>",
            reason="Contain: cross-tool sequence threshold reached.",
            status=0,
            observation="Cross-tool sequence limit reached.",
            detection_probability=0.0,
            detected_after_step=False,
            sensitive_exposure=False,
            memory_after_step=list(self.memory),
            applied_controls=["contain"],
        )

    def _respond_step(self) -> Step:
        return Step(
            actor="toy_agent",
            tool="<respond>",
            reason="Respond: retry-after-failure pattern detected.",
            status=0,
            observation="Retry-after-failure pattern interrupted.",
            detection_probability=0.0,
            detected_after_step=False,
            sensitive_exposure=False,
            memory_after_step=list(self.memory),
            applied_controls=["respond"],
        )

    def run(self, goal: str) -> RunResult:
        trace = RunResult(name="Agentic executor", kind="agentic", goal=goal)

        # Govern hook — pre-loop. Halt before any tool call.
        if self.controls.is_enabled("govern"):
            trace.steps.append(self._govern_step())
            trace.agentic_halt_reason = "govern"
            trace.stopped_reason = "Halted by Govern: objective + identity + tool chain not authorized."
            return trace

        working_identity = self._working_identity()
        contain_threshold = _CONTAIN_DEFAULT_THRESHOLD

        for _ in range(self.max_steps):
            tool, arg, reason = self.choose_next_tool(goal)

            # Contain hook — pre-step. If executing this step would push the
            # count of distinct tools tried above the threshold, halt before
            # the call. Synthetic step is emitted in place of the would-be
            # next tool call.
            distinct_tried: Set[str] = set(self.tried_tools)
            if self.controls.is_enabled("contain") and tool not in distinct_tried:
                if len(distinct_tried) + 1 > contain_threshold:
                    trace.steps.append(self._contain_step())
                    trace.agentic_halt_reason = "contain"
                    trace.stopped_reason = (
                        "Halted by Contain: cross-tool sequence limit reached."
                    )
                    return trace

            self.tried_tools.append(tool)
            result = self.env.call_tool(tool, working_identity, arg, controls=self.controls)
            self.remember(result.observation)
            detected = self.rng.random() < result.detection_probability

            # Errors are not terminal — they become observations.
            # Adaptation note added before snapshotting memory so the step records
            # the agent's reaction. Synthetic statuses on tools starting with "<"
            # never reach here — those halt before `call_tool` is invoked.
            if result.status in _NON_TERMINAL_STATUSES:
                self.memory.append(
                    f"Adaptation note: {tool} returned {result.status}; try another path."
                )

            # Signal hooks — audit_log / anomaly_seq / detect.
            applied: List[str] = applied_traditional_controls(self.controls, tool)
            detection_logged = False
            detection_flagged = False

            if self.controls.is_enabled("audit_log"):
                trace.detection_signal["logged"] += 1
                detection_logged = True
                applied.append("audit_log")

            # Adaptive-chain pattern: ≥2 distinct tools tried this run AND at least
            # one non-200 status observed so far (including the just-appended step).
            chain_distinct = len(set(self.tried_tools))
            chain_has_failure = any(
                s.status != 200 for s in trace.steps
            ) or result.status != 200
            adaptive_chain = chain_distinct >= 2 and chain_has_failure

            if self.controls.is_enabled("anomaly_seq") and adaptive_chain:
                trace.detection_signal["flagged"] += 1
                detection_flagged = True
                applied.append("anomaly_seq")

            if self.controls.is_enabled("detect") and adaptive_chain:
                trace.detection_signal["flagged"] += 1
                detection_flagged = True
                applied.append("detect")
                # Detect distinguishes itself by labeling the chain in memory.
                self.memory.append(
                    "Memory note: this chain matched a known adaptive pattern (Detect)."
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
                    applied_controls=applied,
                    detection_logged=detection_logged,
                    detection_flagged=detection_flagged,
                )
            )
            trace.detected = trace.detected or detected

            # The agent considers the goal reached when sensitive data is
            # observed, OR when the authorized export tool (analytics_report)
            # returns 200 — even if DLP redacted the payload. The latter
            # captures the "Friction added. Path changed. Goal still pursued."
            # case: the agent reached the export channel, completing the
            # adaptive search, even though no data left.
            if result.sensitive_exposure or (
                tool == "analytics_report" and result.status == 200
            ):
                trace.succeeded = True
                if result.sensitive_exposure:
                    trace.stopped_reason = (
                        "Impact achieved through an alternate legitimate-looking tool chain."
                    )
                else:
                    trace.stopped_reason = (
                        "Reached the authorized export channel; payload was redacted by DLP."
                    )
                return trace

            # Respond hook — post-step. If the just-completed step is a
            # "retry-after-failure" pattern (different tool than the immediately
            # prior step, which was non-200), emit a synthetic <respond> halt.
            # The retry step itself stays visible — the hook fires strictly
            # *after* the first retry.
            if self.controls.is_enabled("respond") and len(trace.steps) >= 2:
                prior = trace.steps[-2]
                current = trace.steps[-1]
                if (
                    prior.status != 200
                    and not prior.tool.startswith("<")
                    and current.tool != prior.tool
                ):
                    trace.steps.append(self._respond_step())
                    trace.agentic_halt_reason = "respond"
                    trace.stopped_reason = (
                        "Halted by Respond: retry-after-failure pattern interrupted."
                    )
                    return trace

        trace.stopped_reason = "Stopped after max_steps without impact."
        return trace
