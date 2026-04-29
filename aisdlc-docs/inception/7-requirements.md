# 7: Interactive controls section + sharpened argument

Enhancements to the existing demo at https://rseveymant.github.io/agentic-sec-new/. Adds one new interactive section, rewrites three existing argument sections, replaces the static governance-gap table. Framed as enhancements, not a v2 — the page reads as one artifact, deepened.

This document is the delta against `aisdlc-docs/inception/1-requirements.md`. Constraints, audience, distribution model, brand/authorship, license, and v1 archive policy are inherited unchanged unless noted.

## Problem

The v1 page lands the threat-model argument for receptive readers — but a meaningful share of skeptics now bounce off one layer deeper. They concede the primitives are old, then assert that existing *controls* (not primitives) handle the new control loop. The author hears four reflexive forms of this:

1. *"OK, but we have controls for that — just rate-limit the API and you're fine."*
2. *"This is a rule-based simulation. A real LLM would be detected sooner."*
3. *"Existing IAM and DLP would catch this in production."*
4. *"You're showing one toy scenario, not a real attacker model."*

The current page does not close any of these down. The author still has to walk through, control by control, why each is routed around — which is the same Zoom debate as before, one level deeper. There is no shared artifact to send. The author is again the artifact; the author's calendar is again the bottleneck.

The opportunity: an interactive section that lets the reader *apply* the controls they would themselves recommend, watch the agent route around them, and then toggle on a different *category* of controls (governance / containment / detection / response) and see the loop interrupted. The reader runs their own experiment instead of being told.

## Users & Roles Affected

- **Author (Ryan Sevey, personal capacity).** Same as #1. Wants to stop having the "but we have controls" debate verbally and start having it asynchronously. No arloa.ai branding.
- **Skeptical engineering leader / CTO (primary reader).** Same as #1, refined: now includes the subset who *accepts* the primitive-layer concession but reaches for "we have controls for that" as the next defense. They are who the new section is aimed at.
- **Author's broader network (incidental).** Same as #1. Forwards screenshots; spreads the argument.

## Success Criteria

- A skeptic who held one of the four pushbacks above plays with the toggles for ~60 seconds, sees their own suggestion routed around, and replies with either "OK, fine — what's a govern/contain/detect/respond control then?" or shifts to talking about implementation. Verbal pushback should resolve into a substantive question, not into a different reflex.
- At least one screenshot per pushback is produced — a frame the author can paste back into a Slack thread. Specifically: a pre-toggle frame, a "MFA on / agent still succeeds" frame, an "agentic Govern on / agent halts" frame, and an "all traditional on, agent still finds a path" frame.
- The page reads top-to-bottom as one continuous argument; readers who scroll past the trace and chart land in the new interactive section without feeling a discontinuity. The "enhancement, not v2" framing means the existing live URL keeps its identity.
- The argument's strongest version moves into the page text: "the agent moves the success/detection *ratio*, not just the rate." A skeptic cannot leave thinking *"agents are dangerous because they do the same thing faster"* — that framing has been actively countered in copy.

These are qualitative but observable; same evaluation rhythm as #1.

## Authoritative Phrasing

User-approved verbatim lines and content that must appear (or appear in close paraphrase) in the final artifact. Phase 3 (design) and implementation are bound by these.

**Load-bearing claims (rewrite material for steelman / pivot / equation sections):**

- *"Agentic AI changes the success/detection race because it changes the attacker's control loop, not merely the attacker's speed."*
- *"Traditional automation executes steps. Agentic AI pursues objectives."*
- *"A script fails when the path breaks. An agent treats failure as information."*
- *"The issue is not that the agent makes the same bad path faster. The issue is that the agent searches the path space differently."*
- *"AI lowers the cost of adaptive cognitive work and raises the baseline capability available to many more actors."*
- The shift line: *"Old model: security buys time. Agentic model: security must constrain autonomous search."*

**Traditional model — explicit statement (steelman / pivot rewrite):**

> A human attacker has finite time, attention, expertise, and patience. A static script has fixed instructions and brittle failure modes. Defense adds friction. Friction increases time-to-success. Monitoring reduces time-to-detection. Defender wins if detection or containment happens before impact.
>
> *Defender wins if `time_to_detect_or_contain < human_time_to_impact`.*

**Closed-loop framing (pivot rewrite):**

> Script: `goal → step → fail → stop`.
> Agent: `goal → plan → act → observe → update → retry → adapt → continue`.

**Equation section (in `<details>` collapse):** see §Equation rewrite below for content; phrasing direction:

- Lead with the rate-race intuition (`λ_success` vs `λ_detect`), then expose the variable model.
- Replace any "AI IQ" framing with *autonomous task-completion capability* (or *effective adversarial throughput*).
- Include the stress test: *agentic risk is lower when [no tools / read-only / narrow perms / memory disabled / external content cannot influence tool use / approval-gating / agent identity separation / retry caps]*. The argument is measured, not catastrophist.

