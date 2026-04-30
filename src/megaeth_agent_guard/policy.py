"""Agent-intent policy engine for MegaETH.

MegaETH makes onchain feedback fast enough that agents need guardrails before
wallet calls, not after. This module accepts plain intent payloads and returns a
machine-readable decision plus a public receipt hash.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

READ_ONLY_RPC_METHODS = {
    "eth_blockNumber",
    "eth_call",
    "eth_callMany",
    "eth_chainId",
    "eth_createAccessList",
    "eth_estimateGas",
    "eth_feeHistory",
    "eth_gasPrice",
    "eth_getBalance",
    "eth_getBlockByNumber",
    "eth_getCode",
    "eth_getLogs",
    "eth_getLogsWithCursor",
    "eth_getStorageAt",
    "eth_getTransactionByHash",
    "eth_getTransactionCount",
    "eth_getTransactionReceipt",
    "net_version",
    "web3_clientVersion",
}

DENIED_RPC_METHODS = {
    "eth_sendRawTransaction",
    "eth_sendTransaction",
    "eth_sign",
    "eth_signTransaction",
    "eth_signTypedData",
    "eth_signTypedData_v3",
    "eth_signTypedData_v4",
    "personal_sign",
    "realtime_sendRawTransaction",
    "wallet_addEthereumChain",
    "wallet_sendCalls",
    "wallet_switchEthereumChain",
}

SAFE_ACTIONS = {
    "catalog",
    "discover",
    "eth_call",
    "eth_chainId",
    "eth_getBalance",
    "eth_getLogs",
    "evaluate",
    "monitor",
    "probe",
    "query",
    "quote",
    "quote_swap",
    "read",
    "research",
    "risk_score",
    "risk_score_deposit",
    "simulate",
    "simulate_swap",
    "unsigned_quote",
}

SPEND_ACTION_TERMS = {
    "buy",
    "bridge",
    "deposit",
    "execute",
    "install",
    "mint",
    "post",
    "purchase",
    "send",
    "sign",
    "stake",
    "swap",
    "transfer",
    "wager",
    "withdraw",
}

SIMULATION_PREFIXES = ("quote", "read", "research", "risk_score", "simulate", "unsigned")

PROMPT_INJECTION_PATTERNS = (
    r"ignore (all )?(previous|prior) instructions",
    r"bypass (the )?(guard|policy|wallet|approval)",
    r"disable (the )?(guard|policy|safety)",
    r"do not (log|record|tell|show)",
    r"secretly",
    r"without (user|operator) (approval|confirmation)",
)

SECRET_EGRESS_PATTERNS = (
    r"\bprivate[-_ ]?key\b",
    r"\bseed phrase\b",
    r"\bmnemonic\b",
    r"\bapi[-_ ]?key\b",
    r"\baccess[-_ ]?token\b",
    r"\bsecret\b",
    r"0x[a-fA-F0-9]{64}",
)

DEFAULT_BUDGET_CAPS = {
    "max_value_eth": "0",
    "max_value_usd": "0",
    "allow_mainnet_writes": False,
    "allow_wallet_signatures": False,
    "allow_paid_social_or_game_actions": False,
}


@dataclass(frozen=True)
class PolicyDecision:
    decision: str
    severity: str
    action: str
    mode: str
    blockers: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    allowed_next_steps: tuple[str, ...] = field(default_factory=tuple)
    receipt_hash: str = ""
    generated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_intent(
    intent: dict[str, Any] | None,
    budget: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate an agent intent and return a wire-safe decision dictionary."""

    payload = normalize_intent(intent or {})
    caps = {**DEFAULT_BUDGET_CAPS, **(budget or {})}
    blockers: list[str] = []
    warnings: list[str] = []

    action = payload["action"]
    mode = payload["mode"]
    method = payload["method"]
    prompt_text = payload["prompt_text"]
    value_eth = parse_decimal(payload.get("value_eth", "0"))

    if method:
        if method in DENIED_RPC_METHODS or method not in READ_ONLY_RPC_METHODS:
            blockers.append(f"rpc method is not read-only: {method}")

    if contains_pattern(prompt_text, SECRET_EGRESS_PATTERNS):
        blockers.append("intent attempts to expose or use a secret")

    if contains_pattern(prompt_text, PROMPT_INJECTION_PATTERNS):
        blockers.append("prompt-injection language detected")

    if action not in SAFE_ACTIONS and not action.startswith(SIMULATION_PREFIXES):
        if action_has_spend_term(action):
            blockers.append(f"live action is out of policy: {action}")
        else:
            warnings.append(f"unknown action requires operator review: {action}")

    if action_has_spend_term(action) and not action.startswith(SIMULATION_PREFIXES):
        blockers.append(f"action implies a write or spend: {action}")

    if value_eth > Decimal(str(caps["max_value_eth"])):
        blockers.append(f"value exceeds cap: {value_eth} ETH > {caps['max_value_eth']} ETH")

    if payload["requires_signature"] and not caps["allow_wallet_signatures"]:
        blockers.append("wallet signature requested while signatures are disabled")

    if payload["chain_id"] and payload["chain_id"] != 4326:
        warnings.append(f"unexpected chain_id for MegaETH guard: {payload['chain_id']}")

    if (
        mode in {"live_transaction", "wallet_write", "mainnet_write"}
        and not caps["allow_mainnet_writes"]
    ):
        blockers.append("mainnet write mode is disabled")

    if mentions_paid_game_or_social(prompt_text) and not caps["allow_paid_social_or_game_actions"]:
        blockers.append("paid game/social action requires explicit operator approval")

    if blockers:
        decision = "deny"
        has_critical_blocker = any("secret" in item or "signature" in item for item in blockers)
        severity = "critical" if has_critical_blocker else "high"
        allowed_next_steps = (
            "Convert the request into an unsigned quote, read, or simulation.",
            "Attach verified app and contract metadata before reconsidering.",
            "Keep private keys and wallet signatures outside the agent process.",
        )
    elif warnings:
        decision = "review"
        severity = "medium"
        allowed_next_steps = (
            "Show this preview to the operator.",
            "Require a fresh human approval before any wallet-facing step.",
        )
    else:
        decision = "allow"
        severity = "low"
        allowed_next_steps = (
            "Run read-only RPC/catalog query.",
            "Record the receipt hash with the agent trace.",
        )

    generated_at = int(time.time())
    receipt_hash = build_receipt_hash(
        {
            "payload": payload,
            "decision": decision,
            "severity": severity,
            "blockers": blockers,
            "warnings": warnings,
            "budget": caps,
        }
    )
    return PolicyDecision(
        decision=decision,
        severity=severity,
        action=action,
        mode=mode,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        allowed_next_steps=tuple(allowed_next_steps),
        receipt_hash=receipt_hash,
        generated_at=generated_at,
    ).to_dict()


