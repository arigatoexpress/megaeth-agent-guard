from __future__ import annotations

import pytest

from megaeth_agent_guard.scout import build_scout_report, normalize_address, rpc_call


def test_static_scout_does_not_require_network():
    report = build_scout_report(live=False)

    assert report["live"] is False
    assert report["catalog"]["network"]["chain_id"] == 4326
    assert report["guardrails"]["can_send_transactions"] is False


def test_rpc_call_refuses_writes_before_network():
    with pytest.raises(RuntimeError, match="refusing non-read RPC method"):
        rpc_call("https://mainnet.megaeth.com/rpc", "eth_sendRawTransaction", ["0x"])


def test_normalize_address_validates_shape():
    assert normalize_address("0x0000000000000000000000000000000000000000").startswith("0x")
    with pytest.raises(ValueError):
        normalize_address("0x1234")

