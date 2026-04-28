#!/usr/bin/env python3
"""CLI entry point for the agentic-sec control-loop demo.

Modes:
    --demo           Print one side-by-side trace to stdout (default).
    --monte-carlo    Print a capability sweep table.
    --serve          Run the local HTTP server (Unit B).
    --build-static   Pre-render static assets (Unit B).
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from typing import Optional, Sequence

from simulator import capability_sweep, run_pair
from simulator.trace import RunResult


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
        if step.memory_after_step:
            lines.append(f"   Memory after step ({len(step.memory_after_step)} entries):")
            for note in step.memory_after_step:
                lines.append(f"     - {note}")
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
    result = capability_sweep(runs=runs, max_steps=max_steps)
    print("\nMONTE CARLO SWEEP — capability changes path quality, not just speed")
    print("=" * 78)
    print(
        f"{'Capability':>10} | {'Static success':>14} | {'Agent success':>13} | "
        f"{'Static detect':>13} | {'Agent detect':>12} | {'Agent avg steps':>15}"
    )
    print("-" * 78)
    for row in result.rows:
        print(
            f"{row.capability:>10} | "
            f"{row.static_success_rate * 100:>13.1f}% | "
            f"{row.agent_success_rate * 100:>12.1f}% | "
            f"{row.static_detection_rate * 100:>12.1f}% | "
            f"{row.agent_detection_rate * 100:>11.1f}% | "
            f"{row.agent_avg_steps:>15.2f}"
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


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Closed-world demo of static automation vs. agentic control loops."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Print one side-by-side trace.")
    group.add_argument("--monte-carlo", action="store_true", help="Print a capability sweep.")
    group.add_argument("--serve", action="store_true", help="Run the local HTTP server.")
    group.add_argument("--build-static", action="store_true", help="Pre-render static assets.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for trace demo.")
    parser.add_argument("--capability", type=int, default=4, help="Agent capability from 1 to 5.")
    parser.add_argument("--runs", type=int, default=1000, help="Monte Carlo runs.")
    parser.add_argument("--max-steps", type=int, default=8, help="Maximum agent steps.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for --serve.")
    parser.add_argument("--port", type=int, default=8000, help="Port for --serve.")
    parser.add_argument("--out", default="docs", help="Output directory for --build-static.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    capability = max(1, min(5, args.capability))
    max_steps = max(2, args.max_steps)

    if args.serve:
        from web.server import serve
        serve(host=args.host, port=args.port)
        return 0
    if args.build_static:
        import build_static
        return build_static.main(["--out", args.out])
    if args.monte_carlo:
        print_monte_carlo(runs=max(1, args.runs), max_steps=max_steps)
    else:
        print_demo(seed=args.seed, capability=capability, max_steps=max_steps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
