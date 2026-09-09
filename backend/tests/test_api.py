from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert len(response.headers["x-request-id"]) == 32
    assert float(response.headers["x-process-time-ms"]) >= 0


def test_readiness_checks_database() -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_cors_allows_configured_local_frontend() -> None:
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_tris_end_to_end_api() -> None:
    imported = client.post(
        "/api/v1/tris/imports",
        json={
            "csv_text": "draw_id,draw_date,winning_number\n1,2026-01-01,00508\n",
            "commit": True,
        },
    )
    assert imported.status_code == 200 and imported.json()["committed"] == 1
    assert client.get("/api/v1/tris/draws/latest").json()["winning_number"] == "00508"
    portfolio = client.post(
        "/api/v1/tris/portfolios", json={"count": 2, "strategy": "random", "seed": 42}
    )
    assert portfolio.json()["tickets"] == ["83810", "14592"]


def test_games() -> None:
    response = client.get("/api/v1/games")
    assert response.status_code == 200
    assert len(response.json()) == 8


def test_game_lookup() -> None:
    response = client.get("/api/v1/games/tris")
    assert response.status_code == 200
    assert response.json()["status"] == "available"


def test_unknown_game_has_structured_error() -> None:
    response = client.get("/api/v1/games/not-a-game")
    assert response.status_code == 404
    assert response.json()["detail"] == {
        "game": "not-a-game",
        "capability": "registry",
        "status": "unknown",
        "message": "Game 'not-a-game' is not registered.",
    }


def test_capability_placeholder_is_structured() -> None:
    response = client.get("/api/v1/games/tris/capabilities/statistics")
    assert response.status_code == 501
    detail = response.json()["detail"]
    assert detail["game"] == "tris"
    assert detail["capability"] == "statistics"
    assert detail["status"] == "available"
