#!/usr/bin/env python3
"""Pre-render simulator output into static JSON files for GitHub Pages deployment.

Writes (idempotent, deterministic):
    web/static/data/default_trace.json
    web/static/data/monte_carlo.json

Then optionally copies web/static/* to an output directory (default web/dist/)
so the site can be served from GitHub Pages without a Python runtime.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from typing import Optional, Sequence

from simulator.encode import monte_carlo_to_dict, trace_to_dict


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_STATIC_DIR = os.path.join(REPO_ROOT, "web", "static")
DEFAULT_OUT_DIR = os.path.join(REPO_ROOT, "docs")

# Canonical defaults for the static deploy.
CANONICAL_SEED = 7
CANONICAL_CAPABILITY = 4
CANONICAL_MAX_STEPS = 8
CANONICAL_MC_RUNS = 500


def write_data_files() -> None:
    data_dir = os.path.join(WEB_STATIC_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)

    trace = trace_to_dict(
        seed=CANONICAL_SEED,
        capability=CANONICAL_CAPABILITY,
        max_steps=CANONICAL_MAX_STEPS,
    )
    mc = monte_carlo_to_dict(runs=CANONICAL_MC_RUNS, max_steps=CANONICAL_MAX_STEPS)

    trace_path = os.path.join(data_dir, "default_trace.json")
    mc_path = os.path.join(data_dir, "monte_carlo.json")

    with open(trace_path, "w") as f:
        json.dump(trace, f, indent=2, sort_keys=False)
        f.write("\n")
    with open(mc_path, "w") as f:
        json.dump(mc, f, indent=2, sort_keys=False)
        f.write("\n")

    print(f"Wrote: {os.path.relpath(trace_path, REPO_ROOT)}")
    print(f"Wrote: {os.path.relpath(mc_path, REPO_ROOT)}")


def copy_to_dist(out_dir: str) -> None:
    """Lay out files so relative paths resolve under both local server and GitHub Pages.

    out_dir/
      index.html
      static/
        styles.css
        app.js
        data/
          default_trace.json
          monte_carlo.json
    """
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    shutil.copy(os.path.join(WEB_STATIC_DIR, "index.html"), out_dir)

    static_dest = os.path.join(out_dir, "static")
    os.makedirs(static_dest, exist_ok=True)
    for entry in sorted(os.listdir(WEB_STATIC_DIR)):
        if entry == "index.html":
            continue
        src = os.path.join(WEB_STATIC_DIR, entry)
        dst = os.path.join(static_dest, entry)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)

    print(f"Copied to {os.path.relpath(out_dir, REPO_ROOT)}/ (index.html + static/)")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pre-render static assets for deployment.")
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT_DIR,
        help=f"Output directory (default: {os.path.relpath(DEFAULT_OUT_DIR, REPO_ROOT)}).",
    )
    parser.add_argument(
        "--data-only",
        action="store_true",
        help="Only write JSON data files; skip copying to out dir.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    write_data_files()
    if not args.data_only:
        copy_to_dist(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
