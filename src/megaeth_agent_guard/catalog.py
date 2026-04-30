"""Curated MegaETH mainnet catalog and source registry.

The catalog is deterministic and safe to load offline. Live refreshes happen in
``scout.py`` and are kept separate from the project narrative so demos do not
depend on a third-party endpoint being up.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

MEGAETH_MAINNET_RPC = "https://mainnet.megaeth.com/rpc"
MEGAETH_CHAIN_ID = 4326
MEGAETH_CHAIN_ID_HEX = "0x10e6"
MEGAETH_NATIVE_TOKEN = "ETH"
MEGAETH_BLOCK_EXPLORERS = ("https://mega.etherscan.io", "https://megaeth.blockscout.com")

MEGAETH_DOCS = {
    "mainnet": "https://docs.megaeth.com/frontier",
    "connect": "https://docs.megaeth.com/user-guide/connect",
    "read": "https://docs.megaeth.com/developer-docs/overview-2",
    "realtime_api": "https://docs.megaeth.com/developer-docs/overview-2/realtime-api",
    "tokenlist": "https://github.com/megaeth-labs/mega-tokenlist",
}

RABBITHOLE_BASE = "https://rabbithole.megaeth.com"
RABBITHOLE_CHAIN_STATS = f"{RABBITHOLE_BASE}/api/data/chain"
RABBITHOLE_FEATURED_APPS = f"{RABBITHOLE_BASE}/api/featured-apps"
RABBITHOLE_DISCOVER_LIST = f"{RABBITHOLE_BASE}/api/discover/list"

MEGAETH_TOKENS = {
    "ETH": "native",
    "MEGA": "0x28B7E77f82B25B95953825F1E3eA0E36c1c29861",
    "USDM": "0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7",
    "WETH9": "0x4200000000000000000000000000000000000006",
}

MEGAETH_CONTRACTS = {
    "l1_standard_bridge": "0x0CA3A2FBC3D770b578223FBB6b062fa875a2eE75",
    "multicall3": "0xcA11bde05977b3631167028862bE2a173976CA11",
}


@dataclass(frozen=True)
class MegaETHApp:
    id: str
    name: str
    category: tuple[str, ...]
    status: str
    url: str
    source: str
    agent_surface: str
    guardrail: str
    opportunity: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntentTemplate:
    id: str
    label: str
    action: str
    app_hint: str
    mode: str
    risk: str
    safe_next_step: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CURATED_APPS: tuple[MegaETHApp, ...] = (
    MegaETHApp(
        id="rabbithole",
        name="Rabbithole",
        category=("portal", "bridge", "swap", "discovery"),
        status="official_portal",
        url=RABBITHOLE_BASE,
        source=RABBITHOLE_BASE,
        agent_surface="Public chain stats, featured app config, and discover catalog.",
        guardrail="No signing, bridging, swapping, or wallet popups from automation.",
        opportunity="Canonical ecosystem inventory and app-intent source for policy scoring.",
        notes=(RABBITHOLE_CHAIN_STATS, RABBITHOLE_FEATURED_APPS, RABBITHOLE_DISCOVER_LIST),
    ),
    MegaETHApp(
        id="kumbaya",
        name="Kumbaya",
        category=("dex", "swap", "liquidity"),
        status="featured_live",
        url="https://kumbaya.xyz",
        source=RABBITHOLE_FEATURED_APPS,
        agent_surface="DEX UI and public market context; direct swap API is not assumed.",
        guardrail="Unsigned quote or fork simulation only.",
        opportunity=(
            "Best visible venue for demonstrating a MEGA/USDM swap intent "
            "that never signs."
        ),
    ),
    MegaETHApp(
        id="world-markets",
        name="World Markets",
        category=("rwa", "prediction", "trading"),
        status="featured_live",
        url=f"{RABBITHOLE_BASE}/featured-apps",
        source=RABBITHOLE_FEATURED_APPS,
        agent_surface=(
            "Rabbithole-discovered app surface; contracts must be verified "
            "before automation."
        ),
        guardrail="Research and public-data read only.",
        opportunity="Connects Sapphire-style cyber/RWA signal access to real-time MegaETH markets.",
    ),
    MegaETHApp(
        id="brix",
        name="Brix",
        category=("rwa", "yield", "emerging-markets"),
        status="featured_live",
        url=f"{RABBITHOLE_BASE}/featured-apps",
        source=RABBITHOLE_FEATURED_APPS,
        agent_surface="Public app surface and catalog metadata.",
        guardrail="No deposit, no portfolio allocation, no promise of yield.",
        opportunity=(
            "Strong privacy-risk demo: prove agent knows constraints before "
            "touching RWA yield."
        ),
    ),
    MegaETHApp(
        id="showdown",
        name="Showdown",
        category=("gaming", "cards", "real-time"),
        status="featured_live",
        url=f"{RABBITHOLE_BASE}/featured-apps",
        source=RABBITHOLE_FEATURED_APPS,
        agent_surface="Fast consumer/game actions with potential paid or chance-based flows.",
        guardrail="No autonomous wagering, paid gameplay, or asset purchases.",
        opportunity="Latency stress test for agent safety decisions under pressure.",
    ),
    MegaETHApp(
        id="monster",
        name="Monster",
        category=("novel-assets", "culture", "cards"),
        status="featured_live",
        url="https://mnstr.xyz/",
        source=RABBITHOLE_FEATURED_APPS,
        agent_surface="Collectible/asset purchase flows discovered through Rabbithole.",
        guardrail="No purchase, no buyback reliance, no paid game action.",
        opportunity="Excellent adversarial demo for blocking attractive but spendy prompts.",
    ),
    MegaETHApp(
        id="hit-one",
        name="Hit.One",
        category=("culture", "consumer", "real-time"),
        status="featured_live",
        url=f"{RABBITHOLE_BASE}/featured-apps",
        source=RABBITHOLE_FEATURED_APPS,
        agent_surface="Consumer app actions and public social/culture context.",
        guardrail="No social posting, identity changes, or paid actions.",
        opportunity="Demonstrates non-financial agent action boundaries.",
    ),
    MegaETHApp(
        id="rocksolid",
        name="RockSolid",
        category=("yield", "vault", "usdm"),
        status="discover_live",
        url="https://rocksolid.network/",
        source=RABBITHOLE_DISCOVER_LIST,
        agent_surface="Yield/vault UI and catalog metadata.",
        guardrail="No deposits; require contract verification and simulations first.",
        opportunity="Useful for vault-risk scoring and privacy-preserving suitability proofs.",
    ),
    MegaETHApp(
        id="agnt",
        name="AGNT",
        category=("ai", "agent-marketplace", "identity"),
        status="discover_live",
        url="https://agnt.social",
        source=RABBITHOLE_DISCOVER_LIST,
        agent_surface=(
            "Agent marketplace and identity-like flows; public contract "
            "metadata is available."
        ),
        guardrail="No paid skill install, posting, or identity minting.",
        opportunity="Best path to x402-style paid AI services plus onchain policy receipts.",
        notes=("Rabbithole has listed contract metadata for AGNT in discover responses.",),
    ),
    MegaETHApp(
        id="cap",
        name="Cap",
        category=("stablecoin", "yield", "credit"),
        status="mega_mafia_research",
        url="https://www.cap.app",
        source="https://www.cap.app/blog/cap-launches-on-megaeth",
        agent_surface="Stablecoin/yield docs and app UI; no API contract is assumed.",
        guardrail="Disclosure collection and risk scoring only.",
        opportunity="USDM/stablecoin policy bridge for private agent payment workflows.",
    ),
)


INTENT_TEMPLATES: tuple[IntentTemplate, ...] = (
    IntentTemplate(
        id="read-chain-state",
        label="Read chain state",
        action="eth_chainId",
        app_hint="MegaETH RPC",
        mode="read",
        risk="low",
        safe_next_step="Allow and attach a receipt hash.",
        params={"method": "eth_chainId", "params": []},
    ),
    IntentTemplate(
        id="quote-mega-usdm",
        label="Quote MEGA to USDM",
        action="quote_swap",
        app_hint="Kumbaya",
        mode="unsigned_quote",
        risk="medium",
        safe_next_step="Build an unsigned quote request; block any wallet signature.",
        params={"asset_in": "MEGA", "asset_out": "USDM", "value_eth": 0},
    ),
    IntentTemplate(
        id="x402-agent-report",
        label="Gate an AI report",
        action="request_x402_payment",
        app_hint="AGNT or Sapphire satellite",
        mode="http_402_mock",
        risk="medium",
        safe_next_step="Return payment requirements and keep settlement disabled by default.",
        params={"resource": "private-risk-report", "settlement": "mock"},
    ),
    IntentTemplate(
        id="score-usdm-vault",
        label="Score USDm vault",
        action="risk_score_deposit",
        app_hint="RockSolid or Cap",
        mode="analysis",
        risk="high",
        safe_next_step="Collect disclosures and contract metadata; deny deposit transaction.",
        params={"asset": "USDM", "value_eth": 0},
    ),
    IntentTemplate(
        id="block-bridge",
        label="Attempt bridge",
        action="bridge_eth",
        app_hint="Rabbithole",
        mode="live_transaction",
        risk="critical",
        safe_next_step="Block and show a simulation-only alternative.",
        params={"value_eth": 0.001, "to": MEGAETH_CONTRACTS["l1_standard_bridge"]},
    ),
)


def build_catalog() -> dict[str, Any]:
    """Return the deterministic project catalog."""

    return {
        "network": {
            "name": "MegaETH Mainnet",
            "chain_id": MEGAETH_CHAIN_ID,
            "chain_id_hex": MEGAETH_CHAIN_ID_HEX,
            "rpc": MEGAETH_MAINNET_RPC,
            "native_token": MEGAETH_NATIVE_TOKEN,
            "block_explorers": list(MEGAETH_BLOCK_EXPLORERS),
            "mini_block_time": "10ms",
            "evm_block_time": "1s",
            "mode": "mainnet_read_and_simulate_only",
        },
        "tokens": MEGAETH_TOKENS,
        "contracts": MEGAETH_CONTRACTS,
        "sources": {
            "docs": MEGAETH_DOCS,
            "rabbithole": {
                "portal": RABBITHOLE_BASE,
                "chain_stats": RABBITHOLE_CHAIN_STATS,
                "featured_apps": RABBITHOLE_FEATURED_APPS,
                "discover_list": RABBITHOLE_DISCOVER_LIST,
            },
        },
        "apps": [app.to_dict() for app in CURATED_APPS],
        "intent_templates": [template.to_dict() for template in INTENT_TEMPLATES],
        "guardrails": {
            "can_read_rpc": True,
            "can_fetch_public_catalogs": True,
            "can_probe_public_urls": True,
            "can_build_unsigned_intents": True,
            "can_estimate_or_simulate": True,
            "can_sign": False,
            "can_send_transactions": False,
            "can_swap": False,
            "can_bridge": False,
            "can_deposit": False,
            "can_wager": False,
        },
    }


def classify_discover_app(app: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Rabbithole discover row without treating it as executable."""

    categories = tuple(str(item) for item in (app.get("category") or ()))
    contract = app.get("contract_address")
    return {
        "id": str(app.get("id") or app.get("name") or "unknown"),
        "name": str(app.get("name") or "Unknown"),
        "website": app.get("website"),
        "category": list(categories),
        "is_live": bool(app.get("is_live")),
        "is_mega_native": bool(app.get("is_mega_native")),
        "contract_address": contract if looks_like_address(contract) else None,
        "agent_policy": policy_for_categories(categories),
        "description": app.get("description") or "",
    }


