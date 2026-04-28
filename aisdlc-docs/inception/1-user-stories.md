# 1: User Stories

Source: `aisdlc-docs/inception/1-requirements.md`.

Seven user stories. Each is independently shippable in the sense that, on its own, it produces a slice of value — though several only deliver their full impact in combination. Acceptance criteria use Given/When/Then and cover happy path, one realistic unhappy/boundary case, and one screenshot or out-of-context-readability case.

---

## Story 1: Read the argument cold (90-second skim)

**As a** security-curious engineering leader who received the link in Slack and clicked through, **I want** the page's argument to land in the first viewport-and-a-half of scrolling, **so that** I get a tweet-length mental model in 90 seconds and can decide whether to engage further.

### Acceptance Criteria
- [ ] **Given** a reader who lands on the page, **when** they read the first viewport, **then** they see the thesis ("Same primitives. New control loop. New risk model.") plainly stated and the "curl is still curl" position fairly steelmanned in adjacent text.
- [ ] **Given** a hostile reader who already holds the "curl is still curl" position, **when** they read the steelman card, **then** they recognize their own position (no straw man) — concession to the primitive layer is explicit before any pivot.
- [ ] **Given** a reader who exits before the simulation, **when** they recall the page, **then** they can reproduce the thesis in their own words ("same primitives, new control loop, new risk") even without watching anything.
- [ ] **Given** a reader skeptical that a rule-based simulation represents a "real" agent, **when** they look for the page's framing of the simulation, **then** they see an explicit disclosure that the agent is rule-based by design so the control loop is inspectable, and the page's claim is structural — not about LLM intelligence.

### Risks & Edge Cases
- Reader has zero security background: thesis and steelman are written in plain English; "primitive" is illustrated with concrete examples (HTTP request, IAM denial) not jargon.
- Reader has deep red-team experience: steelman acknowledges "the agent here is rule-based, not an LLM" in passing — defuses the "real agents don't work that way" objection without making it the headline.
- Reader is on mobile: the first viewport-and-a-half assumption holds for typical phone viewports too.

---

## Story 2: Watch the divergence trace

**As a** reader who has scrolled into the simulation, **I want** to play, pause, and replay a frame-by-frame side-by-side trace of both actors pursuing the same goal, **so that** I experience the failure-becomes-feedback moment directly instead of being told about it.

### Acceptance Criteria
- [ ] **Given** a reader on the simulation section with default motion preferences, **when** the section enters the viewport (or they click play), **then** both actors are at step 0 in identical starting positions, advance step-by-step through their respective traces, and visibly diverge at step 1 (static halts on 403; agent annotates the 403 as feedback and continues with a new tool call).
- [ ] **Given** a reader who has `prefers-reduced-motion: reduce` set, **when** the section first renders, **then** the trace renders in its final completed state immediately, with controls to step through manually if they choose.
- [ ] **Given** the trace is in any intermediate state, **when** that state is captured as a screenshot, **then** the frame is independently intelligible — both actors' tool, status, observation, and per-actor state are readable without surrounding context.
- [ ] **Given** the trace has played to completion, **when** the reader clicks "replay," **then** the trace resets to step 0 and plays again from the same fixed seed (deterministic).

### Risks & Edge Cases
- Reader scrubs backwards or jumps ahead: per-step state is recomputable from step number, not accumulated, so scrubbing works in either direction without animation glitches.
- Reader screenshots mid-transition: every frame is a clean discrete state — no half-rendered transitions; intermediate animation frames are not capturable as primary states.
- Animation jitter on a slow laptop: animation tolerates dropped frames without skipping the divergence moment (the moment is announced explicitly in text, not only by motion).

---

## Story 3: See the comparative Monte Carlo curve

**As a** reader who wants quantitative grounding, **I want** to see a chart that overlays static success rate and agent success rate across capability levels 1–5, **so that** I see the slope difference and grasp that this is path-quality, not speed.

### Acceptance Criteria
- [ ] **Given** a reader scrolling past the trace, **when** they reach the Monte Carlo section, **then** they see two curves on one chart: a near-flat static curve and a rising agent curve as capability increases.
- [ ] **Given** the chart is captured as a standalone screenshot, **when** viewed without surrounding context, **then** axes are labeled, both curves have legends, and the divergent shape is the dominant visual signal.
- [ ] **Given** a reader who reads the caption next to the chart, **when** they interpret the curves, **then** the caption explicitly says "the difference is not speed — both actors are bounded to the same step budget" and links the slope difference to the failure-becomes-feedback property; a reader cannot leave thinking "agent is just faster."

### Risks & Edge Cases
- Reader objects to the rule-based agent: caption acknowledges the agent is a deliberately simplified model and links to the source so the reader can verify.
- Run count too low: pre-render uses ≥500 runs per capability bucket so the curves are stable and the slope difference reproducible.

---

## Story 4: Live talk demo (interactive)

**As the** author presenting on stage, **I want** to start the page locally with one command and adjust seed, capability, and max-steps in the UI, **so that** the audience sees the simulation respond live and trusts that nothing was pre-baked.