def normalize_intent(intent: dict[str, Any]) -> dict[str, Any]:
    action = str(intent.get("action") or intent.get("type") or "read").strip()
    method = str(intent.get("method") or "").strip()
    mode = str(intent.get("mode") or ("read" if action in SAFE_ACTIONS else "unknown")).strip()
    prompt_parts = [
        str(intent.get("prompt") or ""),
        str(intent.get("message") or ""),
        str(intent.get("description") or ""),
    ]
    prompt_text = "\n".join(part for part in prompt_parts if part).strip()
    value_eth = intent.get("value_eth", intent.get("eth_value", intent.get("value", "0")))
    return {
        "action": action,
        "method": method,
        "mode": mode,
        "prompt_text": prompt_text,
        "app": str(intent.get("app") or intent.get("app_hint") or ""),
        "chain_id": normalize_chain_id(intent.get("chain_id")),
        "value_eth": str(value_eth or "0"),
        "requires_signature": bool(intent.get("requires_signature") or intent.get("sign")),
        "raw": redact_intent(intent),
    }


def normalize_chain_id(value: Any) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, str) and value.startswith("0x"):
        return int(value, 16)
    return int(value)


def redact_intent(intent: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in intent.items():
        lowered = str(key).lower()
        secret_markers = ("secret", "private", "mnemonic", "seed", "token", "key")
        if any(marker in lowered for marker in secret_markers):
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


def action_has_spend_term(action: str) -> bool:
    lowered = action.lower().replace("-", "_")
    return any(term in lowered.split("_") or term in lowered for term in SPEND_ACTION_TERMS)


def mentions_paid_game_or_social(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ("wager", "loot", "buyback", "post for me", "paid game"))


def contains_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def parse_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value or "0"))
    except InvalidOperation:
        return Decimal("0")


def build_receipt_hash(data: dict[str, Any]) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
