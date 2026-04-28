"""Capability sweep over many runs to expose the slope difference."""

from __future__ import annotations

import random
import statistics
from typing import List, Tuple

from simulator.actors import AgenticExecutor, StaticAutomation
from simulator.trace import MonteCarloResult, MonteCarloRow, RunResult
from simulator.world import DEFAULT_GOAL, DEFAULT_IDENTITY, ToyEnterprise


def run_pair(seed: int = 7, capability: int = 4, max_steps: int = 8) -> Tuple[RunResult, RunResult]:
    """Run static automation and agentic executor under the same seeded environment."""
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


def monte_carlo(runs: int = 1000, capability: int = 4, max_steps: int = 8) -> MonteCarloRow:
    """Aggregate one capability bucket across many seeds."""
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

    return MonteCarloRow(
        capability=capability,
        static_success_rate=static_success / runs,
        agent_success_rate=agent_success / runs,
        static_detection_rate=static_detected / runs,
        agent_detection_rate=agent_detected / runs,
        static_avg_steps=statistics.mean(static_steps),
        agent_avg_steps=statistics.mean(agent_steps),
    )


def capability_sweep(runs: int = 1000, max_steps: int = 8) -> MonteCarloResult:
    """Run the standard capability 1–5 sweep."""
    rows = [monte_carlo(runs=runs, capability=c, max_steps=max_steps) for c in range(1, 6)]
    return MonteCarloResult(runs=runs, max_steps=max_steps, rows=rows)
