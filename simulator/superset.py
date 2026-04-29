"""Superset trace catalog for the static GitHub Pages deploy (ADR-7-3, ADR-7-7).

Enumerates all 2^12 = 4096 control toggle combinations under canonical
seed/capability/max_steps, runs the simulator on each, deduplicates resulting
agent traces by JSON shape, and emits a `SupersetCatalog`. Bisection enforces
the ~150 KB gzipped size budget; dropped combinations are recorded in
`fallback_combinations` so the JS overlay can show a "run live" note.

The static actor's behavior is identical across all toggle states (it ignores
the `ControlSet` entirely), so a single `static_actor_trace_dict` is stored
once and shared across the catalog.
"""

from __future__ import annotations

import gzip
import json
import random
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple

from simulator.actors import AgenticExecutor, StaticAutomation
from simulator.controls import (
    AGENTIC_CONTROLS,
    TRADITIONAL_CONTROLS,
    ControlSet,
)
from simulator.encode import trace_to_dict
from simulator.trace import RunResult
from simulator.world import DEFAULT_GOAL, DEFAULT_IDENTITY, ToyEnterprise

from dataclasses import replace as dc_replace


SIZE_BUDGET_BYTES: int = 150 * 1024  # gzipped


@dataclass
class CatalogEntry:
    """One unique agent trace, plus the (tc, ac) combinations that produce it."""

    id: int
    covers: List[Tuple[FrozenSet[str], FrozenSet[str]]]
    trace_dict: dict
    detection_signal: Dict[str, int]


@dataclass
class SupersetCatalog:
    """All unique agent paths under canonical seed/capability/max_steps."""

    params: dict
    static_actor_trace_dict: dict
    agent_traces: List[CatalogEntry] = field(default_factory=list)
    fallback_combinations: List[Tuple[FrozenSet[str], FrozenSet[str]]] = field(
        default_factory=list
    )


def _build_working_identity(controls: ControlSet):
    """Per-run working identity: drop catalog:read when least_priv_catalog is on."""
    if controls.is_enabled("least_priv_catalog"):
        return dc_replace(
            DEFAULT_IDENTITY,
            scopes=frozenset(DEFAULT_IDENTITY.scopes - {"catalog:read"}),
        )
    return DEFAULT_IDENTITY


def _run_agent(
    seed: int,
    capability: int,
    max_steps: int,
    controls: ControlSet,
) -> RunResult:
    """Run AgenticExecutor once with a fresh RNG and the given ControlSet."""
    rng = random.Random(seed)
    env = ToyEnterprise(rng)
    identity = _build_working_identity(controls)
    actor = AgenticExecutor(
        env,
        identity,
        rng,
        capability=capability,
        max_steps=max_steps,
        controls=controls,
    )
    return actor.run(DEFAULT_GOAL)


def _run_static(seed: int) -> RunResult:
    """Run StaticAutomation once with a fresh RNG. Controls are no-ops here."""
    rng = random.Random(seed)
    env = ToyEnterprise(rng)
    actor = StaticAutomation(env, DEFAULT_IDENTITY, rng)
    return actor.run(DEFAULT_GOAL)


def _encode_pair(static_result: RunResult, agent_result: RunResult, params: dict) -> Tuple[dict, dict]:
    """Run encode.trace_to_dict on already-computed actors; return (static, agent) dicts.

    `trace_to_dict` is the public encoder. We call it with both actors supplied so
    nothing is re-run, then split out each actor's dict. The agent dict gets a
    `detection_signal` field merged in (encoded under the envelope-level signal,
    not per-actor — but the catalog wants it per-entry).
    """
    envelope = trace_to_dict(
        seed=params["seed"],
        capability=params["capability"],
        max_steps=params["max_steps"],
        static=static_result,
        agent=agent_result,
    )
    actors = envelope["actors"]
    static_dict = next(a for a in actors if a["kind"] == "static")
    agent_dict = next(a for a in actors if a["kind"] == "agentic")
    agent_dict = dict(agent_dict)
    agent_dict["detection_signal"] = dict(agent_result.detection_signal)
    return static_dict, agent_dict