**New interactive section copy:**

- Heading direction: ties to the "apply the controls your skeptic recommended" frame. Not a sales pitch.
- Sub-heading direction (above the toggles): *"Apply the controls your skeptic recommended. Watch the agent route around them. Then try a different shape of control."*
- Below the toggles, when traditional toggles are on but agentic toggles are off, copy reads: *"Friction added. Path changed. Goal still pursued."* (or close paraphrase).
- When at least one agentic toggle is on and the agent's loop halts: *"The loop is interrupted, not just the call."* (or close paraphrase).
- Reset / "show all on" / "show all off" buttons get neutral labels — no urgency framing.

**The four agentic categories (toggle labels):**

| Toggle | Parenthetical (the question this category asks) |
|---|---|
| **Govern** | Was this objective authorized for this identity for this tool chain? |
| **Contain** | Limit cross-tool sequences, regardless of individual permissions. |
| **Detect** | Flag adaptive-chain patterns post-execution. |
| **Respond** | Interrupt the loop when retry-after-failure patterns emerge. |

These are categories of question the control must ask, not products. No vendor, no concrete mechanism (no "objective-level policy DSL," no "tool allowlist by purpose"). Surface only what each *category observes*.

**The eight traditional controls (toggle labels):**

Each is scoped to a specific tool in the toy enterprise so the reader sees concrete behavior, not a blanket switch. Exact tool-bindings are a Phase 3 decision; the user-facing labels and their evasion shapes:

