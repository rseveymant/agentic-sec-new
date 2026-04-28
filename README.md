# Same Primitives. New Control Loop.

A small simulation showing why agentic AI risk is not just *"the same attacks, faster."* Same primitives, new control loop, new risk model.

**Live (hosted, static):** https://rseveymant.github.io/agentic-sec-new/
**Source:** this repo. The `v1/` directory holds the original 859-line single-file prototype as a reference snapshot.

## What this is

A web page (live and static-deploy) with two actors that pursue the same goal in a closed-world toy enterprise. They use the same starting credentials and the same tool catalogue. They make the same first call. They both get a 403.

The static script stops. The agent treats the failure as feedback, searches internal context, finds an alternate approved-looking path through legitimate tools, and reaches the goal.

A Monte Carlo curve then shows that capability bends the agent's success rate but leaves the static actor flat — the difference is path quality, not speed. Failure becomes feedback.

The artifact exists to replace a recurring verbal argument ("curl is still curl") with something link-able and screenshottable.

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

## Repo layout

```
agentic-sec-new/
  agentic_security_demo.py     # CLI entry point
  build_static.py              # static-site pre-render
  simulator/                   # closed-world simulation (pure Python, deterministic)
    world.py                   # ToyEnterprise + tool catalogue
    actors.py                  # StaticAutomation + AgenticExecutor
    monte_carlo.py             # capability sweep aggregation
    trace.py                   # data classes
    encode.py                  # JSON wire shape
  web/
    server.py                  # stdlib HTTP server (live mode)
    static/                    # HTML / CSS / JS source
  docs/                        # static deploy output (GitHub Pages serves from here)
  v1/                          # original prototype, archived for reference
  aisdlc-docs/                 # inception planning docs
```

## How the static deploy works

`python3 agentic_security_demo.py --build-static` runs the simulator once with the canonical seed and writes:

- `docs/index.html`
- `docs/static/styles.css`
- `docs/static/app.js`
- `docs/static/data/default_trace.json`  — one paired trace
- `docs/static/data/monte_carlo.json`     — capability sweep over 500 runs

Pushing to `main` triggers GitHub Pages to redeploy from `docs/`. To enable Pages: repo Settings → Pages → Source: Deploy from a branch → Branch `main` / `/docs`.

The browser detects whether `api/trace` is reachable (live mode) and falls back to the pre-rendered JSON otherwise (static mode). Same wire shape, two delivery paths. Live mode shows interactive parameter controls; static mode shows a "for full interactivity, run locally" link to this repo.

## Why this exists

If you're inclined to say *"this is just curl, faster,"* the page is meant for you. Read `aisdlc-docs/inception/1-requirements.md` for the longer argument. The TL;DR is the title.

## About

By **Ryan Sevey**. Personal project. Not affiliated with any company.

License: [MIT](LICENSE).

The simulation is deterministic per seed. Change the seed in the live UI or in `build_static.py` (constants near the top) and re-run.
