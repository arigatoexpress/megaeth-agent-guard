# MegaETH Research Snapshot

Checked on April 30, 2026.

## Official Network Facts

Official MegaETH mainnet docs list:

- Chain ID: `4326` / `0x10e6`
- Public RPC: `https://mainnet.megaeth.com/rpc`
- Native gas token: `ETH`
- Mini-block cadence: `10ms`
- EVM block cadence: `1s`
- Block explorers: `https://mega.etherscan.io` and `https://megaeth.blockscout.com`

Sources:

- `https://docs.megaeth.com/frontier`
- `https://docs.megaeth.com/user-guide/connect`
- `https://docs.megaeth.com/developer-docs/overview-2/realtime-api`

## Contracts of Interest

From the official mainnet docs:

| Contract | Address |
| --- | --- |
| MEGA ERC-20 | `0x28B7E77f82B25B95953825F1E3eA0E36c1c29861` |
| USDM on MegaETH | `0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7` |
| WETH9 | `0x4200000000000000000000000000000000000006` |
| Multicall3 | `0xcA11bde05977b3631167028862bE2a173976CA11` |
| L1 Standard Bridge | `0x0CA3A2FBC3D770b578223FBB6b062fa875a2eE75` |

## App Discovery

Rabbithole is the useful app-discovery surface for this build:

- Portal: `https://rabbithole.megaeth.com`
- Chain stats: `https://rabbithole.megaeth.com/api/data/chain`
- Featured apps: `https://rabbithole.megaeth.com/api/featured-apps`
- Discover list: `https://rabbithole.megaeth.com/api/discover/list`

Live reads during development showed the app directory as a broad surface across
trading, infra, culture/social, gaming, novel assets, yield/credit, and consumer
DeFi. The guard treats this as public discovery data only. It does not trust any
catalog row as permission to spend, sign, post, deposit, bridge, or wager.

## Build Implications

MegaETH's Realtime API makes state reads, logs, and receipts available at
mini-block freshness. That is excellent for agents, but it raises the cost of a
bad tool call. The guard therefore places policy before wallet automation:

1. Verify network and source context.
2. Classify app and action type.
3. Deny secrets, prompt injection, write methods, and spend semantics.
4. Emit a receipt hash.
5. Only then permit read-only or simulation work.

## What This Does Not Claim

- It does not claim financial advice.
- It does not claim that third-party MegaETH apps are safe.
- It does not submit transactions.
- It does not provide live Zama or Aztec proofs yet.
- It does not automate Robinhood or any real brokerage flow.