### Acceptance Criteria
- [ ] **Given** the author has a fresh clone of the repo, **when** they run `python agentic_security_demo.py --serve` (the v1 entry point; preserved or renamed in Phase 3 if the simulator package is restructured) and open `http://127.0.0.1:8000`, **then** the page loads with default parameters and the divergence trace is ready to play.
- [ ] **Given** the author changes a parameter (seed, capability, max-steps, runs), **when** they trigger a re-run from the UI, **then** the trace and the Monte Carlo chart both update to reflect the new parameters within ~2 seconds on a typical laptop.
- [ ] **Given** the laptop has no internet on stage, **when** the page loads, **then** no external assets (fonts, scripts, images, telemetry) are requested — page is fully self-contained.

### Risks & Edge Cases
- Conference projector at non-standard resolution: layout holds at 1920×1080 and 1280×720 without horizontal scrolling.
- Author wants to demonstrate "what if the agent has only 1 capability point" mid-talk: capability slider produces a recognizably degraded agent path (more wandering, more failed retries), reinforcing "capability bends the curve."

---

## Story 5: Static GitHub Pages snapshot (async share)

**As the** author sharing the link asynchronously in Slack or in a blog post, **I want** a static HTML version of the page hosted on GitHub Pages, **so that** a recipient who clicks the link sees the divergence trace and the comparative curve immediately, with no Python install required.

### Acceptance Criteria
- [ ] **Given** a documented build step in the repo (one Python command or one `make` target), **when** the build runs, **then** a static HTML page (with associated CSS / JS / data) is produced that requires no Python at runtime to deliver the divergence trace and the Monte Carlo chart.
- [ ] **Given** the static page is served from GitHub Pages, **when** a reader visits the URL on any modern browser, **then** the divergence trace plays to completion and the comparative curve is visible — same visual quality as the live version's equivalent frame.
- [ ] **Given** an interactive parameter control is not supported in the static version, **when** a reader interacts with it, **then** they see a clear, friendly note pointing to the GitHub repo and the `python -m web.server` instructions for the full interactive version (or the control is hidden in the static build, with a single "for full interactivity, run locally" link).

### Risks & Edge Cases
- Static page goes stale because the simulator changed: the build step is idempotent and the README documents how to rebuild and republish.
- Reader on a corporate browser blocks inline JS: divergence trace falls back to a paginated step-through (next/prev buttons) rather than auto-animation. (Stretch; flag in design if the cost is high.)

---

## Story 6: Author + source-of-truth visible

**As a** reader who has been convinced by the argument and wants to verify or follow up, **I want** to see the author's name and a link to the GitHub source, **so that** I can audit the simulation's honesty, file an issue, or reach the author.

### Acceptance Criteria
- [ ] **Given** a reader at any scroll position who looks for attribution, **when** they check the page footer (and ideally the header), **then** they see "Ryan Sevey" as the byline and a link to `github.com/rseveymant/agentic-sec-new`.
- [ ] **Given** a reader who clicks through to the repo, **when** they look for the simulator code, **then** the repo README points them to the simulator source files in two clicks or fewer.
- [ ] **Given** a reader wants to know the license, **when** they reach the repo, **then** `LICENSE` is visible at the root and reads MIT.

### Risks & Edge Cases
- Reader on mobile sees the footer pushed off-screen: byline and repo link are also referenced in a non-footer position (header link or hero card "by Ryan Sevey →").
- Reader wants to follow the author: out of scope for this story (no Twitter / LinkedIn links required); the repo is the canonical contact surface.

---

## Story 7: See the governance gap

**As a** reader who has just seen the divergence trace and grasped the control-loop point, **I want** a concise table that contrasts "what a traditional control inspects" with "what agentic security must additionally ask," **so that** I leave the page with a sharper, named sense of why existing controls are necessary but not sufficient — without being told what to buy or build.

### Acceptance Criteria
- [ ] **Given** a reader who has just finished the simulation section, **when** they scroll into the governance section, **then** they see a small table (~5 rows) with two columns labeled "Traditional control sees" and "Agentic security must also ask," where each row pairs a familiar control question with the additional question the trace has revealed (e.g., "Was this API call allowed?" / "Was this tool use aligned to an authorized goal?").
- [ ] **Given** the table is captured as a standalone screenshot, **when** viewed without surrounding context, **then** the contrast is intelligible — both column headers read clearly, and the gap reads as a set of new *questions*, not a list of products, controls to buy, or fixes to implement.
- [ ] **Given** a reader interpreting the section, **when** they read the surrounding caption, **then** the framing is explicitly threat-model: the page does not name or recommend specific controls, vendors, or programs (preserves the requirements-doc out-of-scope on defenses-in-depth catalogues).
- [ ] **Given** a reader on mobile, **when** the table renders on a narrow viewport, **then** rows stack vertically with each pair clearly labeled (`Traditional: …` / `Now also ask: …`).

### Risks & Edge Cases
- Reader interprets the table as a vendor pitch or "you need this" CTA: surrounding caption and visual style stay neutral; no CTA, no vendor names, no arloa.ai mention, no "see our product" footer.
- Table risks overreach if it lists every conceivable gap: hold to ~5 rows that map directly to behaviors the reader has just witnessed in the trace — the 403, the breadcrumb pickup, the alternate tool path, the chained legitimate authority, the goal pursuit. One row per witnessed behavior.
- Author later wants to extend the table into "and here's how to fix it" content: that lives in a separate artifact (per requirements out-of-scope); resist adding here.