def _shape_signature(trace_dict: dict) -> str:
    """Stable JSON serialization of just the agent's trace shape (for dedup).

    Excludes any envelope fluff; the trace dict from `_agent_trace_dict` is
    already a per-actor shape that includes `agentic_halt_reason`,
    `succeeded`, `detected`, `stopped_reason`, `steps`, `detection_signal`.
    """
    return json.dumps(trace_dict, sort_keys=True)


def _all_subsets(items: Iterable) -> List[FrozenSet[str]]:
    """All subsets of an iterable, returned as frozensets. 2^N entries."""
    pool = tuple(items)
    out: List[FrozenSet[str]] = []
    for r in range(len(pool) + 1):
        for combo in combinations(pool, r):
            out.append(frozenset(combo))
    return out


def _interesting_subsets() -> set:
    """The "interesting" (tc, ac) pairs the bisection rule preserves.

    Defined per ADR-7-3:
      - All single-toggle states: one tc with empty ac, OR one ac with empty tc.
      - All-traditional + zero-agentic.
      - Zero-traditional + all-agentic.
      - Every (single tc) x (single ac) pair = 32 states.
      - The empty-empty (no controls) state.

    Returns a set of (frozenset[str], frozenset[str]) pairs.
    """
    tc_ids = [c.id for c in TRADITIONAL_CONTROLS]
    ac_ids = [c.id for c in AGENTIC_CONTROLS]

    out: set = set()
    # No controls at all.
    out.add((frozenset(), frozenset()))
    # Single tc only.
    for cid in tc_ids:
        out.add((frozenset({cid}), frozenset()))
    # Single ac only.
    for cid in ac_ids:
        out.add((frozenset(), frozenset({cid})))
    # Single-tc x single-ac pairs.
    for t in tc_ids:
        for a in ac_ids:
            out.add((frozenset({t}), frozenset({a})))
    # All traditional + 0 agentic.
    out.add((frozenset(tc_ids), frozenset()))
    # 0 traditional + all agentic.
    out.add((frozenset(), frozenset(ac_ids)))
    return out


def _serialize_for_size(catalog: SupersetCatalog) -> bytes:
    """Serialize the catalog to JSON bytes for size measurement."""
    return json.dumps(serialize_catalog(catalog), sort_keys=False).encode("utf-8")


def _gzipped_size(catalog: SupersetCatalog) -> int:
    return len(gzip.compress(_serialize_for_size(catalog)))


