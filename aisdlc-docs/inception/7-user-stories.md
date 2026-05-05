# 7: User Stories

Source: `aisdlc-docs/inception/7-requirements.md`. Inherits user-roles model and acceptance-criteria style from `1-user-stories.md`.

Five stories. Story 1 is independently shippable as a copy-only release. Stories 2 and 3 are coupled — they share the same toggle panel and shipping one without the other lands worse than v1. Story 4 ships with Stories 2/3. Story 5 (static) ships after Stories 2/3/4 are in place.

---

## Story 1: Argument is sharper top-to-bottom (steelman + pivot + equation rewrites)

**As a** skeptical engineering leader rereading the page after the v1 conversation, **I want** the argument to lead with the rate-race / closed-loop framing in plain English (and the harder math available behind a disclosure), **so that** I cannot leave with "agents are dangerous because they do the same thing faster" as my takeaway.

### Acceptance Criteria
- [ ] **Given** a reader on the steelman section, **when** they read it, **then** the explicit traditional model is stated — *human attacker has finite time / static script has fixed instructions / defense adds friction / friction increases time-to-success / monitoring reduces time-to-detection / defender wins if detection or containment beats impact* — followed by the line `defender wins if time_to_detect_or_contain < human_time_to_impact` framed as the reader's own working model.
- [ ] **Given** a reader on the pivot section, **when** they read it, **then** the closed-loop framing is plain: `script: goal → step → fail → stop` vs `agent: goal → plan → act → observe → update → retry → adapt → continue` — and the page says explicitly *"the difference is feedback, not speed"* (or a close paraphrase) before the trace section starts.
- [ ] **Given** a reader who expands the equation `<details>`, **when** they read it, **then** they see the rate-race intuition (`λ_success` vs `λ_detect`, ratio matters); the variable model for agentic throughput (`W / (M × T × A × F × R × P × D)` with each variable defined); the governance-aware defender equation (`min(T_govern, T_detect, T_contain, T_response)`); and the stress-test paragraph naming when agentic risk is *low* — so the argument reads measured, not catastrophist.
- [ ] **Given** any reader at any scroll position, **when** they search the page text, **then** the phrase "AI IQ" does not appear; instead, *autonomous task-completion capability* (or *effective adversarial throughput*) is used.
- [ ] **Given** a reader screenshotting a single rewritten section, **when** the screenshot is shared without the surrounding page, **then** the section reads as a self-contained argument. Steelman alone makes the traditional-model case; pivot alone makes the closed-loop case.

### Risks & Edge Cases
- Reader is on mobile and the equations overflow: equations wrap or scroll horizontally inside their `<pre>` block; the surrounding paragraphs reflow.
- Reader has the v1 page bookmarked and opens to the steelman: section reads as a deepening, not a contradiction. The "curl is still curl" concession is preserved verbatim or close.
- Reader is hostile and reads only the equation section: the stress-test paragraph denies them an "this is fearmongering" exit.

---

## Story 2: Apply traditional controls and watch the agent route around them

**As a** skeptic who has just argued *"we have controls for that — just rate-limit it,"* **I want** to toggle the eight common traditional controls myself and see the agent re-plan around each, **so that** I experience my own suggestion getting routed around without having to be told it would be.

