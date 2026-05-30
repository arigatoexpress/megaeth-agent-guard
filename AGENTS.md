# MegaETH Agent Guard — Agent Notes

## What This Is

A read-only app scout and intent firewall for autonomous agents operating on MegaETH mainnet. Pre-wallet safety layer that checks live network context, evaluates agent intents, and blocks signing/spending flows by default.

## Key Paths

| Path | Purpose |
|------|---------|
| `src/megaeth_agent_guard/` | Core guard engine |
| `src/megaeth_agent_guard/scout.py` | Live app/network scout |
| `src/megaeth_agent_guard/intent.py` | Intent evaluation |
| `src/megaeth_agent_guard/firewall.py` | Signing/spending blocks |
| `tests/` | Test suite |
| `docs/` | Architecture and runbooks |

## Dev Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Safety Boundaries

- This is a **read-only** scout by design. Do not add transaction signing.
- Do not commit real RPC endpoints with credentials.
- URL spoof checks are heuristic — verify with manual review before acting.

## Status

Active prototype. MegaETH mainnet integration verified.
