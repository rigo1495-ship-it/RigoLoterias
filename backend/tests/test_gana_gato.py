from datetime import date
from pathlib import Path

from app.engines.board_pattern.engine import (
    BOARD_SPACE_SIZE,
    GanaGatoBoard,
    diversity_metrics,
    generate_boards,
)
from app.games.gana_gato.domain import GanaGatoDrawResult, settle
from app.games.gana_gato.service import parse_history, walk_forward


def test_parser_preserves_temporal_golden_positions() -> None:
    path = Path(__file__).resolve().parents[2] / "fixtures/gana_gato/golden.csv"
    parsed = parse_history(path.read_bytes())
    assert not parsed.rejected
    assert [item.draw_number for item in parsed.accepted] == ["1", "1530", "3058"]
    assert parsed.accepted[1].board.values == (3, 1, 2, 1, 1, 2, 2, 1)


def test_parser_rejects_duplicate_incomplete_date_and_range() -> None:
    header = "CONCURSO,F1,F2,F3,F4,F5,F6,F7,F8,FECHA\n"
    raw = (
        header
        + "1,1,1,1,1,1,1,1,1,01/01/2020\n1,2,2,2,2,2,2,2,2,02/01/2020\n2,1,1,1,1,1,1,1,6,wrong\n"
    )
    parsed = parse_history(raw)
    assert len(parsed.accepted) == 1 and parsed.duplicates == ("1",)
    assert len(parsed.rejected) == 1


def test_settlement_has_verified_cost_but_no_invented_prize_or_roi() -> None:
    board = GanaGatoBoard((1,) * 8)
    result = settle(board, GanaGatoDrawResult("1", date(2020, 1, 1), board))
    assert result.line_count == 8 and result.prize_category == 1
    assert str(result.ticket_cost) == "10.00" and result.prize_amount is None and result.roi is None


def test_generation_reproducibility_constraints_and_coverage() -> None:
    one = generate_boards(5, 17, "coverage_optimized", 3, {"A1": 2}, {"A2": [5]})
    two = generate_boards(5, 17, "coverage_optimized", 3, {"A1": 2}, {"A2": [5]})
    assert one == two and all(item.values[0] == 2 and item.values[1] != 5 for item in one)
    metrics = diversity_metrics(one)
    assert metrics["unique_boards"] == 5 and metrics["min_hamming_distance"] >= 3
    assert metrics["duplicate_board_count"] == 0


def test_walk_forward_is_strict_and_ignores_target_and_future_for_generation() -> None:
    draws = [
        GanaGatoDrawResult(str(i), date(2020, 1, i), GanaGatoBoard((i % 5 + 1,) * 8))
        for i in range(1, 8)
    ]
    original = walk_forward(draws, 3, 2, "random", 9)
    changed = draws.copy()
    changed[3] = GanaGatoDrawResult("4", date(2020, 1, 4), GanaGatoBoard((5, 4, 3, 2, 1, 5, 4, 3)))
    mutated = walk_forward(changed, 3, 2, "random", 9)
    assert original["steps"][0]["portfolio"] == mutated["steps"][0]["portfolio"]
    assert original["steps"][0]["cutoff"] == "3"
    assert walk_forward(draws[:-1], 3, 2, "random", 9)["steps"] == original["steps"][:-1]
    assert BOARD_SPACE_SIZE == 390625
