# MegaETH Agent Guard — Agent Guide

## What this repo does

MegaETH Agent Guard is a **read-only app scout and intent firewall** for autonomous agents operating around MegaETH mainnet. It evaluates agent intents, blocks risky signing/spending flows by default, and emits deterministic receipt hashes for every decision.

## Key directories and files

```
megaeth-agent-guard/
├── src/megaeth_agent_guard/   # Application code
│   ├── app.py                 # Flask web server and API routes
│   ├── policy.py              # Intent policy engine
│   ├── scout.py               # MegaETH RPC and Rabbithole scout
│   ├── domain_guard.py        # URL/domain spoof detection
│   └── catalog.py             # MegaETH network and app catalog
├── scripts/                   # CLI and utility scripts
│   ├── mega_guard.py          # CLI entrypoint
│   └── browser_smoke.py       # Browser smoke tests
├── docs/                      # Safety docs, demo script, research
├── tests/                     # pytest suite
└── pyproject.toml             # Dependencies and project config
```

## How to run tests / dev server

```bash
# Install
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'

# Tests
pytest -q
python3 -m compileall src scripts
ruff check .

# Dev server
python3 -m megaeth_agent_guard.app
# open http://127.0.0.1:8108
```

## Safety boundaries (DO NOT CHANGE)

1. **No transaction signing or broadcasting** — The guard must never sign or send transactions.
2. **No custody** — No private keys, mnemonics, or wallet seed phrases in code or logs.
3. **Read-only live mode** — Public HTTP endpoints and read-only JSON-RPC only.
4. **No paid actions** — No swaps, bridges, deposits, wagers, or token launches by default.
5. **No secret egress** — Prompt-injection detection must block secret-bearing output.

## Current status

- Experimental proof-of-concept for MegaETH mainnet safety.
- Live read-only scout and intent evaluation working.
- Realtime API watcher and unsigned transaction preview adapters planned.
