# MegaETH Agent Guard

MegaETH Agent Guard is a read-only app scout and intent firewall for autonomous
agents operating around MegaETH mainnet.

The thesis is simple: MegaETH's real-time execution makes onchain apps feel
instant, which means an AI agent can also make wallet mistakes instantly. This
repo gives the ecosystem a pre-wallet safety layer: it reads live MegaETH
network/app context, evaluates agent intents, blocks signing/spending flows by
default, checks MegaETH-looking URLs for spoof risk, and emits public receipt
hashes for every decision.

## What It Does

- Verifies MegaETH mainnet facts from official docs and public RPC.
- Reads Rabbithole app/catalog endpoints without wallet automation.
- Scores agent intents as `allow`, `review`, or `deny`.
- Refuses signing, raw transaction submission, bridges, swaps, deposits, wagers,
  token launches, and paid social/game actions by default.
- Detects prompt-injection and secret-egress language before an agent reaches a
  wallet.
- Checks app URLs against a curated MegaETH/app domain registry.
- Ships a usable dashboard and JSON API for demos.

## Why It Can Win

Most hackathon demos show an agent doing a transaction. This one shows an agent
earning the right not to do one.

MegaETH is fast enough for real-time trading, games, social apps, and agent
markets. That creates a new security problem: agent intent needs to be evaluated
at app speed, with source provenance and visible receipts. MegaETH Agent Guard is
a small, composable primitive for that job.

## Safety Boundary

This repo is mainnet-aware but not mainnet-spending.

- No private keys.
- No transaction signing.
- No transaction broadcasting.
- No swaps, bridges, deposits, wagers, or paid app actions.
- No real Robinhood actions.
- No secret-bearing output.

Live mode only calls public HTTP endpoints, read-only JSON-RPC methods, and
ERC-20 `balanceOf` through `eth_call`.

## Quickstart

```bash
cd /Users/aribs/Code/megaeth-agent-guard
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m megaeth_agent_guard.app
```

Open `http://127.0.0.1:8108`.

## CLI

```bash
python3 scripts/mega_guard.py catalog
python3 scripts/mega_guard.py scout --live --discover-limit 20
python3 scripts/mega_guard.py domain https://rabbithole.megaeth.com
python3 scripts/mega_guard.py evaluate --intent-json '{"action":"bridge_eth","mode":"live_transaction","value_eth":0.001,"requires_signature":true}'
```

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Service mode and safety flags |
| `GET /api/frontend-contract` | Browser-smoke contract for required UI selectors, route readbacks, and disabled external effects |
| `GET /api/catalog` | Static MegaETH network/app/intent catalog |
| `GET /api/scout?live=1` | Live read-only RPC and Rabbithole scout |
| `POST /api/evaluate` | Intent policy decision and receipt hash |
| `GET /api/domain?url=...` | URL/domain spoof guard |
| `GET /api/intents` | Demo intent templates and budget caps |

## Current MegaETH Anchors

- Mainnet docs: `https://docs.megaeth.com/frontier`
- Connect docs: `https://docs.megaeth.com/user-guide/connect`
- Chain ID: `4326`
- Public RPC: `https://mainnet.megaeth.com/rpc`
- Native gas token: `ETH`
- MEGA token: `0x28B7E77f82B25B95953825F1E3eA0E36c1c29861`
- USDM token: `0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7`
- WETH9: `0x4200000000000000000000000000000000000006`
- L1 Standard Bridge: `0x0CA3A2FBC3D770b578223FBB6b062fa875a2eE75`
- Rabbithole portal: `https://rabbithole.megaeth.com`

## Tests

```bash
python3 -m pytest -q
python3 -m compileall src scripts
ruff check .
gitleaks detect --no-git --source . --redact --verbose
```

## Roadmap

1. Add a Realtime API watcher for mini-block/log subscriptions in read-only mode.
2. Add unsigned transaction preview adapters for selected MegaETH apps.
3. Add x402-style mock payment gates for paid AI reports.
4. Add Zama/Aztec proof envelopes for private risk claims without live proof
   overclaiming.
5. Add a signed policy receipt contract on MegaETH testnet only, then consider
   mainnet after explicit operator review.