def build_catalog(
    seed: int = 7,
    capability: int = 4,
    max_steps: int = 8,
) -> SupersetCatalog:
    """Enumerate all 4096 toggle combinations and dedupe by agent trace shape.

    Prints a single summary line to stdout: ``unique paths: N | gzipped size: K KB | fallbacks: F``.
    """
    tc_ids = [c.id for c in TRADITIONAL_CONTROLS]
    ac_ids = [c.id for c in AGENTIC_CONTROLS]
    tc_subsets = _all_subsets(tc_ids)
    ac_subsets = _all_subsets(ac_ids)

    encode_params = {"seed": seed, "capability": capability, "max_steps": max_steps}

    # Static trace is identical across all toggle states — encode it once.
    static_result = _run_static(seed)
    # Use a no-op controls run to get the static dict via the public encoder.
    placeholder_agent = _run_agent(seed, capability, max_steps, ControlSet())
    static_dict, _ = _encode_pair(static_result, placeholder_agent, encode_params)

    # Map shape signature → CatalogEntry. Order of insertion preserved.
    by_signature: Dict[str, CatalogEntry] = {}
    next_id = 0
    for tc_set in tc_subsets:
        for ac_set in ac_subsets:
            controls = ControlSet(enabled=frozenset(tc_set | ac_set))
            agent_result = _run_agent(seed, capability, max_steps, controls)
            _, agent_dict = _encode_pair(static_result, agent_result, encode_params)
            sig = _shape_signature(agent_dict)
            entry = by_signature.get(sig)
            if entry is None:
                entry = CatalogEntry(
                    id=next_id,
                    covers=[(tc_set, ac_set)],
                    trace_dict=agent_dict,
                    detection_signal=dict(agent_result.detection_signal),
                )
                by_signature[sig] = entry
                next_id += 1
            else:
                entry.covers.append((tc_set, ac_set))

    # Sort each entry's covers list canonically: by sorted(tc) then sorted(ac).
    for entry in by_signature.values():
        entry.covers.sort(key=lambda p: (sorted(p[0]), sorted(p[1])))

    catalog = SupersetCatalog(
        params={"seed": seed, "capability": capability, "max_steps": max_steps},
        static_actor_trace_dict=static_dict,
        agent_traces=list(by_signature.values()),
        fallback_combinations=[],
    )

    # Bisection: enforce ~150 KB gzipped budget.
    interesting = _interesting_subsets()

    def covers_only_uninteresting(entry: CatalogEntry) -> bool:
        return all(pair not in interesting for pair in entry.covers)

    if _gzipped_size(catalog) > SIZE_BUDGET_BYTES:
        # Pass 1: drop entries whose covers are entirely outside the
        # interesting subsets. Move their pairs to fallback_combinations.
        kept: List[CatalogEntry] = []
        for entry in catalog.agent_traces:
            if covers_only_uninteresting(entry):
                catalog.fallback_combinations.extend(entry.covers)
            else:
                kept.append(entry)
        catalog.agent_traces = kept

    if _gzipped_size(catalog) > SIZE_BUDGET_BYTES:
        # Pass 2: iteratively drop the entry with the smallest covers count
        # whose covers contain at least one uninteresting overlap. Stop when
        # under budget or only "fully interesting" entries remain.
        while _gzipped_size(catalog) > SIZE_BUDGET_BYTES:
            # Candidates: entries with at least one uninteresting cover.
            candidates = [
                e
                for e in catalog.agent_traces
                if any(p not in interesting for p in e.covers)
            ]
            if not candidates:
                break
            # Drop the candidate with the smallest covers count (least valuable).
            victim = min(candidates, key=lambda e: len(e.covers))
            catalog.fallback_combinations.extend(victim.covers)
            catalog.agent_traces = [e for e in catalog.agent_traces if e is not victim]

    # Deterministic ordering for fallback_combinations (sorted-csv key).
    catalog.fallback_combinations.sort(
        key=lambda p: (sorted(p[0]), sorted(p[1]))
    )

    raw_size = len(_serialize_for_size(catalog))
    gz_size = _gzipped_size(catalog)
    print(
        f"unique paths: {len(catalog.agent_traces)} | "
        f"gzipped size: {gz_size // 1024} KB | "
        f"fallbacks: {len(catalog.fallback_combinations)}"
    )
    # Stash raw size for any caller that wants it without re-serializing.
    catalog.params = {**catalog.params, "_raw_size": raw_size, "_gzipped_size": gz_size}
    return catalog


def serialize_catalog(catalog: SupersetCatalog) -> dict:
    """Convert a SupersetCatalog to a JSON-friendly dict (ADR-7-7 wire shape).

    `covers` and `fallback_combinations` are emitted as ``{"tc": [...], "ac": [...]}``
    objects with sorted ID lists.
    """
    # Strip private size annotations from params before emitting.
    public_params = {k: v for k, v in catalog.params.items() if not k.startswith("_")}

    def pair_to_dict(pair: Tuple[FrozenSet[str], FrozenSet[str]]) -> dict:
        tc_set, ac_set = pair
        return {"tc": sorted(tc_set), "ac": sorted(ac_set)}

    out_traces = []
    for entry in catalog.agent_traces:
        out_traces.append(
            {
                "id": entry.id,
                "covers": [pair_to_dict(p) for p in entry.covers],
                "trace": entry.trace_dict,
                "detection_signal": dict(entry.detection_signal),
            }
        )
    return {
        "params": public_params,
        "static_actor_trace": catalog.static_actor_trace_dict,
        "agent_traces": out_traces,
        "fallback_combinations": [
            pair_to_dict(p) for p in catalog.fallback_combinations
        ],
    }


