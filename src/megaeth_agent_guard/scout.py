"""Read-only MegaETH scout.

This module only performs public HTTP reads, read-only JSON-RPC calls, and
ERC-20 ``balanceOf`` via ``eth_call``. It deliberately refuses send/sign RPC
methods even if a caller asks for them.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from decimal import Decimal
from typing import Any

from megaeth_agent_guard.catalog import (
    CURATED_APPS,
    MEGAETH_CHAIN_ID,
    MEGAETH_MAINNET_RPC,
    MEGAETH_TOKENS,
    RABBITHOLE_CHAIN_STATS,
    RABBITHOLE_DISCOVER_LIST,
    RABBITHOLE_FEATURED_APPS,
    build_catalog,
    looks_like_address,
    stable_json,
    summarize_featured_config,
    summarize_live_catalog,
)
from megaeth_agent_guard.policy import READ_ONLY_RPC_METHODS


def build_scout_report(
    *,
    address: str | None = None,
    live: bool = False,
    probe_apps: bool = False,
    app_timeout: float = 4.0,
    discover_limit: int = 30,
) -> dict[str, Any]:
    """Build a deterministic or live read-only MegaETH report."""

    catalog = build_catalog()
    report: dict[str, Any] = {
        "generated_at": int(time.time()),
        "mode": "read_only_no_signing_no_swaps",
        "live": live,
        "catalog": catalog,
        "guardrails": catalog["guardrails"],
    }

    if live:
        report["rpc"] = scout_rpc(MEGAETH_MAINNET_RPC)
        report["rabbithole"] = scout_rabbithole(discover_limit=discover_limit)
        if address:
            report["wallet"] = scout_wallet(MEGAETH_MAINNET_RPC, address)
        if probe_apps:
            report["app_probes"] = probe_apps_live(app_timeout)
    else:
        report["rpc"] = {
            "ok": None,
            "chain_id": MEGAETH_CHAIN_ID,
            "source": "static",
            "note": "Pass live=true or CLI --live to query the public RPC.",
        }
        report["rabbithole"] = {
            "sources": {
                "chain_stats": RABBITHOLE_CHAIN_STATS,
                "featured": RABBITHOLE_FEATURED_APPS,
                "discover": RABBITHOLE_DISCOVER_LIST,
            },
            "note": "Pass live=true or CLI --live to refresh Rabbithole counts.",
        }
    return report


def scout_rpc(rpc: str = MEGAETH_MAINNET_RPC) -> dict[str, Any]:
    chain_id = int(rpc_call(rpc, "eth_chainId", []), 16)
    block_number = int(rpc_call(rpc, "eth_blockNumber", []), 16)
    gas_price_wei = int(rpc_call(rpc, "eth_gasPrice", []), 16)
    return {
        "ok": chain_id == MEGAETH_CHAIN_ID,
        "chain_id": chain_id,
        "block_number": block_number,
        "gas_price_wei": gas_price_wei,
        "gas_price_gwei": str((Decimal(gas_price_wei) / Decimal("1000000000")).normalize()),
        "rpc": rpc,
    }


def scout_wallet(rpc: str, address: str) -> dict[str, Any]:
    normalized = normalize_address(address)
    native_wei = int(rpc_call(rpc, "eth_getBalance", [normalized, "latest"]), 16)
    balances = {
        "ETH": {
            "address": "native",
            "raw": str(native_wei),
            "formatted": format_units(native_wei, 18),
        }
    }
    for symbol, token_address in MEGAETH_TOKENS.items():
        if symbol == "ETH" or token_address == "native":
            continue
        raw = erc20_balance_of(rpc, token_address, normalized)
        balances[symbol] = {
            "address": token_address,
            "raw": str(raw),
            "formatted": format_units(raw, 18),
        }
    return {
        "address": normalized,
        "balances": balances,
        "note": "Public balances only; no private key was read.",
    }


def scout_rabbithole(discover_limit: int = 30) -> dict[str, Any]:
    chain_stats = fetch_json(RABBITHOLE_CHAIN_STATS)
    featured = summarize_featured_config(fetch_json(RABBITHOLE_FEATURED_APPS))
    discover = summarize_live_catalog(fetch_json(RABBITHOLE_DISCOVER_LIST))
    if isinstance(discover.get("apps"), list):
        discover["apps"] = discover["apps"][:discover_limit]
    return {
        "chain_stats": chain_stats.get("data", chain_stats),
        "featured": featured,
        "discover": discover,
        "sources": {
            "chain_stats": RABBITHOLE_CHAIN_STATS,
            "featured": RABBITHOLE_FEATURED_APPS,
            "discover": RABBITHOLE_DISCOVER_LIST,
        },
    }


def probe_apps_live(timeout: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for app in CURATED_APPS:
        url = app.url
        if not url.startswith("http") or url in seen:
            continue
        seen.add(url)
        rows.append(probe_url(app.name, url, timeout))
    return rows


def probe_url(name: str, url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "megaeth-agent-guard/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {
                "name": name,
                "url": url,
                "ok": 200 <= response.status < 400,
                "status": response.status,
                "content_type": response.headers.get("content-type"),
            }
    except urllib.error.HTTPError as exc:
        return {"name": name, "url": url, "ok": False, "status": exc.code, "error": exc.reason}
    except Exception as exc:
        return {"name": name, "url": url, "ok": False, "error": str(exc)}


def erc20_balance_of(rpc: str, token: str, owner: str) -> int:
    selector = "70a08231"
    encoded_owner = owner.lower().removeprefix("0x").rjust(64, "0")
    result = rpc_call(
        rpc,
        "eth_call",
        [{"to": normalize_address(token), "data": "0x" + selector + encoded_owner}, "latest"],
    )
    if result == "0x":
        return 0
    return int(result, 16)


def rpc_call(rpc: str, method: str, params: list[Any]) -> Any:
    if method not in READ_ONLY_RPC_METHODS:
        raise RuntimeError(f"refusing non-read RPC method: {method}")
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    request = urllib.request.Request(
        rpc,
        data=json.dumps(payload).encode(),
        headers={"content-type": "application/json", "user-agent": "megaeth-agent-guard/0.1"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = json.loads(response.read().decode())
    if "error" in body:
        raise RuntimeError(body["error"])
    return body["result"]


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"user-agent": "megaeth-agent-guard/0.1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode())


def normalize_address(address: str) -> str:
    text = address.strip()
    if not looks_like_address(text):
        raise ValueError("address must be a 20-byte 0x-prefixed address")
    return text


def format_units(raw: int, decimals: int) -> str:
    value = Decimal(raw) / (Decimal(10) ** decimals)
    return str(value.normalize())


def report_to_json(report: dict[str, Any]) -> str:
    return stable_json(report)

