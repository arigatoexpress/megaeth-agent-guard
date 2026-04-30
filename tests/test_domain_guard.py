from __future__ import annotations

from megaeth_agent_guard.domain_guard import evaluate_url


def test_domain_guard_allows_known_official_url():
    decision = evaluate_url("https://rabbithole.megaeth.com")

    assert decision["decision"] == "allow"
    assert decision["severity"] == "low"


def test_domain_guard_denies_lookalike():
    decision = evaluate_url("https://rabbithole-megaeth.com")

    assert decision["decision"] == "deny"
    assert "looks similar" in " ".join(decision["reasons"])


def test_domain_guard_reviews_unknown_external():
    decision = evaluate_url("https://example.com")

    assert decision["decision"] == "review"
    assert decision["severity"] == "medium"
