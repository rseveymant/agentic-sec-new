# 1: Agentic-Sec Control-Loop Demo

A single web page that uses a closed-world toy simulation to make the case that agentic AI is not "the same attacks, faster" — that the primitives are old but the *control loop* around them is new, and that change moves the risk model.

## Problem

Today, the author repeatedly has the same Zoom and Slack debate with peers and engineering leaders who hold the position that agentic AI is "just `curl`, faster." The argument runs aground at the primitive layer ("API calls are still API calls, IAM is still IAM, injection is still injection") before reaching the substantive disagreement about whether a goal-directed, non-deterministic, tool-using, memory-bearing, adaptive control loop changes the risk model.

The cost is not abstract: the same conversation is re-litigated synchronously, in real time, every time the topic comes up. There is no shared artifact to send a skeptical reader. The author is the artifact, and the author's calendar is the bottleneck.

## Users & Roles Affected

- **Author (Ryan Sevey, personal capacity).** Initiates the argument, owns the artifact. Wants to stop having this debate verbally and start having it asynchronously by sharing a link. Personal project; not affiliated with arloa.ai for this artifact.
- **Skeptical engineering leader / CTO (primary reader).** Receives the link, possibly cold. Skims, scrolls, plays with the divergence visualization for a few minutes, screenshots a frame for a thread or deck. Walks away with one mental model: *static automation: goal → step → fail → stop. Agentic: goal → step → fail → adapt → continue. Same primitives, different loop, different risk.*
- **Author's broader network (incidental).** People who screenshot or forward the page. They don't reply directly; they spread the argument.

## Success Criteria

- A reader who started skeptical of the control-loop framing sends an unprompted "OK, I get it" message after reading the page.
- The author can share the link in Slack or Zoom and the conversation moves *past* primitive-layer round trips into substantive control-loop / governance discussion (not back to "but it's still curl").
- The divergence trace produces good screenshots — at least one frame is visually intelligible enough to use as a slide or post hero image without surrounding text.

These are qualitative but observable. Three months out the author can look back and say yes/no, this happened — that is enough for a personal artifact.

## Authoritative Phrasing

User-approved verbatim lines and content that must appear in the final artifact. Phase 3 (design) and implementation are bound by these; surrounding copy can vary, these specific phrasings are load-bearing.

- **Page title:** *Same Primitives. New Control Loop.*
- **Subtitle:** *A small simulation showing why agentic AI risk is not just "the same attacks, faster."*
- **Thesis line:** *Same primitives. New control loop. New risk model.*
- **Adjacent-to-trace line:** *The difference is not speed. The difference is what happens after failure.*
- **Closing line:** *curl is still curl. But the thing deciding the next curl has changed.*
- **Rule-based-agent disclosure (verbatim or close paraphrase):** *This simulation deliberately uses a simplified rule-based agent so the control loop is inspectable. The claim is not that this toy agent is intelligent. The claim is that adding observation, memory, retry, and alternate-path selection changes the security behavior.*

**Tone direction:** render the agent as boringly mechanical — observe, record, search, rank, retry. Not magic. The argument is stronger when the agent looks dull and predictable.

**Governance-gap table** (verbatim user content, 5 rows, two columns; ordering preserved):

| Traditional control sees | Agentic security must also ask |
|---|---|
| Was this API call allowed? | Was this tool use aligned to an authorized goal? |
| Did this identity have access? | Was the agent acting under valid delegated intent? |
| Was this request suspicious? | Was this part of an adaptive chain after failure? |
| Did DLP catch the output? | Did the agent act across tools before producing output? |
| Did logs capture the event? | Can logs reconstruct goal, plan, context, memory, and tool chain? |

## Constraints

**Technical**
- Python 3 standard library only on the backend; no pip dependencies.
- Frontend is hand-written HTML / CSS / JS; no framework, no bundler. A single Python pre-render script is permissible (see Distribution below).
- Live demo runs as `python -m web.server` (or similar) on a single laptop. No external services, no auth, no runtime deployment infrastructure for the live demo.
- No real network access, no real secrets, no real attack content. The toy enterprise is fictional and self-contained.
- License: MIT (already on repo).

**Distribution**
- **Live talk demo:** Python stdlib server on the speaker's laptop. Full interactivity (seed, capability slider, Monte Carlo runs).
- **Blog reader / async share:** static HTML snapshot of the page (canonical fixed seed) served from GitHub Pages. The divergence trace must be experienceable in the static version — readers must be able to play through the frame-by-frame animation without running Python. The static and live versions share the same source of truth for the simulation; the static version either ships a JS port of the simulator or embeds pre-computed trace data as JSON. Decision deferred to Phase 3 (design).