def policy_for_categories(categories: tuple[str, ...]) -> str:
    lowered = " ".join(categories).lower()
    if any(term in lowered for term in ("yield", "credit", "trading", "defi", "rwa")):
        return "research_or_quote_only"
    if any(term in lowered for term in ("gaming", "cards", "social", "culture", "assets")):
        return "read_only_no_posting_no_wagering"
    if any(term in lowered for term in ("ai", "agent", "identity")):
        return "read_only_no_paid_skill_install"
    return "read_only"


def looks_like_address(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if len(text) != 42 or not text.startswith("0x"):
        return False
    try:
        int(text[2:], 16)
    except ValueError:
        return False
    return True


def summarize_live_catalog(raw: dict[str, Any]) -> dict[str, Any]:
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        return {"count": 0, "live_count": 0, "mega_native_count": 0, "apps": []}
    apps = [classify_discover_app(row) for row in rows if isinstance(row, dict)]
    return {
        "count": len(apps),
        "live_count": sum(1 for app in apps if app["is_live"]),
        "mega_native_count": sum(1 for app in apps if app["is_mega_native"]),
        "apps": apps,
    }


def summarize_featured_config(raw: dict[str, Any]) -> dict[str, Any]:
    data = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(data, dict):
        return {"liveNow": [], "upcoming": [], "roadmap": []}
    return {
        "liveNow": [str(item) for item in data.get("liveNow", [])],
        "upcoming": [str(item) for item in data.get("upcoming", [])],
        "roadmap": [str(item) for item in data.get("roadmap", [])],
    }


def stable_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)
