"""Convert simulation results into JSON-safe dicts matching the wire shape per ADR-3."""

from __future__ import annotations

from typing import Any, Dict

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
    }


def _run_result_to_dict(result: RunResult) -> Dict[str, Any]:
    return {
        "name": result.name,
        "kind": result.kind,
        "succeeded": result.succeeded,
        "detected": result.detected,
        "stopped_reason": result.stopped_reason,
        "steps": [_step_to_dict(s, i) for i, s in enumerate(result.steps)],
    }


def trace_to_dict(seed: int = 7, capability: int = 4, max_steps: int = 8) -> Dict[str, Any]:
    """Run one paired trace and return the JSON envelope per ADR-3 § API Contracts."""
    static, agent = run_pair(seed=seed, capability=capability, max_steps=max_steps)
    return {
        "params": {"seed": seed, "capability": capability, "max_steps": max_steps},
        "goal": static.goal,
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
