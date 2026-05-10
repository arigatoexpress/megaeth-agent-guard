"""Flask dashboard and JSON API for MegaETH Agent Guard."""

from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

from megaeth_agent_guard.catalog import build_catalog
from megaeth_agent_guard.domain_guard import evaluate_url
from megaeth_agent_guard.policy import DEFAULT_BUDGET_CAPS, evaluate_intent
from megaeth_agent_guard.scout import build_scout_report

app = Flask(__name__, template_folder="templates")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/api/health")
def api_health():
    return jsonify(
        {
            "ok": True,
            "service": "megaeth-agent-guard",
            "mode": "mainnet_read_and_simulate_only",
            "liveSettlementEnabled": False,
            "signingEnabled": False,
        }
    )


@app.get("/api/frontend-contract")
def api_frontend_contract():
    """Expose the workbench contract for repeatable safe browser smoke checks.

    The contract is metadata only. It describes required selectors, local API
    readbacks, and permitted UI actions without signing, broadcasting,
    settling payments, or moving funds.
    """

    return jsonify(
        {
            "schema": "megaeth_agent_guard.frontend_contract.v1",
            "route": "/",
            "mode": "mainnet_read_and_simulate_only",
            "network": "megaeth-mainnet",
            "chainId": 4326,
            "liveSettlementEnabled": False,
            "signingEnabled": False,
            "moneyMovementEnabled": False,
            "telegramSendsEnabled": False,
            "externalMutationDefault": "disabled",
            "requiredText": [
                "MegaETH Agent Guard",
                "Read, quote, simulate. Never sign.",
                "MegaETH mainnet",
                "read + simulate",
                "no signing",
                "Settlement",
                "Intent Firewall",
                "Domain Guard",
                "Raw Decision",
            ],
            "requiredSelectors": [
                "#guardrails",
                "#refreshLive",
                "#staticScout",
                "#denySample",
                "#allowSample",
                "#chainId",
                "#blockNumber",
                "#appCount",
                "#intentInput",
                "#evaluateIntent",
                "#decisionBadge",
                "#receipt",
                "#domainInput",
                "#checkDomain",
                "#domainStatus",
                "#domainOutput",
                "#featuredList",
                "#appsList",
                "#decisionOutput",
            ],
            "apiRoutes": [
                {
                    "method": "GET",
                    "path": "/api/health",
                    "expectedStatus": 200,
                    "purpose": "confirm service posture and disabled signing/settlement",
                },
                {
                    "method": "GET",
                    "path": "/api/catalog",
                    "expectedStatus": 200,
                    "purpose": "hydrate static MegaETH app and guardrail catalog",
                },
                {
                    "method": "GET",
                    "path": "/api/scout?live=0",
                    "expectedStatus": 200,
                    "purpose": "hydrate deterministic offline scout snapshot",
                },
                {
                    "method": "POST",
                    "path": "/api/evaluate",
                    "expectedStatus": 200,
                    "purpose": "policy preview only for agent intents",
                },
                {
                    "method": "GET",
                    "path": "/api/domain?url=https%3A%2F%2Frabbithole.megaeth.com",
                    "expectedStatus": 200,
                    "purpose": "check MegaETH URL provenance without wallet automation",
                },
            ],
            "primaryActions": [
                {
                    "id": "evaluate-intent",
                    "selector": "#evaluateIntent",
                    "method": "POST",
                    "path": "/api/evaluate",
                    "resultSelector": "#decisionOutput",
                    "expectedMode": "policy_preview_only",
                    "externalEffects": False,
                },
                {
                    "id": "deny-sample",
                    "selector": "#denySample",
                    "resultSelector": "#decisionBadge",
                    "expectedDecision": "deny",
                    "externalEffects": False,
                },
                {
                    "id": "allow-sample",
                    "selector": "#allowSample",
                    "resultSelector": "#decisionBadge",
                    "expectedDecision": "allow",
                    "externalEffects": False,
                },
                {
                    "id": "static-scout",
                    "selector": "#staticScout",
                    "path": "/api/scout?live=0",
                    "resultSelector": "#blockNumber",
                    "externalEffects": False,
                },
                {
                    "id": "check-domain",
                    "selector": "#checkDomain",
                    "path": "/api/domain",
                    "resultSelector": "#domainOutput",
                    "externalEffects": False,
                },
            ],
            "readOnlyExternalActions": [
                {
                    "id": "refresh-live-scout",
                    "selector": "#refreshLive",
                    "path": "/api/scout?live=1",
                    "externalEffects": False,
                    "networkWrites": False,
                }
            ],
            "blockedCapabilities": [
                "wallet signatures",
                "transaction broadcasting",
                "swaps, bridges, deposits, wagers, or paid app actions",
                "mainnet value movement",
                "secret reads or secret display",
                "Telegram or external customer sends",
            ],
        }
    )


@app.get("/api/catalog")
def api_catalog():
    return jsonify(build_catalog())


@app.get("/api/intents")
def api_intents():
    catalog = build_catalog()
    return jsonify({"intents": catalog["intent_templates"], "budget_caps": DEFAULT_BUDGET_CAPS})


@app.get("/api/scout")
def api_scout():
    live = request.args.get("live", "").lower() in {"1", "true", "yes"}
    probe_apps = request.args.get("probe_apps", "").lower() in {"1", "true", "yes"}
    address = request.args.get("address") or None
    discover_limit = int(request.args.get("discover_limit") or 30)
    return jsonify(
        build_scout_report(
            address=address,
            live=live,
            probe_apps=probe_apps,
            discover_limit=discover_limit,
        )
    )


@app.post("/api/evaluate")
def api_evaluate():
    payload = request.get_json(silent=True) or {}
    intent = payload.get("intent", payload)
    budget = payload.get("budget")
    return jsonify(
        {
            "mode": "policy_preview_only",
            "liveSettlementEnabled": False,
            "decision": evaluate_intent(intent, budget=budget),
        }
    )


@app.get("/api/domain")
def api_domain():
    return jsonify(evaluate_url(request.args.get("url") or ""))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8108"))
    app.run(host="127.0.0.1", port=port, debug=False)
