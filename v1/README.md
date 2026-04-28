# Agentic Security Control-Loop Demo

This is a safe, closed-world Python simulation for explaining why agentic AI security is not merely “the same attacks, faster.”

It compares two actors using the same fictional internal tools:

1. **Static automation**: tries one direct path, receives `403 Forbidden`, and stops.
2. **Toy agentic executor**: receives the same `403`, treats it as feedback, searches internal context, remembers a useful handle, and tries an alternate legitimate-looking tool path.

The demo has no real network access, no real exploitation, and no real secrets. It is intentionally a toy model.

## Run as CLI

```bash
python agentic_security_demo.py --demo
```

## Run the Monte Carlo capability sweep

```bash
python agentic_security_demo.py --monte-carlo --runs 1000
```

## Run as a local web app

```bash
python agentic_security_demo.py --serve
```

Then open:

```text
http://127.0.0.1:8000
```

## The message it demonstrates

The primitive did not change: both actors make ordinary HTTP-like fictional tool calls.

The control loop changed:

```text
Static automation: Goal → fixed step → error → stop
Agentic execution: Goal → tool → observation → memory → adaptation → retry
```

The risk is not `curl`. The risk is who or what decides the next `curl`.
