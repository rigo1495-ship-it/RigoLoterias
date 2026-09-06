from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROGOL = (
    "CONCURSO,R1,R2,R3,R4,R5,R6,R7,R8,R9,R10,R11,R12,R13,R14,FECHA\n"
    "F9001,L,E,V,L,E,V,L,E,V,L,E,V,L,E,01/01/2026\n"
)
MEDIA = (
    "CONCURSO,R1,R2,R3,R4,R5,R6,R7,R8,R9,FECHA\n"
    "F9001,L,E,V,L,E,V,L,E,V,01/01/2026\n"
    "F9002,E,V,L,E,V,L,E,V,L,02/01/2026\n"
)


def test_pool_config_import_statistics_and_isolation() -> None:
    assert client.get("/api/v1/progol/config").json()["match_count"] == 14
    assert client.get("/api/v1/progol_media_semana/config").json()["max_doubles"] == 3
    result = client.post("/api/v1/progol/imports", json={"csv_text": PROGOL, "commit": True})
    assert result.status_code == 200 and result.json()["accepted_rows"] == 1
    assert client.get("/api/v1/progol/contests/latest").json()["contest_number"] == "F9001"
    client.post("/api/v1/progol_media_semana/imports", json={"csv_text": MEDIA, "commit": True})
    assert (
        client.get("/api/v1/progol_media_semana/contests/latest").json()["contest_number"]
        == "F9002"
    )
    assert "entropy" in client.get("/api/v1/progol_media_semana/statistics").json()
    assert client.get("/api/v1/gana_gato/config").status_code == 200


def test_portfolio_settlement_backtest_and_errors() -> None:
    portfolio = client.post(
        "/api/v1/progol_media_semana/portfolios", json={"number_of_portfolios": 2, "random_seed": 4}
    )
    assert portfolio.status_code == 200 and portfolio.json()["line_count"] == 2
    invalid = client.post(
        "/api/v1/progol_media_semana/portfolios", json={"fixed_outcomes": {"0": "X"}}
    )
    assert invalid.status_code == 422
    selection = [["L"] for _ in range(9)]
    settled = client.post(
        "/api/v1/progol_media_semana/contests/F9002/settle", json={"selections": selection}
    )
    assert settled.status_code == 200 and "hits" in settled.json()
    made = client.post("/api/v1/progol_media_semana/backtests", json={"train_size": 1})
    assert made.status_code == 200 and made.json()["roi"] is None
    assert (
        client.get(f"/api/v1/progol_media_semana/backtests/{made.json()['id']}").status_code == 200
    )
    assert client.get("/api/v1/progol/backtests/99999").status_code == 404