| Toggle | Evasion shape (what the agent does when it's enabled) |
|---|---|
| **MFA on direct_vault_read** | 401 step-up required. Agent skips this path entirely; uses delegated-employee identity through a different tool. |
| **Network segmentation on direct_vault_read** | No-route. Agent routes through an approved analytics tool that already has the data. |
| **Least-privilege scope on sensitive_export** | 403 scope. Agent uses a non-sensitive scope chain that aggregates the same data. |
| **Audit logging on all calls** | No block. Detection-signal indicator increments. Agent's path unchanged; appears in a side panel as "logged." |
| **Rate-limit on file_search** | 429 with retry-after. Agent waits or pivots to a less-rate-limited tool that surfaces the same context. |
| **Approval-gate on sensitive_export** | 403 awaiting approval. Agent re-routes through an analytics tool whose default authority covers the export. |
| **DLP on outbound mail** | 200 with sanitized payload. Agent observes that the data didn't leave; pivots to an approved export channel that DLP doesn't gate. |
| **Anomaly detection on tool sequences** | No block. Detection-signal indicator increments. The agent's adaptive chain is exactly the kind of pattern this would flag — but doesn't stop. |

**Detection signal:** logging and anomaly detection don't block — they raise a visible counter. This is the page's honest version of "post-hoc detection is not the same as prevention." Agentic *Detect* (post-execution flag) increments the same signal *and* labels the chain explicitly; Agentic *Respond* halts the loop.

## Constraints

Inherited from #1 except where noted.

**Technical**
- Python 3 stdlib only, server-side. (Inherited.)
- Frontend hand-written HTML / CSS / JS, no framework, no bundler. (Inherited.)
- **JS port — scoped exception to ADR-1.** A small JavaScript module re-evaluates which steps are blocked, redirected, or flagged based on enabled controls, so the static GitHub Pages snapshot supports toggling without a Python runtime. The path-search and trace generation stay in Python; the JS port is a thin overlay on a pre-rendered superset trace. Phase 3 specifies the wire shape and the boundary. **The JS port does NOT re-implement the agent's adaptive search.**
- No external assets, no CDN, no telemetry, no auth. (Inherited.)
- License: MIT. (Inherited.)

**Distribution**
- Live talk demo: same `python agentic_security_demo.py --serve` entry point. The toggles re-fetch from `/api/trace` with control parameters in the query string. Server is the source of truth.
- Static GitHub Pages: ships a pre-rendered "superset trace" — the agent's full path-search tree under a canonical seed and capability — plus the JS overlay that prunes / annotates steps based on toggled controls. Same canonical default as static-mode v1.
- Both delivery paths share the same JSON contract. (Inherited.)

**Performance (proposed targets, refine in design phase)**
- Toggling a control re-renders the trace inside ~250ms in static mode (JS-only) and inside ~600ms in live mode (round-trip to Python).
- Pre-rendered superset trace size stays under ~150KB gzipped.

**Accessibility**
- Toggles are real `<input type="checkbox">` with `<label>` — no clickable divs.
- Detection-signal counter is a polite live region, not visual-only.
- Toggle order and grouping read sensibly with a screen reader. (Inherited reduced-motion + contrast rules.)

**Mobile**
- 12 checkboxes is a lot on a phone. Toggles render as a single column on narrow viewports, grouped under "Traditional" / "Agentic" headings. Trace stacks vertically below.

## Edge Cases Considered

- **All toggles off** (default state). Trace renders identically to v1: same primitives, agent succeeds via path adaptation. No regression.
- **All eight traditional on, zero agentic.** This is the visceral payoff. Agent still reaches the goal — slower path, more steps, possibly noisier — but reaches it. Detection-signal counter is high if logging/anomaly are on.
- **All four agentic on, zero traditional.** Agent halts at the Govern check (objective-level policy denies the chain). Loop never starts. Detection signal is moot because nothing executed.
- **One traditional on, one agentic on (e.g., MFA + Govern).** Agent halts at Govern regardless of MFA — Govern is upstream. Reader learns: agentic controls are upstream of the per-call gates, not a replacement for them.
- **Reader rapidly toggles many controls.** Live mode debounces re-fetches; static mode re-renders synchronously (cheap). No race conditions.
- **Reader on mobile screenshotting.** Each state is screenshottable independently — the chosen toggles are visible in the same frame as the resulting trace.
- **Reader toggles, then scrolls — section is mid-render.** Final state is deterministic; scrolling away and back doesn't lose state.
- **Static mode reader expects the live-only seed/capability sliders.** Already absent in v1's static; no new behavior. Toggles are present in both modes.
- **Reader screen-reads the page.** Toggle group names announce; each toggle's parenthetical reads as part of the label; trace updates use `aria-live="polite"` on the steps region.

## Out of Scope

Inherited from #1 (no real attack content; no LLM-backed agent; no arloa.ai branding; no analytics; no public hosting infra; no multi-scenario menu — single canonical scenario with toggle variations) except as updated below.

**Confirmed for #7:**

- **No products, no vendors, no concrete mechanism names.** "Govern" stays a category; we never write "objective-level policy DSL" or "tool allowlist by purpose" or any vendor name. The four agentic categories' parentheticals describe what the category *observes*, not how to implement it.
- **No defenses-in-depth catalogue.** The "fix-it" guide stays a separate artifact. The new section demonstrates the *gap* (what each control class does and doesn't see); it does not prescribe controls to implement.
- **No expansion of the threat scenario.** Same toy enterprise, same goal (board forecast retrieval), same agent kind (rule-based by design — Story 1 of #1's disclosure stands).
- **No real-time multiplayer / sharing of toggle states.** No URL-encoded state to forward (deferred to open question).
- **No analytics on which toggles users hit.** Personal artifact, no telemetry. (Inherited.)
- **No full LLM agent simulation.** The rule-based agent is the design choice; the toggles change what *responses* the agent observes, not what *intelligence* it has.
- **No replacement of the trace, MC, or source sections.** Only steelman, pivot, equation, and governance sections are touched. Trace and MC are extended only insofar as the simulator gains control-aware behavior; their UX is unchanged.

## Open Questions

Carried to Phase 3 unless noted.

- **Superset-trace shape.** Phase 3 has to nail the JSON contract for the pre-rendered superset (the agent's full searched path tree under canonical seed/capability) and the JS-side overlay that prunes/annotates by toggle state. Exact shape = design decision.
- **Tool-binding for traditional controls.** Each control toggle is scoped to specific tools (e.g., MFA *on direct_vault_read*). Confirm the tool↔control bindings against the existing `simulator/world.py` tool list. Phase 3 catalogues each binding; the requirements doc above is the proposed mapping but the Phase 3 author should validate against the actual tool surface.
- **Detection-signal UX.** Counter, badge, log feed, sparkline? Visible above or beside the trace? Stays a UX call for Phase 3 / Phase 4-D.
- **Page-narrative anchor for the new section.** Working title for the anchor `#controls`; copy heading TBD with the user during implementation. Pull from the authoritative phrasing material above.
- **State-encoding in URL.** Should the toggle state be reflected in the URL hash (so screenshots can be paired with shareable links)? Deferred — useful, low cost; flag for Phase 3.
- **Equation-section default visibility.** Currently `<details>` collapsed. With the rewritten richer equations, consider whether the rate-race intuition line lives *outside* the collapse (always visible) and only the equations themselves are inside. Phase 3 / Unit-equivalent decision.
- **Naming of the Detection-signal counter.** "Detection signal" is a working name; might land as "logged events" / "flagged sequences" / etc. Resolve in copy unit.

## Links

- Parent inception issue: [rseveymant/agentic-sec-new#7](https://github.com/rseveymant/agentic-sec-new/issues/7)
- Predecessor: [#1](https://github.com/rseveymant/agentic-sec-new/issues/1) — original page.
- Predecessor docs: `aisdlc-docs/inception/1-requirements.md`, `1-user-stories.md`, `1-design.md`, `1-units.md`.
- Live page (existing): https://rseveymant.github.io/agentic-sec-new/
- Source brief (verbatim user content from inception conversation): captured in this document's Authoritative Phrasing section; full stress-test of the equations is preserved in conversation transcript and is the substrate for the rewritten equation section.
