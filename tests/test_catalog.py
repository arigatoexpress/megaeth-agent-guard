from __future__ import annotations

from megaeth_agent_guard.catalog import (
    MEGAETH_CHAIN_ID,
    build_catalog,
    classify_discover_app,
    summarize_featured_config,
    summarize_live_catalog,
)


def test_catalog_is_mainnet_read_only():
    catalog = build_catalog()

    assert catalog["network"]["chain_id"] == MEGAETH_CHAIN_ID == 4326
    assert catalog["network"]["rpc"] == "https://mainnet.megaeth.com/rpc"
    assert catalog["tokens"]["MEGA"] == "0x28B7E77f82B25B95953825F1E3eA0E36c1c29861"
    assert catalog["guardrails"]["can_read_rpc"] is True
    assert catalog["guardrails"]["can_sign"] is False
    assert catalog["guardrails"]["can_send_transactions"] is False
    assert catalog["guardrails"]["can_bridge"] is False
    assert any(app["id"] == "agnt" for app in catalog["apps"])


def test_discover_summary_counts_live_mega_native_apps():
    summary = summarize_live_catalog(
        {
            "data": [
                {
                    "id": 1,
                    "name": "AGNT",
                    "website": "https://agnt.social",
                    "category": ["AI", "Culture & Social"],
                    "is_live": True,
                    "is_mega_native": True,
                    "contract_address": "0x130ae104180b7a1467748c1d6e3d1df8e0de55df",
                },
                {
                    "id": 2,
                    "name": "Vault",
                    "category": ["Yield & Credit"],
                    "is_live": False,
                    "is_mega_native": False,
                    "contract_address": "[will insert once vault is live]",
                },
            ]
        }
    )

    assert summary["count"] == 2
    assert summary["live_count"] == 1
    assert summary["mega_native_count"] == 1
    assert summary["apps"][0]["agent_policy"] == "read_only_no_posting_no_wagering"
    assert summary["apps"][1]["contract_address"] is None


def test_featured_config_summary_is_stable():
    assert summarize_featured_config(
        {"data": {"liveNow": ["Kumbaya"], "upcoming": ["Dream"], "roadmap": ["HelloTrade"]}}
    ) == {
        "liveNow": ["Kumbaya"],
        "upcoming": ["Dream"],
        "roadmap": ["HelloTrade"],
    }


def test_discover_app_ignores_invalid_contracts():
    row = classify_discover_app({"name": "RockSolid", "contract_address": "not an address"})

    assert row["contract_address"] is None

