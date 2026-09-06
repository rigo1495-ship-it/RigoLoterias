from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
CSV = (
    "CONCURSO,F1,F2,F3,F4,F5,F6,F7,F8,FECHA\n"
    "990001,1,2,3,4,5,1,2,3,01/01/2026\n"
    "990002,2,3,4,5,1,2,3,4,02/01/2026\n"
)


def test_config_import_latest_statistics_and_isolation() -> None:
    config = client.get("/api/v1/gana_gato/config").json()
    assert config["board_space_size"] == 390625 and config["center"] == "wildcard"
    imported = client.post("/api/v1/gana_gato/imports", json={"csv_text": CSV, "commit": True})
    assert imported.status_code == 200 and imported.json()["accepted_rows"] == 2
    assert client.get("/api/v1/gana_gato/draws/latest").json()["draw_number"] == "990002"
    assert "position_frequency" in client.get("/api/v1/gana_gato/statistics").json()
    assert client.get("/api/v1/melate/config").status_code == 200


def test_portfolio_evaluation_backtest_and_predictable_errors() -> None:
    body = {
        "number_of_tickets": 3,
        "strategy": "coverage_optimized",
        "random_seed": 11,
        "minimum_hamming_distance": 2,
    }
    one = client.post("/api/v1/gana_gato/portfolios", json=body)
    two = client.post("/api/v1/gana_gato/portfolios", json=body)
    assert one.status_code == 200 and one.json()["tickets"] == two.json()["tickets"]
    evaluation = client.post(
        "/api/v1/gana_gato/board/evaluate", json={"ticket": [1] * 8, "result": [1] * 8}
    )
    assert evaluation.json()["line_count"] == 8 and evaluation.json()["prize_amount"] is None
    assert (
        client.post(
            "/api/v1/gana_gato/board/evaluate", json={"ticket": [1], "result": [1] * 8}
        ).status_code
        == 422
    )
    made = client.post(
        "/api/v1/gana_gato/backtests",
        json={"train_size": 1, "number_of_tickets": 2, "random_seed": 3},
    )
    assert made.status_code == 200 and made.json()["roi"] is None
    assert client.get(f"/api/v1/gana_gato/backtests/{made.json()['id']}").status_code == 200
    assert client.get("/api/v1/gana_gato/backtests/999999").status_code == 404
