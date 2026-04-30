"""URL/domain guard for MegaETH app discovery.

Agents should not follow arbitrary MegaETH-looking links. This module gives the
demo a small, deterministic phishing/spoof screen that can run before browser or
wallet automation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import urlparse

from megaeth_agent_guard.catalog import (
    CURATED_APPS,
    MEGAETH_BLOCK_EXPLORERS,
    MEGAETH_DOCS,
    RABBITHOLE_BASE,
)

OFFICIAL_DOMAINS = {
    "megaeth.com",
    "www.megaeth.com",
    "docs.megaeth.com",
    "rabbithole.megaeth.com",
    "mega.etherscan.io",
    "megaeth.blockscout.com",
}


@dataclass(frozen=True)
class DomainDecision:
    url: str
    host: str
    decision: str
    severity: str
    reasons: tuple[str, ...]
    nearest_known_domain: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def known_domains() -> set[str]:
    domains = set(OFFICIAL_DOMAINS)
    for url in [*MEGAETH_DOCS.values(), *MEGAETH_BLOCK_EXPLORERS, RABBITHOLE_BASE]:
        host = parse_host(url)
        if host:
            domains.add(host)
    for app in CURATED_APPS:
        host = parse_host(app.url)
        if host:
            domains.add(host)
    return domains


def evaluate_url(url: str) -> dict[str, Any]:
    host = parse_host(url)
    reasons: list[str] = []
    if not host:
        return DomainDecision(
            url=url,
            host="",
            decision="deny",
            severity="high",
            reasons=("invalid or missing URL host",),
        ).to_dict()

    domains = known_domains()
    nearest = nearest_domain(host, domains)
    parsed = urlparse(url if "://" in url else f"https://{url}")

    if parsed.scheme not in {"http", "https"}:
        reasons.append(f"unsupported URL scheme: {parsed.scheme}")
    if any(ord(char) > 127 for char in host):
        reasons.append("non-ascii host requires manual review")
    if host in domains:
        decision = "allow"
        severity = "low"
        reasons.append("host is in the curated MegaETH/app allowlist")
    elif host.endswith(".megaeth.com"):
        decision = "review"
        severity = "medium"
        reasons.append("host is under megaeth.com but not in the curated allowlist")
    elif nearest and SequenceMatcher(None, host, nearest).ratio() >= 0.84:
        decision = "deny"
        severity = "high"
        reasons.append(f"host looks similar to known domain {nearest}")
    else:
        decision = "review"
        severity = "medium"
        reasons.append("unknown external host")

    if parsed.scheme != "https":
        if decision == "allow":
            decision = "review"
            severity = "medium"
        reasons.append("https is required for automated navigation")

    return DomainDecision(
        url=url,
        host=host,
        decision=decision,
        severity=severity,
        reasons=tuple(reasons),
        nearest_known_domain=nearest,
    ).to_dict()


def parse_host(url: str) -> str:
    text = str(url or "").strip()
    if not text:
        return ""
    parsed = urlparse(text if "://" in text else f"https://{text}")
    return (parsed.hostname or "").lower().strip(".")


def nearest_domain(host: str, domains: set[str]) -> str | None:
    if not domains:
        return None
    return max(domains, key=lambda domain: SequenceMatcher(None, host, domain).ratio())