**Brand / authorship**
- Byline: Ryan Sevey, personal. No arloa.ai branding, no company affiliation visible on the page.

**Performance (proposed targets, refine in design phase)**
- Initial page render under ~500ms on a conference laptop on local loopback.
- Monte Carlo precomputation runs server-side once on page load and returns inside ~2s on the same laptop.
- Animated divergence trace plays smoothly (no commitment to a specific FPS target; "no visible jank" is the bar).

**Accessibility**
- Semantic HTML; sufficient color contrast for screenshots and projection.
- Animation respects `prefers-reduced-motion`: trace auto-completes to the final frame instead of auto-playing.
- Color is not the only signaling channel — status badges combine color, label, and shape/icon.

**Mobile**
- Page is readable on a phone. The animated divergence trace falls back to vertical stacking on narrow viewports. Mobile is not optimized, but must not be broken.

## Edge Cases Considered

- **Reader has no security background.** Page does not assume IAM / DLP / OWASP fluency. Glossary or hover-defs for non-common-tech terms.
- **Reader pauses or scrolls away mid-animation.** Animation is replayable — the user can scrub or tap "play" again. First paint is the start frame, not auto-play (paired with reduced-motion handling above).
- **Reader is hostile and nitpicks "the rule-based agent isn't really agentic."** Page acknowledges this in the steelman section: the agent is rule-based by design, so the inspection is honest and the structural argument doesn't depend on the agent being an LLM.
- **Conference WiFi is slow or offline.** Page is fully self-contained and served locally. No external fetches, no CDN.
- **Reader screenshots a single frame in a thread.** Every key frame stands alone — diverged-trace frame, static "stopped" frame, and Monte Carlo curve frame must each be intelligible without surrounding context.
- **Reader has reduced color vision.** See accessibility constraint above.

## Out of Scope

- Real attack content, exploitation recipes, or runnable offensive code. The toy enterprise stays toy.
- Survey of agentic-security failure modes beyond the control-loop / failure-becomes-feedback argument. No prompt-injection deep-dive, no model jailbreaks, no training-data poisoning, no memory-poisoning case studies.
- arloa.ai product pitch, sales narrative, or company branding.
- Defenses-in-depth catalogue or "here is how to fix it" recommendations. This page makes the threat-model argument; the fix-it argument is a separate artifact.
- LLM-backed agent. The demo agent is rule-based on purpose: easier to inspect, safer to ship, structural point unchanged.
- Multi-scenario menu. One canonical scenario (board forecast / approved analytics export path) only.
- User accounts, persistence, sharing features, comments, analytics. Static behavior.
- Public hosting infrastructure. Local laptop is the host for live demos; blog readers click out to the GitHub repo.

## Open Questions

- **Static export mechanics.** Now that GitHub Pages is the blog-reader entry point (resolved), Phase 3 must pick *how* the static version implements the simulation: (a) full JS port of the simulator running in the browser, (b) Python pre-render that bakes the canonical trace into JSON embedded in the HTML, with no client-side simulator, or (c) hybrid — JS animation engine but trace data is pre-baked, only the canonical seed is interactive. Tradeoff: (a) is most flexible but doubles the simulator surface; (b) is smallest but loses interactive parameter sweep on the static version; (c) is the pragmatic middle.
- **Math visibility.** This audience (CTOs / eng leaders) may not want the full risk equations on screen by default. Default to the comparative Monte Carlo chart only, with a "show math" disclosure for the equations? Or keep equations inline because they are part of the page's authority?
- **Steelman placement.** Where does the primitive-layer skeptic argument get its fullest hearing — top (concede before pivoting), middle (after the visceral demo lands), or threaded throughout as inline contrast cards? Affects narrative flow and screenshot quality.
- **Trace richness.** v1 has the agent take 2–3 alternate steps. Is that long enough to make autonomy *visible*, or should the agent's path be slightly longer (and the toy environment slightly richer) so the adaptive behavior reads as real and not as a single lucky branch?
- **v1 file disposition.** Keep `agentic_security_demo.py` and `README_agentic_security_demo.md` in the repo as a `v1/` reference subdir, or delete after extracting design intent? No impact on ship; preference call.

## Links

- Parent inception issue: [rseveymant/agentic-sec-new#1](https://github.com/rseveymant/agentic-sec-new/issues/1)
- v1 reference (local, not committed): `agentic_security_demo.py`, `README_agentic_security_demo.md`
- Author notes (full steelman of both sides + equations): captured verbatim in the inception conversation; will be the authoritative source for thesis phrasing in Phase 2 (user stories) and copy in implementation.
