from datetime import date
from decimal import Decimal

import pytest

from app.engines.positional.engine import positional_statistics
from app.games.tris.backtest import walk_forward_backtest
from app.games.tris.domain import TrisDrawResult, TrisModality, TrisTicket
from app.games.tris.generator import generate_portfolio
from app.games.tris.importer import TrisHistoricalImporter
from app.games.tris.settlement import evaluate_ticket, ticket_matches


def history(count: int = 15) -> list[TrisDrawResult]:
    return [
        TrisDrawResult(str(i), date(2026, 1, i + 1), str(i * 7919 % 100000).zfill(5))
        for i in range(count)
    ]


def test_domain_preserves_leading_zero_and_validates() -> None:
    draw = TrisDrawResult("1", date(2026, 1, 1), "00508")
    assert draw.winning_number == "00508"
    with pytest.raises(ValueError):
        TrisDrawResult("2", date(2026, 1, 1), "508")


@pytest.mark.parametrize(
    ("modality", "selection"),
    [
        (TrisModality.NUMERO_INICIAL, "0"),
        (TrisModality.NUMERO_FINAL, "8"),
        (TrisModality.PAR_INICIAL, "00"),
        (TrisModality.PAR_FINAL, "08"),
        (TrisModality.DIRECTA_3, "508"),
        (TrisModality.DIRECTA_4, "0508"),
        (TrisModality.DIRECTA_5, "00508"),
    ],
)
def test_modalities_match(modality: TrisModality, selection: str) -> None:
    assert ticket_matches(
        TrisDrawResult("1", date(2026, 1, 1), "00508"), TrisTicket(modality, selection)
    )


def test_economic_fields_are_unavailable_without_verified_rule() -> None:
    result = evaluate_ticket(
        TrisDrawResult("1", date(2026, 1, 1), "00508"),
        TrisTicket(TrisModality.DIRECTA_5, "00508", Decimal("10")),
    )
    assert (
        result["matched"] is True
        and result["gross_prize"] is None
        and result["roi"] is None
    )


def test_importer_reports_errors_duplicates_and_hash() -> None:
    preview = TrisHistoricalImporter().parse(
        "draw_id,draw_date,winning_number\n1,2026-01-01,00508\n1,2026-01-02,12345\n3,2026-01-03,123\n"
    )
    assert preview.rows_total == 3 and preview.accepted[0].winning_number == "00508"
    assert (
        preview.duplicates == ("1",)
        and len(preview.rejected) == 1
        and len(preview.source_hash) == 64
    )


def test_statistics_and_signal_contract() -> None:
    result = positional_statistics(history())
    assert result["draw_count"] == 15 and set(result["position_frequency"]) == {
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
    }
    assert result["signals"]["LT"]["status"] == "not_implemented"


def test_random_generation_matches_master_golden_value() -> None:
    result = generate_portfolio([], 3, "random", 42)
    assert result.tickets == ("83810", "14592", "03278")
    assert len(set(result.tickets)) == 3 and result.metadata["seed"] == 42


def test_backtest_is_reproducible_and_has_no_lookahead() -> None:
    draws = history()
    first = walk_forward_backtest(draws, train_size=10, ticket_count=3, seed=7)
    changed = draws[:-1] + [
        TrisDrawResult(draws[-1].draw_number, draws[-1].draw_date, "99999")
    ]
    second = walk_forward_backtest(changed, train_size=10, ticket_count=3, seed=7)
    assert first["steps"][:-1] == second["steps"][:-1]
    assert first["steps"][0]["history_end_draw_number"] == "9"
    assert (
        first["tickets_generated"] == first["random_baseline"]["tickets_generated"]
        and first["roi"] is None
    )
