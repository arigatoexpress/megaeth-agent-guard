from __future__ import annotations

from megaeth_agent_guard.app import app


def test_health_endpoint():
    client = app.test_client()
    payload = client.get("/api/health").get_json()

    assert payload["ok"] is True
    assert payload["liveSettlementEnabled"] is False
    assert payload["signingEnabled"] is False


def test_catalog_endpoint():
    client = app.test_client()
    payload = client.get("/api/catalog").get_json()

    assert payload["network"]["chain_id"] == 4326
    assert payload["guardrails"]["can_sign"] is False


def test_evaluate_endpoint_denies_live_transaction():
    client = app.test_client()
    payload = client.post(
        "/api/evaluate",
        json={"intent": {"action": "swap", "mode": "live_transaction", "value_eth": 1}},
    ).get_json()

    assert payload["liveSettlementEnabled"] is False
    assert payload["decision"]["decision"] == "deny"


def test_static_scout_endpoint():
    client = app.test_client()
    payload = client.get("/api/scout").get_json()

    assert payload["live"] is False
    assert payload["catalog"]["network"]["chain_id"] == 4326

