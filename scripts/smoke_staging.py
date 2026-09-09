"""Run the Phase J2 smoke checks against a deployed staging environment."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def request(url: str, *, headers: dict[str, str] | None = None, body: object | None = None) -> tuple[int, dict[str, str], bytes]:
    data = json.dumps(body).encode() if body is not None else None
    merged = {"Accept": "application/json", **(headers or {})}
    if data is not None:
        merged["Content-Type"] = "application/json"
    try:
        with urlopen(Request(url, data=data, headers=merged), timeout=15) as response:
            return response.status, dict(response.headers.items()), response.read()
    except HTTPError as error:
        return error.code, dict(error.headers.items()), error.read()


def assert_status(actual: int, expected: int, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, received {actual}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", required=True, help="Public API prefix, ending in /api/v1")
    parser.add_argument("--frontend-url", required=True, help="Public static frontend origin")
    arguments = parser.parse_args()
    api_url = arguments.api_url.rstrip("/")
    frontend_url = arguments.frontend_url.rstrip("/")
    token = os.environ.get("WRITE_API_TOKEN")
    if not token:
        raise SystemExit("WRITE_API_TOKEN must be supplied through the environment")

    health_status, health_headers, _ = request(f"{api_url}/health")
    assert_status(health_status, 200, "health")
    if len(health_headers.get("X-Request-Id", "")) != 32:
        raise AssertionError("health: missing X-Request-ID")
    ready_status, _, _ = request(f"{api_url}/ready")
    assert_status(ready_status, 200, "ready")
    games_status, _, games_body = request(f"{api_url}/games")
    assert_status(games_status, 200, "games")
    games = json.loads(games_body)
    if len(games) != 8 or any(game["status"] != "available" for game in games):
        raise AssertionError("games: expected eight available games")

    cors_status, cors_headers, _ = request(f"{api_url}/health", headers={"Origin": frontend_url})
    assert_status(cors_status, 200, "allowed CORS")
    if cors_headers.get("Access-Control-Allow-Origin") != frontend_url:
        raise AssertionError("allowed CORS: origin was not echoed")
    _, rejected_cors_headers, _ = request(
        f"{api_url}/health", headers={"Origin": "https://untrusted.invalid"}
    )
    if "Access-Control-Allow-Origin" in rejected_cors_headers:
        raise AssertionError("rejected CORS: untrusted origin was allowed")

    invalid_host_status, _, _ = request(f"{api_url}/health", headers={"Host": "untrusted.invalid"})
    assert_status(invalid_host_status, 400, "invalid Host")

    preview_path = f"{api_url}/tris/imports/preview"
    preview = {"csv_text": "draw_id,draw_date,winning_number\\n1,2026-01-01,00508\\n"}
    no_token_status, _, _ = request(preview_path, body=preview)
    assert_status(no_token_status, 401, "import without token")
    wrong_token_status, _, _ = request(
        preview_path, headers={"X-API-Key": "not-the-server-token"}, body=preview
    )
    assert_status(wrong_token_status, 401, "import with invalid token")
    valid_token_status, _, _ = request(
        preview_path, headers={"X-API-Key": token}, body=preview
    )
    assert_status(valid_token_status, 200, "import with valid token")

    frontend_status, _, frontend_body = request(frontend_url, headers={"Accept": "text/html"})
    assert_status(frontend_status, 200, "frontend")
    assets = re.findall(rb'(?:src|href)="([^"]+\.(?:js|css))"', frontend_body)
    for asset in assets:
        asset_url = asset.decode()
        absolute = asset_url if asset_url.startswith("http") else f"{frontend_url}{asset_url}"
        _, _, content = request(absolute)
        if token.encode() in content:
            raise AssertionError("frontend bundle contains WRITE_API_TOKEN")
    print("Phase J2 staging smoke test passed")


if __name__ == "__main__":
    main()
