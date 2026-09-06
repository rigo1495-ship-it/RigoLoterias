from datetime import datetime

import pytest

from app.engines.pool_prediction.engine import (
    MEDIA_SEMANA_CONFIG,
    PROGOL_CONFIG,
    REVANCHA_CONFIG,
    MatchOutcome,
    PoolSelection,
    PoolTicket,
    ProbabilityVector,
    coverage_metrics,
    expand,
    expanded_line_count,
    from_legacy_code,
    hamming,
    settle,
    ticket_cost,
)


def ticket(config, doubles=0, triples=0):
    selections = [PoolSelection(frozenset({MatchOutcome.HOME})) for _ in range(config.match_count)]
    for index in range(doubles):
        selections[index] = PoolSelection(frozenset({MatchOutcome.HOME, MatchOutcome.DRAW}))
    for index in range(doubles, doubles + triples):
        selections[index] = PoolSelection(frozenset(MatchOutcome))
    return PoolTicket(tuple(selections))


def test_configs_outcomes_legacy_mapping_and_order() -> None:
    assert (
        PROGOL_CONFIG.match_count,
        PROGOL_CONFIG.supplementary_match_count,
        MEDIA_SEMANA_CONFIG.match_count,
    ) == (14, 7, 9)
    assert [from_legacy_code(value) for value in (1, 0, 3)] == [
        MatchOutcome.HOME,
        MatchOutcome.DRAW,
        MatchOutcome.AWAY,
    ]
    assert (
        hamming((MatchOutcome.HOME, MatchOutcome.DRAW), (MatchOutcome.DRAW, MatchOutcome.HOME)) == 2
    )
    with pytest.raises(ValueError):
        from_legacy_code(2)


@pytest.mark.parametrize(
    "doubles,triples,expected",
    [
        (0, 0, 1),
        (1, 0, 2),
        (2, 0, 4),
        (3, 0, 8),
        (0, 1, 3),
        (1, 1, 6),
        (2, 1, 12),
        (3, 1, 24),
        (0, 2, 9),
        (1, 2, 18),
        (2, 2, 36),
        (3, 2, 72),
    ],
)
def test_media_semana_multiple_expansion_math(doubles, triples, expected) -> None:
    value = ticket(MEDIA_SEMANA_CONFIG, doubles, triples)
    assert expanded_line_count(value, MEDIA_SEMANA_CONFIG) == expected
    assert len(expand(value, MEDIA_SEMANA_CONFIG)) == expected
    assert ticket_cost(value, MEDIA_SEMANA_CONFIG) == expected * 15


def test_progol_and_revancha_limits_settlement_and_coverage() -> None:
    main = ticket(PROGOL_CONFIG, 8, 5)
    assert expanded_line_count(main, PROGOL_CONFIG) == 2**8 * 3**5
    revancha = ticket(REVANCHA_CONFIG, 3, 2)
    assert ticket_cost(revancha, REVANCHA_CONFIG) == 72 * 5
    result = settle(ticket(PROGOL_CONFIG), (MatchOutcome.HOME,) * 14, PROGOL_CONFIG)
    assert result["hits"] == 14 and result["prize_amount"] is None
    metrics = coverage_metrics(
        [ticket(MEDIA_SEMANA_CONFIG), ticket(MEDIA_SEMANA_CONFIG, 1)], MEDIA_SEMANA_CONFIG
    )
    assert metrics["expanded_line_count"] == 3


def test_probability_contract_never_accepts_fabricated_vectors() -> None:
    generated = datetime(2026, 1, 2)
    vector = ProbabilityVector(
        0.4, 0.3, 0.3, "market_only", generated, datetime(2026, 1, 1), "verified"
    )
    assert vector.home == 0.4
    with pytest.raises(ValueError):
        ProbabilityVector(0.4, 0.3, 0.4, "market_only", generated, generated, "bad")