def _canonical_key(tc: Iterable[str], ac: Iterable[str]) -> str:
    """Match `ControlSet.key()` exactly: ``tc=<sorted,csv>;ac=<sorted,csv>``."""
    return f"tc={','.join(sorted(tc))};ac={','.join(sorted(ac))}"


def _find_entry_for(
    catalog: SupersetCatalog,
    tc: List[str],
    ac: List[str],
) -> Optional[CatalogEntry]:
    """Find the CatalogEntry whose `covers` list contains the given pair."""
    target = (frozenset(tc), frozenset(ac))
    for entry in catalog.agent_traces:
        for pair in entry.covers:
            if pair == target:
                return entry
    return None


def _diff_hint(expected: dict, actual: dict) -> str:
    """Short hint pointing at the first divergence between two trace dicts."""
    e_steps = expected.get("steps", [])
    a_steps = actual.get("steps", [])
    if len(e_steps) != len(a_steps):
        return f"step count: catalog={len(e_steps)} live={len(a_steps)}"
    for i, (es, as_) in enumerate(zip(e_steps, a_steps)):
        for key in ("tool", "status", "applied_controls", "observation"):
            if es.get(key) != as_.get(key):
                return f"step[{i}].{key}: catalog={es.get(key)!r} live={as_.get(key)!r}"
    if expected.get("agentic_halt_reason") != actual.get("agentic_halt_reason"):
        return (
            f"agentic_halt_reason: catalog={expected.get('agentic_halt_reason')!r} "
            f"live={actual.get('agentic_halt_reason')!r}"
        )
    return "shape signatures differ but field-wise diff did not localize"


def verify_catalog(
    catalog: SupersetCatalog,
    sample_combinations: List[Tuple[List[str], List[str]]],
) -> None:
    """Drift guard: re-run sampled combinations and assert the catalog matches.

    For each sample, look up the entry by `(tc, ac)` membership, re-run the
    agent on the same combination under the catalog's canonical seed, and
    compare the resulting trace dict to the catalog entry's `trace_dict`.

    Raises `AssertionError` with a useful diff hint on mismatch.
    """
    seed = catalog.params.get("seed", 7)
    capability = catalog.params.get("capability", 4)
    max_steps = catalog.params.get("max_steps", 8)
    fallback_set = {(p[0], p[1]) for p in catalog.fallback_combinations}

    for tc_list, ac_list in sample_combinations:
        tc_set = frozenset(tc_list)
        ac_set = frozenset(ac_list)
        key = _canonical_key(tc_list, ac_list)

        if (tc_set, ac_set) in fallback_set:
            # Sampled a fallback combination — skip drift check; the JS
            # overlay handles these by routing to the live demo.
            continue

        entry = _find_entry_for(catalog, list(tc_set), list(ac_set))
        assert entry is not None, (
            f"verify_catalog: no entry covers key {key!r}; "
            f"check enumeration completeness"
        )

        controls = ControlSet(enabled=frozenset(tc_set | ac_set))
        live_result = _run_agent(seed, capability, max_steps, controls)
        encode_params = {"seed": seed, "capability": capability, "max_steps": max_steps}
        # Static is identical across combos; pull a fresh static result for encoding.
        static_result = _run_static(seed)
        _, live_dict = _encode_pair(static_result, live_result, encode_params)

        if _shape_signature(live_dict) != _shape_signature(entry.trace_dict):
            hint = _diff_hint(entry.trace_dict, live_dict)
            raise AssertionError(
                f"verify_catalog drift for {key!r}: {hint}"
            )
