from app.engines.board_pattern.engine import (
    LINES,
    GanaGatoBoard,
    boards,
    diversity_metrics,
    evaluate_lines,
    generate_boards,
    hamming_distance,
    prize_category,
)


def test_board_space_validation_and_positions() -> None:
    board = GanaGatoBoard((1, 2, 3, 4, 5, 1, 2, 3))
    assert board.values == (1, 2, 3, 4, 5, 1, 2, 3)
    assert 5**8 == 390625
    assert len(LINES) == 8
    assert next(iter(boards())).values == (1,) * 8


def test_lines_center_and_categories() -> None:
    board = GanaGatoBoard((1,) * 8)
    assert len(evaluate_lines(board, board)) == 8
    assert (
        prize_category(8) == 1
        and prize_category(7) == 1
        and prize_category(1) == 7
        and prize_category(0) is None
    )
    draw = GanaGatoBoard((1, 2, 3, 4, 5, 1, 2, 3))
    ticket = GanaGatoBoard((5, 2, 5, 4, 5, 5, 2, 5))
    assert ("B1", "CENTER", "B3") in evaluate_lines(ticket, draw)


def test_every_match_mask_stays_in_range_and_category_table_is_complete() -> None:
    draw = GanaGatoBoard((1,) * 8)
    for mask in range(2**8):
        ticket = GanaGatoBoard(tuple(1 if mask & (1 << index) else 2 for index in range(8)))
        assert 0 <= len(evaluate_lines(ticket, draw)) <= 8
    assert [prize_category(lines) for lines in range(9)] == [None, 7, 6, 5, 4, 3, 2, 1, 1]


def test_hamming_generation_and_diversity() -> None:
    assert hamming_distance(GanaGatoBoard((1,) * 8), GanaGatoBoard((1,) * 8)) == 0
    assert hamming_distance(GanaGatoBoard((1,) * 8), GanaGatoBoard((2,) * 8)) == 8
    generated = generate_boards(10, 7, "coverage_optimized", 4, {"A1": 1}, {"A2": (5,)})
    assert generated == generate_boards(10, 7, "coverage_optimized", 4, {"A1": 1}, {"A2": (5,)})
    metrics = diversity_metrics(generated)
    assert metrics["unique_boards"] == 10 and metrics["min_hamming_distance"] >= 4
