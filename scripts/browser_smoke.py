"""Browser smoke for the MegaETH Agent Guard workbench.

The smoke starts the local Flask app, clicks the safe workbench controls, and
verifies the visible no-signing/no-settlement boundary. It never enables live
wallet actions, transaction signing, Telegram sends, or money movement.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager

from playwright.sync_api import Page, expect, sync_playwright

PORT = int(os.environ.get("MEGA_GUARD_BROWSER_SMOKE_PORT", "8118"))
BASE_URL = f"http://127.0.0.1:{PORT}"


def main() -> int:
    env = {**os.environ, "PORT": str(PORT)}
    with run_server(env):
        run_browser_smoke()
    return 0


@contextmanager
def run_server(env: dict[str, str]) -> Iterator[None]:
    process = subprocess.Popen(
        [sys.executable, "-m", "megaeth_agent_guard.app"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_health(process)
        yield
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def wait_for_health(process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 20
    last_error = "server did not start"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"server exited early with {process.returncode}: {output}")
        try:
            with urllib.request.urlopen(f"{BASE_URL}/api/health", timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(0.2)
    raise TimeoutError(f"Timed out waiting for {BASE_URL}/api/health: {last_error}")


def run_browser_smoke() -> None:
    console_errors: list[str] = []

    def record_console_error(message) -> None:
        if message.type == "error":
            console_errors.append(message.text)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.on("console", record_console_error)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))
        try:
            exercise_workbench(page)
        finally:
            browser.close()
    if console_errors:
        raise AssertionError(f"browser console/page errors: {console_errors}")


def exercise_workbench(page: Page) -> None:
    page.goto(BASE_URL)

    expect(page).to_have_title("MegaETH Agent Guard")
    expect(page.locator("body")).to_contain_text("Read, quote, simulate. Never sign.")
    expect(page.locator("body")).to_contain_text("Settlement")
    expect(page.locator("body")).to_contain_text("disabled")
    expect(page.locator("#chainId")).to_contain_text("4326")
    expect(page.locator("#guardrails")).to_contain_text("can_sign")
    expect(page.locator("#guardrails")).to_contain_text("false")

    page.locator("#staticScout").click()
    expect(page.locator("#blockNumber")).to_contain_text("static")

    page.locator("#denySample").click()
    expect(page.locator("#decisionBadge")).to_contain_text("deny")
    expect(page.locator("#decisionOutput")).to_contain_text('"liveSettlementEnabled": false')
    expect(page.locator("#decisionOutput")).to_contain_text('"decision": "deny"')

    page.locator("#allowSample").click()
    expect(page.locator("#decisionBadge")).to_contain_text("allow")
    expect(page.locator("#decisionOutput")).to_contain_text('"mode": "policy_preview_only"')
    expect(page.locator("#decisionOutput")).to_contain_text('"mode": "read"')
    expect(page.locator("#decisionOutput")).to_contain_text('"liveSettlementEnabled": false')

    page.locator("#checkDomain").click()
    expect(page.locator("#domainStatus")).to_contain_text("allow")
    expect(page.locator("#domainOutput")).to_contain_text("rabbithole.megaeth.com")

    health = page.request.get(f"{BASE_URL}/api/health")
    assert health.ok
    health_body = health.json()
    assert health_body["liveSettlementEnabled"] is False
    assert health_body["signingEnabled"] is False

    contract = page.request.get(f"{BASE_URL}/api/frontend-contract")
    assert contract.ok
    contract_body = contract.json()
    assert contract_body["schema"] == "megaeth_agent_guard.frontend_contract.v1"
    assert contract_body["liveSettlementEnabled"] is False
    assert contract_body["signingEnabled"] is False
    assert contract_body["moneyMovementEnabled"] is False
    assert "wallet signatures" in contract_body["blockedCapabilities"]

    evaluate = page.request.post(
        f"{BASE_URL}/api/evaluate",
        data=json.dumps(
            {
                "intent": {
                    "action": "bridge_eth",
                    "mode": "live_transaction",
                    "chain_id": 4326,
                    "value_eth": 0.001,
                    "requires_signature": True,
                }
            }
        ),
        headers={"content-type": "application/json"},
    )
    assert evaluate.ok
    evaluate_body = evaluate.json()
    assert evaluate_body["liveSettlementEnabled"] is False
    assert evaluate_body["decision"]["decision"] == "deny"


if __name__ == "__main__":
    raise SystemExit(main())
