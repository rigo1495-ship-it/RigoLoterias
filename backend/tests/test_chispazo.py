from datetime import date
from decimal import Decimal
from pathlib import Path

from app.engines.combination.engine import expand_selection, ncr
from app.games.chispazo.config import CONFIG, RULE_VERSION
from app.games.chispazo.settlement import settle, ticket_cost
from app.games.combination_backtest import walk_forward
from app.games.combination_service import GenerationRequest, parse_history

ROOT = Path(__file__).resolve().parents[2]


def official():
    return parse_history(
        (ROOT / "fixtures/chispazo/raw/Chispazo.csv").read_bytes(),
        game_slug="chispazo",
        config=CONFIG,
        rule_version=RULE_VERSION,
    )


def test_official_history_and_temporal_golden() -> None:
    preview = official()
    assert len(preview.accepted) == 12234 and not preview.rejected
    assert preview.source_hash == "4d9e15816a9614e2d96fd0d41885a08a4ea1256660e22c6a6066e47fad2f1a06"
    by_id = {draw.draw_number: draw for draw in preview.accepted}
    assert by_id["12234"].natural_numbers == (3, 11, 13, 21, 28)
    assert by_id["6118"].draw_date == date(2017, 12, 31)
    assert by_id["1"].natural_numbers == (4, 7, 11, 21, 24)
    assert by_id["1"].additional_numbers == ()


def test_multiples_cost_and_settlement() -> None:
    assert [ncr(size, 5) for size in (5, 6, 7)] == [1, 6, 21]
    assert [len(expand_selection(list(range(1, size + 1)), CONFIG)) for size in (5, 6, 7)] == [
        1,
        6,
        21,
    ]
    assert ticket_cost([1, 2, 3, 4, 5]) == Decimal("10.00")
    assert ticket_cost([1, 2, 3, 4, 5, 6, 7]) == Decimal("210.00")
    assert settle((1, 2, 3, 4, 5), (1, 2, 8, 9, 10))["prize_amount"] == Decimal("10.00")


def test_same_day_walk_forward_order() -> None:
    draws = sorted(official().accepted, key=lambda draw: (draw.draw_date, int(draw.draw_number)))
    subset = [draw for draw in draws if draw.draw_number in {"12231", "12232", "12233", "12234"}]
    result = walk_forward(subset, "chispazo", CONFIG, GenerationRequest(2, 5, random_seed=8), 1)
    target = next(step for step in result["steps"] if step["target_draw_id"] == "12234")
    assert target["history_cutoff"] == "12233"
