from __future__ import annotations

from megaeth_agent_guard.app import app


def _selector_id(selector: str) -> str | None:
    if not selector.startswith("#"):
        return None
    return selector[1:].split(" ", 1)[0].split(".", 1)[0]


def test_health_endpoint():
    client = app.test_client()
    payload = client.get("/api/health").get_json()

    assert payload["ok"] is True
    assert payload["liveSettlementEnabled"] is False
    assert payload["signingEnabled"] is False


def test_index_uses_static_workbench_assets():
    client = app.test_client()

    response = client.get("/")
    html = response.get_data(as_text=True)
    css = client.get("/static/styles.css")
    js = client.get("/static/app.js")

    assert response.status_code == 200
    assert "/static/styles.css" in html
    assert "/static/app.js" in html
    assert "<style>" not in html
    assert "function evaluateIntent" not in html
    assert "Wallet <strong>no signing</strong>" in html
    assert css.status_code == 200
    assert ".posture-strip" in css.get_data(as_text=True)
    assert js.status_code == 200
    js_body = js.get_data(as_text=True)
    assert "async function evaluateIntent" in js_body
    assert 'fetchJson("/api/evaluate"' in js_body


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


def test_frontend_contract_is_browser_smoke_ready_and_non_mutating():
    client = app.test_client()

    response = client.get("/api/frontend-contract")

    assert response.status_code == 200
    body = response.get_json()
    assert body["schema"] == "megaeth_agent_guard.frontend_contract.v1"
    assert body["route"] == "/"
    assert body["mode"] == "mainnet_read_and_simulate_only"
    assert body["network"] == "megaeth-mainnet"
    assert body["chainId"] == 4326
    assert body["liveSettlementEnabled"] is False
    assert body["signingEnabled"] is False
    assert body["moneyMovementEnabled"] is False
    assert body["telegramSendsEnabled"] is False
    assert body["externalMutationDefault"] == "disabled"
    assert "wallet signatures" in body["blockedCapabilities"]
    assert "mainnet value movement" in body["blockedCapabilities"]

    api_routes = {(route["method"], route["path"]): route for route in body["apiRoutes"]}
    assert api_routes[("GET", "/api/health")]["expectedStatus"] == 200
    assert api_routes[("GET", "/api/catalog")]["expectedStatus"] == 200
    assert api_routes[("GET", "/api/scout?live=0")]["expectedStatus"] == 200
    assert api_routes[("POST", "/api/evaluate")]["expectedStatus"] == 200

    deny_action = next(action for action in body["primaryActions"] if action["id"] == "deny-sample")
    assert deny_action["selector"] == "#denySample"
    assert deny_action["expectedDecision"] == "deny"
    assert deny_action["externalEffects"] is False


def test_frontend_contract_selectors_match_static_shell():
    client = app.test_client()
    contract = client.get("/api/frontend-contract").get_json()
    html = client.get("/").get_data(as_text=True)
    js = client.get("/static/app.js").get_data(as_text=True)

    for expected_text in contract["requiredText"]:
        assert expected_text in html

    for selector in contract["requiredSelectors"]:
        element_id = _selector_id(selector)
        if element_id:
            assert f'id="{element_id}"' in html

    assert 'el("evaluateIntent").addEventListener("click", evaluateIntent)' in js
    assert 'el("denySample").addEventListener("click"' in js
    assert 'el("allowSample").addEventListener("click"' in js
    assert 'fetchJson("/api/evaluate"' in js
    assert 'fetchJson("/api/catalog")' in js


def test_frontend_contract_routes_read_back_expected_statuses():
    client = app.test_client()
    contract = client.get("/api/frontend-contract").get_json()

    for route in contract["apiRoutes"]:
        if route["method"] == "GET":
            response = client.get(route["path"])
        else:
            response = client.post(
                route["path"],
                json={
                    "intent": {
                        "action": "bridge_eth",
                        "mode": "live_transaction",
                        "chain_id": 4326,
                        "value_eth": 0.001,
                        "requires_signature": True,
                    }
                },
            )
        assert response.status_code == route["expectedStatus"], route

    evaluate = client.post(
        "/api/evaluate",
        json={
            "intent": {
                "action": "bridge_eth",
                "mode": "live_transaction",
                "chain_id": 4326,
                "value_eth": 0.001,
                "requires_signature": True,
            }
        },
    ).get_json()
    assert evaluate["liveSettlementEnabled"] is False
    assert evaluate["mode"] == "policy_preview_only"
    assert evaluate["decision"]["decision"] == "deny"
