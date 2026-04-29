#!/usr/bin/env python3
"""Local HTTP server for the agentic-sec demo (stdlib only).

Routes per ADR-3:
    GET /                              → web/static/index.html (placeholder until Unit C lands)
    GET /static/<file>                 → file under web/static/
    GET /static/data/<file>.json       → pre-rendered file under web/static/data/
    GET /api/trace                     → trace JSON envelope
    GET /api/monte-carlo               → monte carlo JSON envelope
    Anything else                      → 404

Query parameters are clamped server-side per ADR-3 ranges. No request logging
to stdout (keeps stage demo console quiet per Story 4 constraint).
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List, Optional
from urllib.parse import parse_qs, urlparse

from simulator.actors import AgenticExecutor, StaticAutomation
from simulator.controls import CONTROL_BY_ID, ControlSet
from simulator.encode import monte_carlo_to_dict, trace_to_dict
from simulator.world import DEFAULT_GOAL, DEFAULT_IDENTITY, ToyEnterprise


WEB_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


PLACEHOLDER_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Agentic-Sec Demo (Unit C placeholder)</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 720px; margin: 4rem auto; padding: 0 1.5rem; color: #10243d; line-height: 1.5; }
    code { background: #f6f9fc; padding: 0.1em 0.3em; border-radius: 4px; }
    a { color: #149c91; }
  </style>
</head>
<body>
  <h1>Agentic-Sec Demo</h1>
  <p>The full UI lands in <strong>Unit C</strong> (issue #4). The simulation API is live now:</p>
  <ul>
    <li><a href="/api/trace">/api/trace</a> &nbsp;—&nbsp; <code>?seed=N&amp;capability=N&amp;max_steps=N</code></li>
    <li><a href="/api/monte-carlo">/api/monte-carlo</a> &nbsp;—&nbsp; <code>?runs=N&amp;max_steps=N</code></li>
  </ul>
  <p>Repo: <a href="https://github.com/rseveymant/agentic-sec-new">github.com/rseveymant/agentic-sec-new</a></p>
</body>
</html>
"""


def _clamp_int(raw: Optional[str], default: int, lo: int, hi: int) -> int:
    if raw is None:
        return default
    try:
        return max(lo, min(hi, int(raw)))
    except ValueError:
        return default


def _parse_control_ids(raw: Optional[str], kind: str) -> List[str]:
    """Parse a comma-separated list of control IDs for `tc` or `ac`.

    Filters against `CONTROL_BY_ID`; silently drops unknown IDs and IDs whose
    canonical kind does not match `kind` (so `tc=govern` is dropped).
    """
    if not raw:
        return []
    out: List[str] = []
    seen: set = set()
    for token in raw.split(","):
        cid = token.strip()
        if not cid or cid in seen:
            continue
        ctrl = CONTROL_BY_ID.get(cid)
        if ctrl is None or ctrl.kind != kind:
            continue
        seen.add(cid)
        out.append(cid)
    return out


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib naming
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/":
            self._serve_index()
        elif path.startswith("/static/"):
            self._serve_static(path)
        elif path == "/api/trace":
            self._serve_trace(params)
        elif path == "/api/monte-carlo":
            self._serve_monte_carlo(params)
        else:
            self._send_404()

    def _serve_index(self) -> None:
        index_path = os.path.join(WEB_STATIC_DIR, "index.html")
        if os.path.isfile(index_path):
            self._send_file(index_path, "text/html; charset=utf-8")
        else:
            self._send_bytes(PLACEHOLDER_HTML.encode("utf-8"), "text/html; charset=utf-8")

    def _serve_static(self, path: str) -> None:
        rel = path[len("/static/") :]
        # Defense against path traversal: normalize and verify the result stays under WEB_STATIC_DIR.
        full = os.path.normpath(os.path.join(WEB_STATIC_DIR, rel))
        if not (full == WEB_STATIC_DIR or full.startswith(WEB_STATIC_DIR + os.sep)):
            self._send_404()
            return
        if not os.path.isfile(full):
            self._send_404()
            return
        ext = os.path.splitext(full)[1].lower()
        content_type = {
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".html": "text/html; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }.get(ext, "application/octet-stream")
        self._send_file(full, content_type)

    def _serve_trace(self, params: dict) -> None:
        seed = _clamp_int(params.get("seed", [None])[0], default=7, lo=0, hi=99999)
        capability = _clamp_int(params.get("capability", [None])[0], default=4, lo=1, hi=5)
        max_steps = _clamp_int(params.get("max_steps", [None])[0], default=8, lo=2, hi=20)
        tc_ids = _parse_control_ids(params.get("tc", [None])[0], kind="traditional")
        ac_ids = _parse_control_ids(params.get("ac", [None])[0], kind="agentic")
        controls = ControlSet(enabled=frozenset(tc_ids + ac_ids))

        # Per-request working identity. Drop catalog:read when least_priv_catalog
        # is enabled. DEFAULT_IDENTITY is never mutated.
        working_identity = DEFAULT_IDENTITY
        if controls.is_enabled("least_priv_catalog"):
            working_identity = replace(
                DEFAULT_IDENTITY,
                scopes=frozenset(DEFAULT_IDENTITY.scopes - {"catalog:read"}),
            )

        # Fresh RNGs per actor for determinism (matches monte_carlo.run_pair).
        static_rng = random.Random(seed)
        agent_rng = random.Random(seed)
        static_env = ToyEnterprise(static_rng)
        agent_env = ToyEnterprise(agent_rng)

        static_actor = StaticAutomation(static_env, DEFAULT_IDENTITY, static_rng)
        agent_actor = AgenticExecutor(
            agent_env,
            working_identity,
            agent_rng,
            capability=capability,
            max_steps=max_steps,
            controls=controls,
        )
        static_result = static_actor.run(DEFAULT_GOAL)
        agent_result = agent_actor.run(DEFAULT_GOAL)

        envelope = trace_to_dict(
            seed=seed,
            capability=capability,
            max_steps=max_steps,
            static=static_result,
            agent=agent_result,
        )
        envelope["params"]["tc"] = sorted(tc_ids)
        envelope["params"]["ac"] = sorted(ac_ids)
        self._send_json(envelope)

    def _serve_monte_carlo(self, params: dict) -> None:
        runs = _clamp_int(params.get("runs", [None])[0], default=500, lo=50, hi=5000)
        max_steps = _clamp_int(params.get("max_steps", [None])[0], default=8, lo=2, hi=20)
        envelope = monte_carlo_to_dict(runs=runs, max_steps=max_steps)
        self._send_json(envelope)

    def _send_file(self, path: str, content_type: str) -> None:
        with open(path, "rb") as f:
            data = f.read()
        self._send_bytes(data, content_type)

    def _send_bytes(self, data: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, obj: dict) -> None:
        data = json.dumps(obj).encode("utf-8")
        self._send_bytes(data, "application/json; charset=utf-8")

    def _send_404(self) -> None:
        body = b"404 Not Found"
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        # Quiet stage console.
        return


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = HTTPServer((host, port), DemoHandler)
    print(f"Serving demo at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    serve()