### Acceptance Criteria
- [ ] **Given** a reader scrolling past the Monte Carlo chart, **when** they reach the new section, **then** they see a panel labeled "Traditional" with eight checkboxes — MFA on direct_vault_read / network segmentation / least-privilege scope on sensitive_export / audit logging / rate-limit on file_search / approval-gate on sensitive_export / DLP on outbound mail / anomaly detection on tool sequences — each unchecked by default, and the trace below renders as the v1 default trace.
- [ ] **Given** a reader who toggles MFA on, **when** the trace re-renders, **then** the agent's first attempt at direct_vault_read returns 401 step-up required (visible in the agent's step list with the new status), and the agent's adapted path uses a different tool to reach the same goal (visible in subsequent steps); the reader can read each step's tool, status, and observation without surrounding context.
- [ ] **Given** a reader who toggles all eight traditional controls on, **when** the trace re-renders, **then** the agent still reaches the goal — possibly with more steps and a noisier path — and the page copy below the trace reads *"Friction added. Path changed. Goal still pursued."* (or close paraphrase from §Authoritative Phrasing).
- [ ] **Given** a reader who screenshots a single state (e.g., "rate-limit + DLP on, Govern off"), **when** the screenshot is shared, **then** the chosen toggles and the resulting trace are both visible in the same frame and the cause/effect is intelligible without surrounding text.
- [ ] **Given** a reader on a phone, **when** they interact with the toggle panel, **then** the eight checkboxes stack in a single column under the "Traditional" heading; tapping a checkbox is reachable without horizontal scroll; the trace stacks vertically below.

### Risks & Edge Cases
- Reader toggles many controls in rapid succession: live mode debounces re-fetches (~150ms), static mode re-renders synchronously per toggle. No race conditions.
- Reader toggles a control whose tool the agent does not visit in the canonical seed: the trace renders without that step appearing as blocked; the toggle still shows as "active" but had no effect on the chosen path. Caption near the toggle clarifies (working copy: "This control is enabled but the agent did not attempt the tool it gates.").
- Reader uses a screen reader: the trace's step-list updates as `aria-live="polite"`; toggle state changes announce as standard checkbox state changes.

---

## Story 3: Apply agentic controls and see the loop interrupted

**As a** reader who has just watched all eight traditional controls fail to stop the agent, **I want** to toggle the four agentic-control categories — govern / contain / detect / respond — and see what each does to the agent's behavior, **so that** I leave with a named mental model of what shape of control interrupts the loop instead of adding friction.

### Acceptance Criteria
- [ ] **Given** a reader on the new section, **when** they read the second toggle group, **then** they see a panel labeled "Agentic" with four checkboxes — *Govern (was this objective authorized for this identity for this tool chain?)* / *Contain (limit cross-tool sequences, regardless of individual permissions)* / *Detect (flag adaptive-chain patterns post-execution)* / *Respond (interrupt the loop when retry-after-failure patterns emerge)* — each label explicitly framed as a *question the control category asks*, not a product or mechanism.
- [ ] **Given** a reader who toggles Govern on (with all other toggles off), **when** the trace re-renders, **then** the agent halts at step 0 with a "denied: objective + identity + tool chain not authorized" observation; no tool call executes; the trace shows zero successful steps; the page copy reads *"The loop is interrupted, not just the call."* (or close paraphrase).
- [ ] **Given** a reader who toggles Contain on alone, **when** the trace re-renders, **then** the agent's first one or two tool calls succeed but the cross-tool chain (e.g., file_search → sensitive_export) is blocked at the *transition*, with an observation noting "cross-tool sequence limit reached" — distinct from a per-call permission denial.
- [ ] **Given** a reader who toggles Detect on alone, **when** the trace re-renders, **then** the agent's path is *unchanged* — no step is blocked — but the detection-signal counter (Story 4) increments, and the trace's final summary explicitly labels the run as flagged.
- [ ] **Given** a reader who toggles Respond on alone, **when** the trace re-renders, **then** the agent's first failure-and-retry triggers a loop interrupt — the agent halts mid-trace, with an observation noting "retry-after-failure pattern interrupted."
- [ ] **Given** a reader who toggles MFA + Govern (one traditional + one agentic), **when** the trace re-renders, **then** Govern halts the agent before MFA matters; the reader sees that agentic controls are upstream of per-call gates, not a replacement for them.
- [ ] **Given** a reader screenshotting the "Govern on, agent halted at step 0" state, **when** the screenshot is shared, **then** the halt and its reason are visible in the same frame as the toggle that caused it.

