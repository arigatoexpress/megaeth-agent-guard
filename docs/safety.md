# Safety Model

MegaETH Agent Guard assumes an autonomous agent may be fast, useful, and wrong.
The guard's job is to stop wrong actions before they become wallet requests.

## Assets

- User funds and wallet signing authority.
- Private keys, seed phrases, API tokens, and local secrets.
- App account state and identity.
- Public reputation from social/game actions.
- Integrity of source provenance and decision receipts.

## Default Deny

The following are denied by default:

- `eth_sendRawTransaction`
- `eth_sendTransaction`
- `eth_sign`
- `eth_signTransaction`
- `eth_signTypedData*`
- `personal_sign`
- `realtime_sendRawTransaction`
- wallet chain switching or wallet send calls
- live swaps, bridges, deposits, withdrawals, wagers, token launches, paid skill
  installs, or social posts

## Allowed by Default

The following are allowed when the intent is otherwise clean:

- Network reads such as `eth_chainId`, `eth_blockNumber`, and `eth_gasPrice`
- Public balance and code reads
- `eth_call`, `eth_estimateGas`, `eth_getLogs`, and cursor log reads
- Rabbithole catalog reads
- URL/domain evaluation
- Unsigned quotes and simulations

## Prompt-Injection Checks

The guard blocks intents containing phrases such as:

- `ignore previous instructions`
- `bypass the guard`
- `do not log`
- `secretly`
- `without operator approval`

## Secret-Egress Checks

The guard blocks private-key, seed phrase, mnemonic, API-key, token, and raw
32-byte hex secret patterns. Secret-bearing fields are redacted in normalized
payloads.

## Receipt Hashes

Every policy decision includes a `sha256:` receipt over:

- normalized intent
- decision
- severity
- blockers
- warnings
- budget caps

This is not a legal attestation or proof of execution. It is a lightweight,
publicly shareable audit marker for agent traces.

