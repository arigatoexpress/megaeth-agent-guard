"""CLI for MegaETH Agent Guard."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from megaeth_agent_guard.catalog import build_catalog, stable_json
from megaeth_agent_guard.domain_guard import evaluate_url
from megaeth_agent_guard.policy import evaluate_intent
from megaeth_agent_guard.scout import build_scout_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only MegaETH agent safety toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("catalog", help="Print deterministic MegaETH app/network catalog.")

    scout = sub.add_parser("scout", help="Build a read-only MegaETH scout report.")
    scout.add_argument(
        "--live",
        action="store_true",
        help="Query live RPC and Rabbithole endpoints.",
    )
    scout.add_argument("--address", help="Optional public wallet address for balance reads.")
    scout.add_argument("--probe-apps", action="store_true", help="HEAD-probe curated app URLs.")
    scout.add_argument("--discover-limit", type=int, default=30)
    scout.add_argument("--write", type=Path, help="Optional JSON report path.")

    evaluate = sub.add_parser("evaluate", help="Evaluate an agent intent JSON object.")
    evaluate.add_argument("--intent-json", required=True, help="Inline JSON object.")

    domain = sub.add_parser("domain", help="Evaluate a URL before agent navigation.")
    domain.add_argument("url")

    args = parser.parse_args(argv)
    if args.command == "catalog":
        print(stable_json(build_catalog()))
        return 0
    if args.command == "scout":
        report = build_scout_report(
            live=args.live,
            address=args.address,
            probe_apps=args.probe_apps,
            discover_limit=args.discover_limit,
        )
        rendered = stable_json(report)
        if args.write:
            args.write.parent.mkdir(parents=True, exist_ok=True)
            args.write.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
        return 0
    if args.command == "evaluate":
        print(stable_json(evaluate_intent(load_json(args.intent_json))))
        return 0
    if args.command == "domain":
        print(stable_json(evaluate_url(args.url)))
        return 0
    return 2


def load_json(text: str) -> dict[str, Any]:
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON: {exc}") from exc
    if not isinstance(loaded, dict):
        raise SystemExit("intent JSON must be an object")
    return loaded


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
