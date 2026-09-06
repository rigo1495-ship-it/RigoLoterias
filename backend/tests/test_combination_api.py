from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
HEADER = "NPRODUCTO,CONCURSO,R1,R2,R3,R4,R5,R6,R7,BOLSA,FECHA\n"
RETRO = "NPRODUCTO,CONCURSO,F1,F2,F3,F4,F5,F6,F7,BOLSA,FECHA\n"


def test_config_and_empty_unknown_resources() -> None:
    assert client.get("/api/v1/melate/config").json()["max_number"] == 56
    assert client.get("/api/v1/melate_retro/config").json()["max_number"] == 39
    chispazo = client.get("/api/v1/chispazo/config").json()
    assert chispazo["max_number"] == 28 and chispazo["natural_numbers_drawn"] == 5
    assert client.get("/api/v1/unknown/config").status_code == 404
    assert client.get("/api/v1/melate/backtests/999999").status_code == 404


def test_import_validation_persistence_latest_and_isolation() -> None:
    mel = HEADER + "40,900001,1,2,3,4,5,56,6,0,01/01/2020\n"
    retro = RETRO + "30,900001,1,2,3,4,5,39,6,0,01/01/2020\n"
    assert (
        client.post("/api/v1/melate/imports", json={"csv_text": mel, "commit": True}).json()[
            "accepted_rows"
        ]
        == 1
    )
    assert (
        client.post(
            "/api/v1/melate_retro/imports", json={"csv_text": retro, "commit": True}
        ).json()["accepted_rows"]
        == 1
    )
    assert client.get("/api/v1/melate/draws/latest").json()["game_slug"] == "melate"
    assert client.get("/api/v1/melate_retro/draws/latest").json()["game_slug"] == "melate_retro"
    melate_rows = client.get("/api/v1/melate/draws").json()
    retro_rows = client.get("/api/v1/melate_retro/draws").json()
    assert (
        next(row for row in melate_rows if row["draw_number"] == "900001")["natural_numbers"][-1]
        == 56
    )
    assert (
        next(row for row in retro_rows if row["draw_number"] == "900001")["natural_numbers"][-1]
        == 39
    )
    bad = HEADER + "40,2,1,1,3,4,5,60,6,0,01/01/2020\n"
    result = client.post("/api/v1/melate/imports/preview", json={"csv_text": bad})
    assert result.status_code == 200 and result.json()["rejected_rows"] == 1


def test_statistics_generation_coverage_and_errors() -> None:
    assert "frequency" in client.get("/api/v1/melate/statistics").json()
    body = {
        "number_of_tickets": 3,
        "ticket_size": 6,
        "strategy": "coverage_optimized",
        "random_seed": 9,
    }
    first = client.post("/api/v1/melate/portfolios", json=body)
    second = client.post("/api/v1/melate/portfolios", json=body)
    assert first.status_code == 200 and first.json()["tickets"] == second.json()["tickets"]
    assert "pair_coverage" in first.json()["coverage"]
    impossible = {**body, "required_numbers": [1], "excluded_numbers": [1]}
    assert client.post("/api/v1/melate/portfolios", json=impossible).status_code == 422
    assert client.post("/api/v1/melate/portfolios", json={}).status_code == 200


def test_backtest_contract_and_cross_game_keys() -> None:
    for slug, prefix in (("melate", HEADER), ("melate_retro", RETRO)):
        rows = "".join(f"40,{910000+i},1,2,3,4,5,6,7,0,{i+1:02d}/02/2020\n" for i in range(8))
        client.post(f"/api/v1/{slug}/imports", json={"csv_text": prefix + rows, "commit": True})
        made = client.post(
            f"/api/v1/{slug}/backtests",
            json={"train_size": 3, "number_of_tickets": 2, "random_seed": 3},
        )
        assert (
            made.status_code == 200
            and made.json()["roi"] is None
            and made.json()["game_slug"] == slug
        )
        assert client.get(f"/api/v1/{slug}/backtests/{made.json()['id']}").status_code == 200


def test_chispazo_api_import_generation_and_isolation() -> None:
    csv_text = "CONCURSO,R1,R2,R3,R4,R5,FECHA\n900001,1,2,3,4,28,01/01/2020\n"
    imported = client.post("/api/v1/chispazo/imports", json={"csv_text": csv_text, "commit": True})
    assert imported.status_code == 200 and imported.json()["accepted_rows"] == 1
    latest = client.get("/api/v1/chispazo/draws/latest").json()
    assert latest["game_slug"] == "chispazo" and latest["additional_numbers"] == []
    body = {"number_of_tickets": 3, "ticket_size": 5, "random_seed": 17}
    one = client.post("/api/v1/chispazo/portfolios", json=body)
    two = client.post("/api/v1/chispazo/portfolios", json=body)
    assert one.status_code == 200 and one.json()["tickets"] == two.json()["tickets"]
    assert all(max(ticket) <= 28 and len(ticket) == 5 for ticket in one.json()["tickets"])
    bad = client.post("/api/v1/chispazo/portfolios", json={**body, "required_numbers": [29]})
    assert bad.status_code == 422
