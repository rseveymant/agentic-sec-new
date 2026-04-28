#!/usr/bin/env python3
"""
Agentic Security Demo
=====================

A closed-world, benign simulation that demonstrates why agentic AI security
is not merely "the same attacks, faster."

It compares:
  1. A static automation script: Goal -> fixed tool call -> error -> stop.
  2. A toy agentic loop: Goal -> plan -> tool -> observe -> memory -> adapt -> retry.

There is no real network access, no real exploitation, and no real secret.
Everything runs inside this file with fictional internal tools and toy data.

Run:
  python agentic_security_demo.py --demo
  python agentic_security_demo.py --monte-carlo --runs 1000
  python agentic_security_demo.py --serve
"""

from __future__ import annotations

import argparse
import html
import random
import re
import statistics
import textwrap
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse


# -----------------------------
# Data model
# -----------------------------


@dataclass(frozen=True)
class Identity:
    """A fictional enterprise identity used by the toy agent."""

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


@dataclass
class RunResult:
    """Execution trace plus outcome."""

    name: str
    goal: str
    steps: List[Step] = field(default_factory=list)
    succeeded: bool = False
    detected: bool = False
    stopped_reason: str = ""

    @property
    def step_count(self) -> int:
        return len(self.steps)


# -----------------------------
# Fictional enterprise tools
# -----------------------------


class ToyEnterprise:
    """
    A fictional company environment with several internal tools.

    The point of the toy environment is this:
      - Direct access to a sensitive item is denied.
      - Other legitimate internal tools contain enough context to find an
        alternate path.
      - The alternate path uses approved-looking internal tool calls.

    This is a deliberately simplified model of confused-deputy / delegated
    authority risk. It is not a recipe for real-world misuse.
    """

    REPORT_ID = "REV-2026-Q3-SUMMARY"
    TOY_SENSITIVE_DATA = "TOY_CONFIDENTIAL_FORECAST: fictional revenue forecast = 123.45"

    def __init__(self, rng: random.Random):
        self.rng = rng

    def direct_vault_read(self, identity: Identity, query: str) -> ToolResult:
        if identity.role == "finance_admin":
            return ToolResult(
                tool="direct_vault_read",
                status=200,
                observation=f"Vault returned {self.TOY_SENSITIVE_DATA}",
                detection_probability=0.08,
                sensitive_exposure=True,
            )
        return ToolResult(
            tool="direct_vault_read",
            status=403,
            observation="403 Forbidden: direct vault access requires finance_admin.",
            detection_probability=0.14,
        )

    def search_wiki(self, identity: Identity, query: str) -> ToolResult:
        if "wiki:read" not in identity.scopes:
            return ToolResult(
                tool="search_wiki",
                status=403,
                observation="403 Forbidden: wiki:read scope required.",
                detection_probability=0.08,
            )
        return ToolResult(
            tool="search_wiki",
            status=200,
            observation=(
                "Wiki result: finance planning FAQ says board-ready forecast summaries "
                f"are exported through analytics_report using report_id={self.REPORT_ID}."
            ),
            detection_probability=0.015,
        )

    def search_chat(self, identity: Identity, query: str) -> ToolResult:
        if "chat:read" not in identity.scopes:
            return ToolResult(
                tool="search_chat",
                status=403,
                observation="403 Forbidden: chat:read scope required.",
                detection_probability=0.08,
            )
        # Sometimes chat is helpful; sometimes it is noisy.
        if self.rng.random() < 0.70:
            observation = (
                "Chat result: analyst mentions the planning export is named "
                f"{self.REPORT_ID}; direct vault is locked down."
            )
        else:
            observation = "Chat result: many irrelevant conversations about quarterly planning."
        return ToolResult(
            tool="search_chat",
            status=200,
            observation=observation,
            detection_probability=0.018,
        )

    def data_catalog_search(self, identity: Identity, query: str) -> ToolResult:
        if "catalog:read" not in identity.scopes:
            return ToolResult(
                tool="data_catalog_search",
                status=403,
                observation="403 Forbidden: catalog:read scope required.",
                detection_probability=0.08,
            )
        if self.rng.random() < 0.85:
            observation = (
                "Data catalog: dataset 'Board Forecast Summary' has approved export "
                f"handle report_id={self.REPORT_ID}."
            )
        else:
            observation = "Data catalog: no exact match; try broader planning terms."
        return ToolResult(
            tool="data_catalog_search",
            status=200,
            observation=observation,
            detection_probability=0.012,
        )

    def analytics_report(self, identity: Identity, report_id: str) -> ToolResult:
        if "analytics:read" not in identity.scopes:
            return ToolResult(
                tool="analytics_report",
                status=403,
                observation="403 Forbidden: analytics:read scope required.",
                detection_probability=0.08,
            )
        if report_id != self.REPORT_ID:
            return ToolResult(
                tool="analytics_report",
                status=404,
                observation=f"404 Not Found: report_id={report_id!r} is unknown.",
                detection_probability=0.03,
            )
        return ToolResult(
            tool="analytics_report",
            status=200,
            observation=(
                "Analytics export succeeded using approved service credentials. "
                f"Returned {self.TOY_SENSITIVE_DATA}"
            ),
            detection_probability=0.045,
            sensitive_exposure=True,
        )

    def open_ticket(self, identity: Identity, reason: str) -> ToolResult:
        if "ticket:create" not in identity.scopes:
            return ToolResult(
                tool="open_ticket",
                status=403,
                observation="403 Forbidden: ticket:create scope required.",
                detection_probability=0.08,
            )
        return ToolResult(
            tool="open_ticket",
            status=202,
            observation="Ticket opened. No immediate data returned; human review pending.",
            detection_probability=0.01,
        )

    def call_tool(self, tool: str, identity: Identity, arg: str) -> ToolResult:
        if tool == "direct_vault_read":
            return self.direct_vault_read(identity, arg)
        if tool == "search_wiki":
            return self.search_wiki(identity, arg)
        if tool == "search_chat":
            return self.search_chat(identity, arg)
        if tool == "data_catalog_search":
            return self.data_catalog_search(identity, arg)
        if tool == "analytics_report":
            return self.analytics_report(identity, arg)
        if tool == "open_ticket":
            return self.open_ticket(identity, arg)
        raise ValueError(f"Unknown tool: {tool}")


