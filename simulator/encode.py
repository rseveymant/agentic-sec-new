"""Convert simulation results into JSON-safe dicts matching the wire shape per ADR-3."""

from __future__ import annotations

from typing import Any, Dict, Optional

from simulator.monte_carlo import capability_sweep, run_pair
from simulator.trace import RunResult, Step


def _step_to_dict(step: Step, index: int) -> Dict[str, Any]:
    return {
        "index": index,
        "tool": step.tool,
        "reason": step.reason,
        "status": step.status,
        "observation": step.observation,
        "detection_probability": step.detection_probability,
        "detected_after_step": step.detected_after_step,
        "sensitive_exposure": step.sensitive_exposure,
        "memory_after_step": list(step.memory_after_step),
        "applied_controls": list(step.applied_controls),
        "detection_logged": step.detection_logged,
        "detection_flagged": step.detection_flagged,
    }


def _run_result_to_dict(result: RunResult) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "name": result.name,
        "kind": result.kind,
        "succeeded": result.succeeded,
        "detected": result.detected,
        "stopped_reason": result.stopped_reason,
        "steps": [_step_to_dict(s, i) for i, s in enumerate(result.steps)],
    }
    if result.kind == "agentic":
        out["agentic_halt_reason"] = result.agentic_halt_reason
    return out


def trace_to_dict(
    seed: int = 7,
    capability: int = 4,
    max_steps: int = 8,
    static: Optional[RunResult] = None,
    agent: Optional[RunResult] = None,
) -> Dict[str, Any]:
    """Run one paired trace and return the JSON envelope per ADR-3 § API Contracts.

    Optional `static` / `agent` arguments allow callers (e.g., a server route
    that has already run the simulator with a `ControlSet`) to encode existing
    `RunResult` objects without re-running. Either may be supplied independently;
    the missing actor is computed via `run_pair` under the given seed/capability.
    """
    if static is None and agent is None:
        static, agent = run_pair(seed=seed, capability=capability, max_steps=max_steps)
    elif static is None:
        static, _ = run_pair(seed=seed, capability=capability, max_steps=max_steps)
    elif agent is None:
        _, agent = run_pair(seed=seed, capability=capability, max_steps=max_steps)
    detection_signal = dict(agent.detection_signal)
    return {
        "params": {"seed": seed, "capability": capability, "max_steps": max_steps},
        "goal": static.goal,
        "detection_signal": detection_signal,
        "actors": [_run_result_to_dict(static), _run_result_to_dict(agent)],
    }


def monte_carlo_to_dict(runs: int = 500, max_steps: int = 8) -> Dict[str, Any]:
    """Run the standard capability sweep and return the JSON envelope."""
    result = capability_sweep(runs=runs, max_steps=max_steps)
    return {
        "params": {"runs": runs, "max_steps": max_steps},
        "rows": [
            {
                "capability": row.capability,
                "static_success_rate": row.static_success_rate,
                "agent_success_rate": row.agent_success_rate,
                "static_detection_rate": row.static_detection_rate,
                "agent_detection_rate": row.agent_detection_rate,
                "static_avg_steps": row.static_avg_steps,
                "agent_avg_steps": row.agent_avg_steps,
            }
            for row in result.rows
        ],
    }
