# Same Primitives. New Control Loop.

A small simulation showing why agentic AI risk is not just *"the same attacks, faster."* Same primitives, new control loop, new risk model.

**Live (hosted, static):** https://rseveymant.github.io/agentic-sec-new/
**Source:** this repo. The `v1/` directory holds the original 859-line single-file prototype as a reference snapshot.

## What this is

A web page (live and static-deploy) with two actors that pursue the same goal in a closed-world toy enterprise. They use the same starting credentials and the same tool catalogue. They make the same first call. They both get a 403.

The static script stops. The agent treats the failure as feedback, searches internal context, finds an alternate approved-looking path through legitimate tools, and reaches the goal.

A Monte Carlo curve then shows that capability bends the agent's success rate but leaves the static actor flat — the difference is path quality, not speed. Failure becomes feedback.

The artifact exists to replace a recurring verbal argument ("curl is still curl") with something link-able and screenshottable.

## Enhancements (#7)

Layered on top of the v1 page without replacing it:

- **New `#controls` interactive section.** 12 toggles in two groups — 8 traditional controls (MFA, segmentation, least-privilege, audit logging, rate-limit, approval gate, DLP, anomaly detection — each scoped to a specific tool) and 4 agentic categories (Govern, Contain, Detect, Respond, framed as the question each category asks). Toggling re-renders the trace; the reader applies the controls they would themselves recommend and watches the agent route around them. Replaces the old static governance-gap table.
- **Sharpened argument across `#steelman`, `#pivot`, `#equation`.** Steelman now leads with the explicit traditional model. Pivot leads with the closed-loop framing — `script: goal → step → fail → stop` vs `agent: goal → plan → act → observe → update → retry → adapt → continue` — and states *"the difference is feedback, not speed."* Equation has an always-visible rate-race lede above the `<details>`; inside, the **revised seven-block math framework** (Probabilistic Action Graph; Goal-Directed Controller Policy; Risk as a Hitting-Time Race; Dynamic Effective Speed Ceilings; Nonlinear Detection Evidence; Total Risk with Interaction Term; AI-Native Risk Chain) — see `agentic_security_manifesto.md` Appendix A for the unabridged version.
- **Catalog-based static deploy.** `build_static.py` enumerates the 2^12 = 4096 toggle combinations under the canonical seed/capability/max-steps, deduplicates traces, and writes `docs/static/data/superset_trace.json` (449 unique paths, ~57 KB gzipped under canonical seed=7, capability=4, max-steps=8). A small JS overlay (`controls-overlay.js`) does dictionary lookups against the catalog so the page is fully interactive on GitHub Pages with no Python runtime.
- **Narrow JS-overlay exception to ADR-1.** The path-search and trace generation stay Python-only. The JS overlay is a thin lookup against the pre-rendered catalog — it does NOT re-implement the simulator. Full rationale: `aisdlc-docs/inception/7-design.md` ADR-7-3.
- **Manifesto-aligned argument.** `#steelman` and `#pivot` copy align to `agentic_security_manifesto.md` §4 / §28; `#equation` is now rendered with real LaTeX via [KaTeX](https://katex.org/) (bundled locally under `web/static/vendor/katex/`, ~600 KB total — same-origin assets, no CDN at runtime). `#source` links to the longer manifesto.

> **Anchor change for external links:** the old `#governance` section was replaced by `#controls`. Update any saved links.

## Run it locally

Requires Python 3.9+. No pip dependencies. No build step.

```bash
git clone https://github.com/rseveymant/agentic-sec-new.git
cd agentic-sec-new
python3 agentic_security_demo.py --serve
```

Then open `http://127.0.0.1:8000`.

In live mode the page shows interactive controls for `seed`, `capability`, and `max-steps`. Change them and the page re-renders against the same simulator that generates the static snapshot.

## Other CLI modes

```bash
# One side-by-side trace to stdout
python3 agentic_security_demo.py --demo

# Capability sweep table
python3 agentic_security_demo.py --monte-carlo --runs 1000

# Pre-render the static site to docs/ for GitHub Pages
python3 agentic_security_demo.py --build-static
```

`--build-static` writes a deterministic snapshot using seed 7, capability 4, max-steps 8, 500 Monte Carlo runs.

### API parameters

`/api/trace` accepts `seed`, `capability`, and `max_steps` (as in v1) plus two new optional control parameters (#7):

- **`tc=`** — comma-separated traditional control IDs. Example:
  ```bash
  curl 'http://127.0.0.1:8000/api/trace?tc=mfa_vault,rate_limit_chat'
  ```
- **`ac=`** — comma-separated agentic control IDs. Example:
  ```bash
  curl 'http://127.0.0.1:8000/api/trace?ac=govern'
  ```

Unknown IDs are silently dropped. Allowed IDs:

- Traditional (8): `mfa_vault`, `segment_vault`, `least_priv_catalog`, `audit_log`, `rate_limit_chat`, `approval_export`, `dlp_export`, `anomaly_seq`.
- Agentic (4): `govern`, `contain`, `detect`, `respond`.

## Repo layout

```
agentic-sec-new/
  agentic_security_demo.py     # CLI entry point
  build_static.py              # static-site pre-render
  simulator/                   # closed-world simulation (pure Python, deterministic)
    world.py                   # ToyEnterprise + tool catalogue
    actors.py                  # StaticAutomation + AgenticExecutor (+ Govern/Contain/Detect/Respond hooks)
    controls.py                # Control + ControlSet + apply_to_tool_call (#7)
    superset.py                # 4096-combination catalog builder (#7)
    monte_carlo.py             # capability sweep aggregation
    trace.py                   # data classes
    encode.py                  # JSON wire shape
  web/
    server.py                  # stdlib HTTP server (live mode)
    static/                    # HTML / CSS / JS source
      vendor/katex/            # KaTeX 0.16.9 bundled locally for equation rendering (#7)
  docs/                        # static deploy output (GitHub Pages serves from here)
  agentic_security_manifesto.md  # long-form companion argument

  v1/                          # original prototype, archived for reference
  aisdlc-docs/                 # inception planning docs
```

## How the static deploy works

`python3 agentic_security_demo.py --build-static` runs the simulator with the canonical seed and writes:

- `docs/index.html`
- `docs/static/styles.css`
- `docs/static/app.js`
- `docs/static/controls-overlay.js`            — JS catalog lookup for the static-mode `#controls` section (#7)
- `docs/static/data/default_trace.json`        — one paired trace
- `docs/static/data/monte_carlo.json`          — capability sweep over 500 runs
- `docs/static/data/superset_trace.json`       — pre-rendered catalog of all 4096 toggle combinations, deduplicated. Size budget: ~150 KB gzipped; canonical seed runs at ~57 KB gzipped (449 unique paths). (#7)
- `docs/static/vendor/katex/`                  — KaTeX 0.16.9 (CSS + JS + 20 woff2 fonts, ~600 KB total). Same-origin assets; no CDN at runtime. (#7)

Pushing to `main` triggers GitHub Pages to redeploy from `docs/`. To enable Pages: repo Settings → Pages → Source: Deploy from a branch → Branch `main` / `/docs`.

The browser detects whether `api/trace` is reachable (live mode) and falls back to the pre-rendered JSON otherwise (static mode). Same wire shape, two delivery paths. Live mode shows interactive parameter controls and re-fetches `/api/trace?tc=…&ac=…` per toggle change; static mode resolves the same toggle state against `superset_trace.json` via `controls-overlay.js` and renders the matching trace without a Python runtime.

## Why this exists

If you're inclined to say *"this is just curl, faster,"* the page is meant for you. Read `aisdlc-docs/inception/1-requirements.md` for the longer argument. The TL;DR is the title.

## About

By **Ryan Sevey**. Personal project. Not affiliated with any company.

License: [MIT](LICENSE).

The simulation is deterministic per seed. Change the seed in the live UI or in `build_static.py` (constants near the top) and re-run.