### Risks & Edge Cases
- Reader interprets the toggle parentheticals as product names: parentheticals are deliberately *questions*, not mechanism names. Copy reinforces "category, not product."
- Reader toggles all four agentic on together: agent halts at the earliest gate (Govern). The other three toggles register as "would also have applied if Govern had not."
- Reader scrolls away mid-toggle: the section's last toggle state and trace state persist on scroll-back (no auto-reset). Refresh resets to defaults.

---

## Story 4: Detection signal — observable but non-blocking

**As a** reader watching the trace, **I want** controls that don't block (logging, anomaly detection, agentic Detect) to produce a visible signal anyway, **so that** the page makes the honest distinction between *post-hoc detection* and *prevention*.

### Acceptance Criteria
- [ ] **Given** a reader with audit logging toggled on, **when** the trace plays, **then** a detection-signal counter near the trace increments with each step; the agent's path is unchanged.
- [ ] **Given** a reader with anomaly detection toggled on, **when** the agent's adaptive chain executes (≥2 alternate-path retries), **then** the detection-signal counter increments by an extra anomaly mark and the trace's summary line names the chain ("flagged as adaptive sequence").
- [ ] **Given** a reader with agentic Detect toggled on, **when** the trace plays, **then** the same detection-signal counter increments AND the trace's per-step memory annotation includes a "this chain matched a known adaptive pattern" note — distinguishing agentic Detect from traditional anomaly detection by *what it observes* (the chain, not a generic anomaly).
- [ ] **Given** a reader on a screen reader, **when** the detection-signal counter changes, **then** the change is announced via an `aria-live="polite"` region with the format "logged events: N, flagged sequences: M."
- [ ] **Given** a reader screenshotting the trace + detection signal, **when** the screenshot is shared, **then** both the agent's path AND the signal counter are in frame, making the "the path completed; here's what was logged" point legible.

### Risks & Edge Cases
- Reader confuses the detection-signal counter with a prevention indicator: copy near the counter reads "These count what controls *observed*, not what they *blocked*." (or close paraphrase).
- Counter overflows visually if many controls are on across many steps: counter stays a tight horizontal pair (e.g., `▣ 14 logged · ⚠ 3 flagged`), no per-step ribbon explosion.

---

## Story 5: Static GitHub Pages snapshot supports the toggles

**As the** author sharing the link asynchronously in Slack or in a blog post, **I want** the new interactive section to work fully on GitHub Pages with no Python runtime, **so that** the recipient can apply the same toggles and reach the same understanding without running anything.

### Acceptance Criteria
- [ ] **Given** the static build runs, **when** it finishes, **then** `web/static/data/` includes a "superset trace" JSON containing the agent's full path-search tree under the canonical seed/capability — the data the JS overlay needs to prune/annotate by toggle state — and total static-data size remains under ~150KB gzipped.
- [ ] **Given** a blog reader on GitHub Pages with no Python runtime, **when** they toggle any of the 12 controls, **then** the trace re-renders inside ~250ms with the same visual outcome the live demo produces for the same toggle state.
- [ ] **Given** a blog reader who toggles a state the superset trace does not cover, **when** the JS overlay cannot reconstruct the resulting path, **then** the section shows a clear "this combination requires the live demo" note with a link to the GitHub repo and `python agentic_security_demo.py --serve` instructions.
- [ ] **Given** the static page on a slow network, **when** first paint completes, **then** the toggle UI is visible immediately; the superset-trace JSON loads in the background; until it loads, toggles are disabled with a clear loading note.
- [ ] **Given** the live and static modes side-by-side, **when** the same toggle state is set in each, **then** the resulting trace is visually identical (same steps, same statuses, same memory annotations).

### Risks & Edge Cases
- Superset trace size grows with capability: cap at canonical capability=4; document that running locally with higher capability requires the live demo.
- JS overlay diverges from Python simulator over time: a smoke-test in the static build invokes the JS overlay against the canonical superset and asserts a fixed expected output for several seed toggle states. Drift surfaces in CI / pre-deploy.
- Reader loses connectivity mid-load of the superset JSON: the toggle UI shows a "couldn't load — refresh to retry" note rather than appearing to "work" against missing data.