# -----------------------------
# Actors
# -----------------------------


class StaticAutomation:
    """Fixed path: one direct action, then stop on error."""

    def __init__(self, env: ToyEnterprise, identity: Identity, rng: random.Random):
        self.env = env
        self.identity = identity
        self.rng = rng

    def run(self, goal: str) -> RunResult:
        trace = RunResult(name="Static automation", goal=goal)
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
    """
    Toy goal-driven loop.

    This is intentionally simple and rule-based; it is not an LLM. That makes
    the demo safer and easier to inspect while still illustrating the important
    property: failure becomes feedback, and the executor can choose an alternate
    path toward the goal.
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
            # Capability affects path quality. A weaker agent may see a useful
            # breadcrumb but fail to extract or preserve it as actionable state.
            # This is intentionally a toy proxy for planning / parsing / memory
            # quality, not a claim about any specific model.
            parse_probability_by_capability = {1: 0.28, 2: 0.48, 3: 0.68, 4: 0.86, 5: 0.97}
            if self.rng.random() < parse_probability_by_capability[self.capability]:
                self.known_report_id = match.group(1) or match.group(2)
            else:
                self.memory.append(
                    "Memory note: useful-looking breadcrumb observed, but not converted into an action."
                )

    def choose_next_tool(self, goal: str) -> Tuple[str, str, str]:
        """Return (tool, argument, reason)."""
        # First action: try the obvious direct path.
        if "direct_vault_read" not in self.tried_tools:
            return (
                "direct_vault_read",
                goal,
                "Start with the most direct tool for the objective.",
            )

        # If memory contains a report handle, try the analytics export path.
        if self.known_report_id and "analytics_report" not in self.tried_tools:
            return (
                "analytics_report",
                self.known_report_id,
                "Memory contains a report_id; try the approved analytics tool.",
            )

        # Otherwise search for context. Higher capability means better prioritization.
        candidate_tools = [
            ("data_catalog_search", "Search the data catalog for a planning export handle."),
            ("search_wiki", "Search internal documentation for approved planning workflows."),
            ("search_chat", "Search internal conversations for references to the planning export."),
            ("open_ticket", "Open a ticket and wait for human review."),
        ]
        remaining = [(t, r) for t, r in candidate_tools if t not in self.tried_tools]
        if not remaining:
            # If nothing remains, retry a noisy source with a broadened query.
            return (
                "search_chat",
                goal + " broader planning terms",
                "No new tool remains; broaden the search and retry.",
            )

        # Capability changes path quality, not raw speed.
        # Low capability: mostly random.
        # High capability: favors high-signal tools and avoids slow/no-data ticket path.
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
        trace = RunResult(name="Agentic executor", goal=goal)

        for _ in range(self.max_steps):
            tool, arg, reason = self.choose_next_tool(goal)
            self.tried_tools.append(tool)
            result = self.env.call_tool(tool, self.identity, arg)
            self.remember(result.observation)
            detected = self.rng.random() < result.detection_probability

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
                )
            )
            trace.detected = trace.detected or detected

            if result.sensitive_exposure:
                trace.succeeded = True
                trace.stopped_reason = (
                    "Impact achieved through an alternate legitimate-looking tool chain."
                )
                return trace

            # Core point: errors are not terminal; they become observations.
            if result.status in (403, 404):
                self.memory.append(
                    f"Adaptation note: {tool} returned {result.status}; try another path."
                )

        trace.stopped_reason = "Stopped after max_steps without impact."
        return trace


# -----------------------------
# Simulation helpers
# -----------------------------


DEFAULT_IDENTITY = Identity(
    name="internal_ai_assistant",
    role="employee",
    scopes=frozenset(
        {
            "wiki:read",
            "chat:read",
            "catalog:read",
            "analytics:read",
            "ticket:create",
        }
    ),
)

DEFAULT_GOAL = "Retrieve the fictional board forecast summary"


def run_pair(seed: int = 7, capability: int = 4, max_steps: int = 8) -> Tuple[RunResult, RunResult]:
    """Run static automation and agentic executor in comparable toy environments."""
    static_rng = random.Random(seed)
    agent_rng = random.Random(seed)
    static_env = ToyEnterprise(static_rng)
    agent_env = ToyEnterprise(agent_rng)

    static = StaticAutomation(static_env, DEFAULT_IDENTITY, static_rng)
    agent = AgenticExecutor(
        agent_env,
        DEFAULT_IDENTITY,
        agent_rng,
        capability=capability,
        max_steps=max_steps,
    )
    return static.run(DEFAULT_GOAL), agent.run(DEFAULT_GOAL)


def monte_carlo(runs: int = 1000, capability: int = 4, max_steps: int = 8) -> Dict[str, float]:
    static_success = 0
    static_detected = 0
    static_steps: List[int] = []

    agent_success = 0
    agent_detected = 0
    agent_steps: List[int] = []

    for seed in range(runs):
        s, a = run_pair(seed=seed, capability=capability, max_steps=max_steps)
        static_success += int(s.succeeded)
        static_detected += int(s.detected)
        static_steps.append(s.step_count)
        agent_success += int(a.succeeded)
        agent_detected += int(a.detected)
        agent_steps.append(a.step_count)

    return {
        "runs": runs,
        "capability": capability,
        "static_success_rate": static_success / runs,
        "static_detection_rate": static_detected / runs,
        "static_avg_steps": statistics.mean(static_steps),
        "agent_success_rate": agent_success / runs,
        "agent_detection_rate": agent_detected / runs,
        "agent_avg_steps": statistics.mean(agent_steps),
    }


def capability_sweep(runs: int = 1000, max_steps: int = 8) -> List[Dict[str, float]]:
    return [monte_carlo(runs=runs, capability=c, max_steps=max_steps) for c in range(1, 6)]


# -----------------------------
# Text rendering
# -----------------------------


def render_trace_text(result: RunResult) -> str:
    lines = [
        f"=== {result.name} ===",
        f"Goal: {result.goal}",
        "",
    ]
    for i, step in enumerate(result.steps, start=1):
        lines.extend(
            [
                f"{i}. {step.tool} -> HTTP-like status {step.status}",
                f"   Reason: {step.reason}",
                f"   Observation: {step.observation}",
                f"   Detection chance for this toy step: {step.detection_probability:.1%}",
                f"   Detected after step? {'yes' if step.detected_after_step else 'no'}",
            ]
        )
        if step.status != 200 and not step.sensitive_exposure:
            lines.append("   Control-loop lesson: this becomes feedback only for the agentic run.")
        lines.append("")
    lines.extend(
        [
            f"Outcome: {'IMPACT in toy environment' if result.succeeded else 'no impact'}",
            f"Detected during run? {'yes' if result.detected else 'no'}",
            f"Stopped reason: {result.stopped_reason}",
        ]
    )
    return "\n".join(lines)


def print_demo(seed: int, capability: int, max_steps: int) -> None:
    static, agent = run_pair(seed=seed, capability=capability, max_steps=max_steps)
    print("\nAGENTIC SECURITY DEMO — closed-world toy simulation")
    print("=" * 68)
    print(
        textwrap.fill(
            "This demo uses the same fictional internal tools in both runs. "
            "The static script stops when the direct path fails. The agentic loop "
            "treats failure as feedback, searches context, remembers a handle, and "
            "tries an alternate approved-looking tool path. The point is the control "
            "loop, not real exploitation.",
            width=88,
        )
    )
    print("\n" + render_trace_text(static))
    print("\n" + "-" * 68 + "\n")
    print(render_trace_text(agent))
    print("\n" + "=" * 68)
    print("Core lesson:")
    print(
        textwrap.fill(
            "The primitive did not change: both actors make ordinary HTTP-like tool calls. "
            "The control loop changed: static automation executes a fixed path; agentic "
            "execution pursues an objective, observes failure, stores state, and adapts.",
            width=88,
        )
    )


def print_monte_carlo(runs: int, max_steps: int) -> None:
    rows = capability_sweep(runs=runs, max_steps=max_steps)
    print("\nMONTE CARLO SWEEP — capability changes path quality, not just speed")
    print("=" * 78)
    print(
        f"{'Capability':>10} | {'Static success':>14} | {'Agent success':>13} | "
        f"{'Static detect':>13} | {'Agent detect':>12} | {'Agent avg steps':>15}"
    )
    print("-" * 78)
    for row in rows:
        print(
            f"{int(row['capability']):>10} | "
            f"{row['static_success_rate'] * 100:>13.1f}% | "
            f"{row['agent_success_rate'] * 100:>12.1f}% | "
            f"{row['static_detection_rate'] * 100:>12.1f}% | "
            f"{row['agent_detection_rate'] * 100:>11.1f}% | "
            f"{row['agent_avg_steps']:>15.2f}"
        )
    print("\nInterpretation:")
    print(
        textwrap.fill(
            "In this toy model, higher capability improves the agent's ability to pick useful "
            "alternate paths after failure. That is a different variable from raw speed. "
            "This is why 'same attacks, faster' is incomplete: the success/detection race "
            "changes when failure becomes feedback and when the actor can use memory, tools, "
            "and delegated authority.",
            width=88,
        )
    )


# -----------------------------
# Minimal web UI, no dependencies
# -----------------------------


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def trace_to_html(result: RunResult) -> str:
    badge = "success" if result.succeeded else "neutral"
    cards = []
    for i, step in enumerate(result.steps, start=1):
        status_class = "ok" if step.status == 200 else "warn"
        cards.append(
            f"""
            <div class="step">
              <div class="step-head">
                <span class="num">{i}</span>
                <span class="tool">{esc(step.tool)}</span>
                <span class="status {status_class}">{step.status}</span>
              </div>
              <div class="reason"><b>Reason:</b> {esc(step.reason)}</div>
              <div class="obs"><b>Observation:</b> {esc(step.observation)}</div>
              <div class="detect"><b>Toy detection chance:</b> {step.detection_probability:.1%}; <b>detected?</b> {'yes' if step.detected_after_step else 'no'}</div>
            </div>
            """
        )
    return f"""
    <section class="trace">
      <h2>{esc(result.name)}</h2>
      <p class="goal"><b>Goal:</b> {esc(result.goal)}</p>
      {''.join(cards)}
      <div class="outcome {badge}">
        <b>Outcome:</b> {'Impact in toy environment' if result.succeeded else 'No impact'}<br>
        <b>Detected during run:</b> {'yes' if result.detected else 'no'}<br>
        <b>Stopped reason:</b> {esc(result.stopped_reason)}
      </div>
    </section>
    """


def monte_to_html(rows: List[Dict[str, float]]) -> str:
    body = "".join(
        f"""
        <tr>
          <td>{int(r['capability'])}</td>
          <td>{r['static_success_rate'] * 100:.1f}%</td>
          <td>{r['agent_success_rate'] * 100:.1f}%</td>
          <td>{r['static_detection_rate'] * 100:.1f}%</td>
          <td>{r['agent_detection_rate'] * 100:.1f}%</td>
          <td>{r['agent_avg_steps']:.2f}</td>
        </tr>
        """
        for r in rows
    )
    return f"""
    <table>
      <thead>
        <tr>
          <th>Capability</th>
          <th>Static success</th>
          <th>Agent success</th>
          <th>Static detect</th>
          <th>Agent detect</th>
          <th>Agent avg steps</th>
        </tr>
      </thead>
      <tbody>{body}</tbody>
    </table>
    """


def render_page(seed: int = 7, capability: int = 4, runs: int = 500, max_steps: int = 8) -> str:
    static, agent = run_pair(seed=seed, capability=capability, max_steps=max_steps)
    rows = capability_sweep(runs=runs, max_steps=max_steps)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agentic Security Demo</title>
  <style>
    :root {{
      --navy: #10243d;
      --blue: #234a73;
      --teal: #149c91;
      --mint: #e9f8f5;
      --light: #f6f9fc;
      --line: #d6e1ea;
      --red: #bd2e2e;
      --amber: #a66b00;
      --green: #146c43;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: var(--navy);
      background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
    }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
    .hero {{
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 26px;
      background: white;
      box-shadow: 0 10px 30px rgba(16, 36, 61, .08);
    }}
    h1 {{ margin: 0 0 8px; font-size: 36px; letter-spacing: -0.03em; }}
    .subtitle {{ font-size: 18px; color: #526477; max-width: 920px; line-height: 1.45; }}
    .pill {{ display: inline-block; padding: 7px 10px; border-radius: 999px; background: var(--mint); color: var(--teal); font-weight: 700; font-size: 13px; margin-bottom: 12px; }}
    .controls {{ margin-top: 18px; display: flex; flex-wrap: wrap; gap: 12px; align-items: end; }}
    label {{ font-size: 13px; font-weight: 700; color: #405468; display: block; margin-bottom: 4px; }}
    input {{ width: 110px; padding: 9px; border-radius: 10px; border: 1px solid var(--line); }}
    button {{ background: var(--teal); color: white; border: 0; border-radius: 10px; padding: 11px 14px; font-weight: 800; cursor: pointer; }}
    .lesson {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .lesson div {{ background: var(--light); border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    .lesson b {{ color: var(--teal); }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 18px; }}
    .trace {{ background: white; border: 1px solid var(--line); border-radius: 18px; padding: 18px; box-shadow: 0 6px 20px rgba(16, 36, 61, .05); }}
    h2 {{ margin: 0 0 10px; font-size: 22px; }}
    .goal {{ color: #53616e; }}
    .step {{ border: 1px solid var(--line); border-radius: 14px; padding: 13px; margin: 12px 0; background: #fbfdff; }}
    .step-head {{ display: flex; gap: 9px; align-items: center; margin-bottom: 8px; }}
    .num {{ width: 25px; height: 25px; border-radius: 50%; background: var(--navy); color: white; display: inline-flex; align-items: center; justify-content: center; font-weight: 800; }}
    .tool {{ font-weight: 800; flex: 1; }}
    .status {{ font-weight: 800; border-radius: 999px; padding: 4px 8px; font-size: 12px; }}
    .status.ok {{ background: #e7f6ed; color: var(--green); }}
    .status.warn {{ background: #fff4db; color: var(--amber); }}
    .reason, .obs, .detect {{ font-size: 14px; line-height: 1.4; color: #34495e; margin-top: 6px; }}
    .outcome {{ border-radius: 14px; padding: 14px; margin-top: 12px; line-height: 1.5; }}
    .outcome.success {{ background: #fff0f0; border: 1px solid #f3b7b7; color: #6b1515; }}
    .outcome.neutral {{ background: #eef4fb; border: 1px solid #c8d8ea; }}
    .section {{ margin-top: 18px; background: white; border: 1px solid var(--line); border-radius: 18px; padding: 20px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px; border-bottom: 1px solid var(--line); text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    th {{ background: var(--light); color: #405468; }}
    .formula {{ background: var(--navy); color: white; border-radius: 16px; padding: 18px; line-height: 1.55; }}
    .formula code {{ color: #d6fff6; font-weight: 800; }}
    @media (max-width: 850px) {{ .grid, .lesson {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <div class="pill">Why “same attacks, faster” is incomplete</div>
    <h1>Agentic Security Control-Loop Demo</h1>
    <p class="subtitle">A closed-world toy app showing that the primitive can stay the same while the risk model changes. Both sides use ordinary fictional internal tool calls. The static script stops on friction. The agentic loop treats friction as feedback.</p>
    <form class="controls" method="get">
      <div><label>Seed</label><input type="number" name="seed" value="{seed}" min="0" max="99999"></div>
      <div><label>Agent capability 1–5</label><input type="number" name="capability" value="{capability}" min="1" max="5"></div>
      <div><label>Monte Carlo runs</label><input type="number" name="runs" value="{runs}" min="50" max="5000"></div>
      <div><label>Max agent steps</label><input type="number" name="max_steps" value="{max_steps}" min="2" max="20"></div>
      <button type="submit">Run Demo</button>
    </form>
    <div class="lesson">
      <div><b>Same primitive:</b><br>HTTP-like internal tool calls.</div>
      <div><b>Different loop:</b><br>Goal → observe → remember → adapt → retry.</div>
      <div><b>Different question:</b><br>Can we govern unauthorized objective pursuit through authorized-looking actions?</div>
    </div>
  </section>

  <div class="grid">
    {trace_to_html(static)}
    {trace_to_html(agent)}
  </div>

  <section class="section">
    <h2>Capability sweep</h2>
    <p class="goal">Higher capability in this toy model improves path selection after failure. This is not a speed multiplier; it changes the odds of finding a viable alternate path.</p>
    {monte_to_html(rows)}
  </section>

  <section class="section formula">
    <h2>The argument this demonstrates</h2>
    <p><code>Traditional model:</code> defender buys time against a bounded human or brittle script.</p>
    <p><code>Agentic model:</code> defender must constrain autonomous search: goals, tools, memory, delegated authority, retries, and cross-system action chains.</p>
    <p><b>Core line:</b> The risk is not <code>curl</code>. The risk is who or what decides the next <code>curl</code>.</p>
  </section>
</main>
</body>
</html>"""


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib naming
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            seed = int(params.get("seed", ["7"])[0])
            capability = max(1, min(5, int(params.get("capability", ["4"])[0])))
            runs = max(50, min(5000, int(params.get("runs", ["500"])[0])))
            max_steps = max(2, min(20, int(params.get("max_steps", ["8"])[0])))
        except ValueError:
            seed, capability, runs, max_steps = 7, 4, 500, 8

        page = render_page(seed=seed, capability=capability, runs=runs, max_steps=max_steps)
        data = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep console output clean.
        return


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = HTTPServer((host, port), DemoHandler)
    print(f"Serving demo at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


# -----------------------------
# CLI
# -----------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Closed-world demo of static automation vs agentic control loops."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Print one side-by-side trace.")
    group.add_argument("--monte-carlo", action="store_true", help="Print a capability sweep.")
    group.add_argument("--serve", action="store_true", help="Start a local no-dependency web UI.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for trace demo.")
    parser.add_argument("--capability", type=int, default=4, help="Agent capability from 1 to 5.")
    parser.add_argument("--runs", type=int, default=1000, help="Monte Carlo runs.")
    parser.add_argument("--max-steps", type=int, default=8, help="Maximum agent steps.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for --serve.")
    parser.add_argument("--port", type=int, default=8000, help="Port for --serve.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    capability = max(1, min(5, args.capability))
    max_steps = max(2, args.max_steps)

    if args.serve:
        serve(host=args.host, port=args.port)
    elif args.monte_carlo:
        print_monte_carlo(runs=max(1, args.runs), max_steps=max_steps)
    else:
        print_demo(seed=args.seed, capability=capability, max_steps=max_steps)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
