# MegaETH Agent Guard

> Read-only app scout and intent firewall for autonomous agents on MegaETH mainnet.

[![CI](https://github.com/arigatoexpress/megaeth-agent-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/arigatoexpress/megaeth-agent-guard/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

## What this does

MegaETH's real-time execution makes onchain apps feel instant — which means an AI agent can also make wallet mistakes instantly. This repo is a pre-wallet safety layer: it reads live MegaETH network and app context, evaluates agent intents, blocks signing and spending flows by default, checks URLs for spoof risk, and emits public receipt hashes for every decision.

## Quick start

```bash
git clone https://github.com/arigatoexpress/megaeth-agent-guard.git
cd megaeth-agent-guard
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m megaeth_agent_guard.app
```

Open `http://127.0.0.1:8108`.

Try the CLI:

```bash
python3 scripts/mega_guard.py catalog
python3 scripts/mega_guard.py scout --live --discover-limit 20
python3 scripts/mega_guard.py domain https://rabbithole.megaeth.com
python3 scripts/mega_guard.py evaluate --intent-json '{"action":"bridge_eth","mode":"live_transaction","value_eth":0.001,"requires_signature":true}'
```

## Architecture

```
Agent intent ──▶ Policy engine ──▶ allow / review / deny
                     │
                     +-- MegaETH RPC scout (read-only)
                     +-- App catalog and URL registry
                     +-- Prompt-injection / secret-egress detection
                     +-- Receipt hash generation
```

## Key features

- **Intent scoring** — `allow`, `review`, or `deny` verdicts with receipt hashes.
- **Read-only scout** — Live MegaETH RPC and Rabbithole app catalog reads.
- **URL guard** — Curated MegaETH/app domain registry with spoof detection.
- **Prompt injection detection** — Blocks secret-egress language before wallet access.
- **No custody** — Refuses signing, broadcasting, bridging, and swapping by default.

## Tech stack

- Python 3.10+
- Flask 3.0+
- web3.py, eth-utils
- pytest, ruff

## API surface

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Service mode and safety flags |
| `GET /api/catalog` | Static MegaETH network/app/intent catalog |
| `GET /api/scout?live=1` | Live read-only RPC and Rabbithole scout |
| `POST /api/evaluate` | Intent policy decision and receipt hash |
| `GET /api/domain?url=...` | URL/domain spoof guard |
| `GET /api/intents` | Demo intent templates and budget caps |

## Safety boundary

This repo is **mainnet-aware but not mainnet-spending**:

- No private keys, signing, or broadcasting.
- No swaps, bridges, deposits, wagers, or paid app actions.
- No real Robinhood actions.
- No secret-bearing output.
- Live mode only calls public HTTP endpoints and read-only JSON-RPC methods.

## Tests

```bash
pytest -q
python3 -m compileall src scripts
ruff check .
```

## Agent collaborators

See [AGENTS.md](AGENTS.md) for project structure, safety boundaries, and development conventions.

## License

[MIT](LICENSE).
