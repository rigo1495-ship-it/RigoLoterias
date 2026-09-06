from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_games() -> None:
    response = client.get("/api/v1/games")
    assert response.status_code == 200
    assert len(response.json()) == 9


def test_game_lookup() -> None:
    response = client.get("/api/v1/games/tris")
    assert response.status_code == 200
    assert response.json()["status"] == "planned"


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
    assert detail["status"] == "planned"
