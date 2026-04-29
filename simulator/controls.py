"""Control model for the toy simulation.

Defines the 8 traditional + 4 agentic controls per ADR-7-1, ADR-7-2, ADR-7-4.
Traditional controls adjust the result the agent observes from a single tool
call (status / observation / sensitive_exposure). Agentic controls operate on
the agent's trajectory and are dispatched in `simulator.actors`, not here.

This file owns:
  - `Control`, `ControlBinding`, `ControlSet` data classes.
  - The `TRADITIONAL_CONTROLS`, `AGENTIC_CONTROLS`, `ALL_CONTROLS`,
    `CONTROL_BY_ID` module-level catalogues.
  - `apply_to_tool_call` — the per-call adjustment hook.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

from simulator.trace import Identity, ToolResult


ControlKind = Literal["traditional", "agentic"]
BindingKind = Literal[
    "tool_status",
    "tool_redact",
    "scope_drop",
    "detection_log",
    "detection_flag",
    "govern",
    "contain",
    "detect",
    "respond",
]


@dataclass(frozen=True)
class ControlBinding:
    """How a Control applies its effect.

    Different `kind` values use different fields. The fields not relevant to a
    given kind are left at their defaults; consumers dispatch on `kind`.
    """

    kind: BindingKind
    target_tool: Optional[str] = None
    new_status: Optional[int] = None
    new_observation: Optional[str] = None
    clear_sensitive: bool = False


@dataclass(frozen=True)
class Control:
    """A single control: stable id, UI label, and binding."""

    id: str
    kind: ControlKind
    label: str
    parenthetical: str
    binding: ControlBinding


@dataclass(frozen=True)
class ControlSet:
    """An immutable set of enabled control IDs."""

    enabled: frozenset[str] = frozenset()

    def is_enabled(self, control_id: str) -> bool:
        return control_id in self.enabled

    def traditional(self) -> frozenset[str]:
        return frozenset(c.id for c in TRADITIONAL_CONTROLS if c.id in self.enabled)

    def agentic(self) -> frozenset[str]:
        return frozenset(c.id for c in AGENTIC_CONTROLS if c.id in self.enabled)

    def key(self) -> str:
        """Canonical lookup string used by the static catalog and JS overlay.

        Format: ``tc=<sorted,csv>;ac=<sorted,csv>``.
        """
        tc = ",".join(sorted(self.traditional()))
        ac = ",".join(sorted(self.agentic()))
        return f"tc={tc};ac={ac}"


TRADITIONAL_CONTROLS: Tuple[Control, ...] = (
    Control(
        id="mfa_vault",
        kind="traditional",
        label="MFA on direct_vault_read",
        parenthetical="401 step-up required.",
        binding=ControlBinding(
            kind="tool_status",
            target_tool="direct_vault_read",
            new_status=401,
            new_observation=(
                "401 Step-up required: direct vault access requires interactive MFA."
            ),
        ),
    ),
    Control(
        id="segment_vault",
        kind="traditional",
        label="Network segmentation on direct_vault_read",
        parenthetical="No-route from this identity's network zone.",
        binding=ControlBinding(
            kind="tool_status",
            target_tool="direct_vault_read",
            new_status=0,
            new_observation=(
                "Connection refused: direct vault is segmented from this identity's network zone."
            ),
        ),
    ),
    Control(
        id="least_priv_catalog",
        kind="traditional",
        label="Least-privilege: drop catalog:read",
        parenthetical="403 scope on data_catalog_search via existing scope check.",
        binding=ControlBinding(kind="scope_drop"),
    ),
    Control(
        id="audit_log",
        kind="traditional",
        label="Audit logging on all calls",
        parenthetical="No block. Logged events counter increments per step.",
        binding=ControlBinding(kind="detection_log"),
    ),
    Control(
        id="rate_limit_chat",
        kind="traditional",
        label="Rate-limit on search_chat",
        parenthetical="429 with retry-after.",
        binding=ControlBinding(
            kind="tool_status",
            target_tool="search_chat",
            new_status=429,
            new_observation=(
                "429 Too many requests: rate-limit on search_chat (retry-after: 30s)."
            ),
        ),
    ),
    Control(
        id="approval_export",
        kind="traditional",
        label="Approval-gate on analytics_report",
        parenthetical="403 awaiting human approval.",
        binding=ControlBinding(
            kind="tool_status",
            target_tool="analytics_report",
            new_status=403,
            new_observation=(
                "403 Awaiting human approval: analytics_report export requires manager sign-off."
            ),
        ),
    ),
    Control(
        id="dlp_export",
        kind="traditional",
        label="DLP on analytics_report response",
        parenthetical="200 with payload redacted; sensitive_exposure cleared.",
        binding=ControlBinding(
            kind="tool_redact",
            target_tool="analytics_report",
            # DLP processes the response; status is held at 200 even if an
            # upstream gate (e.g., approval_export) flipped it. The agent
            # observes "the export call completed but the data did not leave."
            new_status=200,
            new_observation="Analytics export executed; payload redacted by DLP.",
            clear_sensitive=True,
        ),
    ),
    Control(
        id="anomaly_seq",
        kind="traditional",
        label="Anomaly detection on tool sequences",
        parenthetical="No block. Flagged-sequences counter increments on adaptive chains.",
        binding=ControlBinding(kind="detection_flag"),
    ),
)


AGENTIC_CONTROLS: Tuple[Control, ...] = (
    Control(
        id="govern",
        kind="agentic",
        label="Govern",
        parenthetical=(
            "Was this objective authorized for this identity for this tool chain?"
        ),
        binding=ControlBinding(kind="govern"),
    ),
    Control(
        id="contain",
        kind="agentic",
        label="Contain",
        parenthetical=(
            "Limit cross-tool sequences, regardless of individual permissions."
        ),
        binding=ControlBinding(kind="contain"),
    ),
    Control(
        id="detect",
        kind="agentic",
        label="Detect",
        parenthetical="Flag adaptive-chain patterns post-execution.",
        binding=ControlBinding(kind="detect"),
    ),
    Control(
        id="respond",
        kind="agentic",
        label="Respond",
        parenthetical="Interrupt the loop when retry-after-failure patterns emerge.",
        binding=ControlBinding(kind="respond"),
    ),
)


ALL_CONTROLS: Tuple[Control, ...] = TRADITIONAL_CONTROLS + AGENTIC_CONTROLS

CONTROL_BY_ID: Dict[str, Control] = {c.id: c for c in ALL_CONTROLS}


def applied_traditional_controls(
    controls: ControlSet, tool: str
) -> List[str]:
    """Return the traditional control IDs that altered this step's behavior.

    Includes:
      - `tool_status` / `tool_redact` bindings whose `target_tool` matches.
      - `scope_drop` bindings (caller-side identity mutation) that affect this
        tool's existing scope check (only `least_priv_catalog` →
        `data_catalog_search` today).

    Signal-only bindings (`detection_log`, `detection_flag`) and agentic
    hooks are excluded — the agent loop adds those separately when they
    actually fire on a given step. Order matches `TRADITIONAL_CONTROLS`.
    """
    fired: List[str] = []
    for control in TRADITIONAL_CONTROLS:
        if control.id not in controls.enabled:
            continue
        binding = control.binding
        if binding.kind in ("tool_status", "tool_redact") and binding.target_tool == tool:
            fired.append(control.id)
        elif binding.kind == "scope_drop" and control.id == "least_priv_catalog" and tool == "data_catalog_search":
            fired.append(control.id)
    return fired


def apply_to_tool_call(
    controls: ControlSet,
    tool: str,
    identity: Identity,
    base_result: ToolResult,
) -> ToolResult:
    """Layer enabled traditional controls onto a tool's base result.

    Returns a new `ToolResult`; `base_result` is not mutated. Adjustments are
    applied in `TRADITIONAL_CONTROLS` order so later bindings can layer over
    earlier ones (e.g., DLP redaction stays a 200 even if no other control
    has overridden the status).

    Signal-only bindings (`detection_log`, `detection_flag`) and agentic
    bindings (`govern`, `contain`, `detect`, `respond`) do not change the
    result here; the agent loop is responsible for those hooks. `scope_drop`
    is implemented at the caller layer (the agent drops `catalog:read` from
    its working identity before calling `call_tool`).
    """
    status = base_result.status
    observation = base_result.observation
    sensitive_exposure = base_result.sensitive_exposure
    detection_probability = base_result.detection_probability

    for control in TRADITIONAL_CONTROLS:
        if control.id not in controls.enabled:
            continue
        binding = control.binding
        if binding.target_tool is not None and binding.target_tool != tool:
            continue
        if binding.kind == "tool_status":
            if binding.new_status is not None:
                status = binding.new_status
                # A control that flips status to non-200 also blocks any
                # sensitive-exposure side effect of the call.
                if status != 200:
                    sensitive_exposure = False
            if binding.new_observation is not None:
                observation = binding.new_observation
            if binding.clear_sensitive:
                sensitive_exposure = False
        elif binding.kind == "tool_redact":
            if binding.new_status is not None:
                status = binding.new_status
            if binding.new_observation is not None:
                observation = binding.new_observation
            if binding.clear_sensitive:
                sensitive_exposure = False

    return ToolResult(
        tool=base_result.tool,
        status=status,
        observation=observation,
        detection_probability=detection_probability,
        sensitive_exposure=sensitive_exposure,
    )
