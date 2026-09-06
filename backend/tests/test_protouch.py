import pytest

from app.engines.protouch.engine import (
    InitialTeam,
    ProtouchInitialSelection,
    ProtouchOutcome,
    ProtouchTicket,
    expanded_line_count,
    resolve_protouch_outcome,
    settle,
    ticket_cost,
)
from app.games.protouch.service import parse_history


def selections(doubles: int = 0, triples: int = 0):
    values = [frozenset({ProtouchOutcome.LOCAL}) for _ in range(13)]
    for index in range(doubles):
        values[index] = frozenset({ProtouchOutcome.LOCAL, ProtouchOutcome.DIFFERENCE})
    for index in range(doubles, doubles + triples):
        values[index] = frozenset(ProtouchOutcome)
    return tuple(values)


@pytest.mark.parametrize(
    ("margin", "expected"),
    [(7, "L"), (6, "D"), (1, "D"), (0, "D"), (-1, "D"), (-6, "D"), (-7, "V")],
)
def test_official_six_point_boundaries(margin, expected):
    assert resolve_protouch_outcome(max(margin, 0), max(-margin, 0)).value == expected


def test_initial_domain_and_multiple_limits():
    assert ProtouchInitialSelection(InitialTeam.NO_TOUCHDOWN, None)
    with pytest.raises(ValueError):
        ProtouchInitialSelection(InitialTeam.LOCAL, None)
    assert expanded_line_count(ProtouchTicket(selections(2, 4))) == 324
    assert ticket_cost(ProtouchTicket(selections(2, 4))) == 3240
    with pytest.raises(ValueError):
        ProtouchTicket(selections(3, 4))
    with pytest.raises(ValueError):
        ProtouchTicket(selections(2, 5))


def test_settlement_initial_is_separate():
    ticket = ProtouchTicket(selections(), ProtouchInitialSelection(InitialTeam.LOCAL, 1))
    result = settle(
        ticket, tuple([ProtouchOutcome.LOCAL] * 13), ProtouchInitialSelection(InitialTeam.LOCAL, 1)
    )
    assert result["main_hits"] == 13 and result["initial_hit"] is True


def test_official_history_parser_preserves_order():
    parsed = parse_history(
        "NPRODUCTO,CONCURSO,R1,R2,R3,R4,R5,R6,R7,R8,R9,R10,R11,R12,R13,BOLSA,FECHA\n30,1,L,D,V,L,D,V,L,D,V,L,D,V,L,100,01/01/2026\n"
    )
    row = parsed["accepted"][0]
    assert row.contest_number == "1" and [value.value for value in row.outcomes] == [
        "L",
        "D",
        "V",
    ] * 4 + ["L"]
