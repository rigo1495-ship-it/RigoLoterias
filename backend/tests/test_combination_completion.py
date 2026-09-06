from datetime import date, timedelta

import pytest

from app.games.combination_backtest import walk_forward
from app.games.combination_domain import CombinationDrawResult
from app.games.combination_service import GenerationRequest, coverage_metrics, generate
from app.games.melate.config import CONFIG


def draws(count: int = 15) -> list[CombinationDrawResult]:
    return [
        CombinationDrawResult(
            "melate",
            str(i),
            date(2026, 1, 1) + timedelta(days=i),
            tuple(range(1 + i % 20, 7 + i % 20)),
        )
        for i in range(count)
    ]


def test_generation_filters_reproducibility_and_bounds() -> None:
    request = GenerationRequest(
        5, 6, (1,), (), 50, 200, 2, 5, 1, 5, 2, 0, 2, "random", 12
    )
    first = generate(CONFIG, request, (1, 2, 3, 4, 5, 6))
    assert first == generate(CONFIG, request, (1, 2, 3, 4, 5, 6))
    assert all(1 in ticket and max(ticket) <= 56 for ticket in first)
    with pytest.raises(ValueError):
        generate(CONFIG, GenerationRequest(1, 6, (1,), (1,)))


def test_coverage_definitions() -> None:
    metrics = coverage_metrics(((1, 2, 3, 4, 5, 6), (1, 7, 8, 9, 10, 11)), CONFIG)
    assert metrics["unique_numbers_covered"] == 11
    assert metrics["mean_ticket_overlap"] == 1
    assert metrics["max_ticket_overlap"] == 1
    assert 0 < metrics["pair_coverage"] < 1


def test_walk_forward_is_reproducible_and_anti_lookahead() -> None:
    source = draws()
    request = GenerationRequest(3, 6, strategy="heuristic_ranked", random_seed=7)
    first = walk_forward(source, "melate", CONFIG, request, 5)
    changed = source.copy()
    changed[8] = CombinationDrawResult(
        "melate", "8", changed[8].draw_date, (30, 31, 32, 33, 34, 35)
    )
    second = walk_forward(changed, "melate", CONFIG, request, 5)
    assert (
        first["steps"][3]["generated_tickets"]
        == second["steps"][3]["generated_tickets"]
    )
    assert first == walk_forward(source, "melate", CONFIG, request, 5)
    assert first["steps"][0]["history_cutoff"] == "4"
    assert first["tickets_generated"] == first["random_baseline"]["tickets_generated"]
