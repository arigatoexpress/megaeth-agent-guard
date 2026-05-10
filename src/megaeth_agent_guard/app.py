"""Flask dashboard and JSON API for MegaETH Agent Guard."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from megaeth_agent_guard.catalog import build_catalog
from megaeth_agent_guard.domain_guard import evaluate_url
from megaeth_agent_guard.policy import DEFAULT_BUDGET_CAPS, evaluate_intent
from megaeth_agent_guard.scout import build_scout_report

PROJECT_ROOT = Path(__file__).resolve().parents[2]

app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"))


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
