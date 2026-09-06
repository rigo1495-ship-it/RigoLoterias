from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import product
from random import Random


class ProtouchOutcome(StrEnum):
    """Official Protouch result; DIFFERENCE is not a soccer draw."""

    LOCAL = "L"
    DIFFERENCE = "D"
    VISITOR = "V"


class InitialTeam(StrEnum):
    LOCAL = "local"
    VISITOR = "visitor"
    NO_TOUCHDOWN = "no_touchdown"


class ResolutionType(StrEnum):
    PLAYED = "played"
    OFFICIAL_ASSIGNED = "official_assigned"
    LOTTERY_RESOLUTION = "lottery_resolution"
    PENDING = "pending"
    CANCELLED_OR_REPLACED = "cancelled_or_replaced"


def resolve_protouch_outcome(home_score: int, away_score: int) -> ProtouchOutcome:
    """Resolve using the official regulation score, never an inferred final score."""
    difference = home_score - away_score
    if difference > 6:
        return ProtouchOutcome.LOCAL
    if difference < -6:
        return ProtouchOutcome.VISITOR
    return ProtouchOutcome.DIFFERENCE


@dataclass(frozen=True)
class ProtouchInitialSelection:
    team: InitialTeam
    quarter: int | None

    def __post_init__(self) -> None:
        if self.team is InitialTeam.NO_TOUCHDOWN and self.quarter is not None:
            raise ValueError("NO_TOUCHDOWN requires quarter=None")
        if self.team is not InitialTeam.NO_TOUCHDOWN and self.quarter not in {1, 2, 3, 4}:
            raise ValueError("LOCAL/VISITOR requires quarter 1..4")


INITIAL_OUTCOME_SPACE_SIZE = 9


@dataclass(frozen=True)
class ProtouchMultipleRuleVersion:
    version: str = "protouch-official-2026-09-06"
    unit_cost_mxn: int = 10
    max_doubles_only: int = 8
    max_triples_only: int = 5
    max_mixed_doubles: int = 2
    max_mixed_triples: int = 4


RULE = ProtouchMultipleRuleVersion()


@dataclass(frozen=True)
class ProtouchTicket:
    selections: tuple[frozenset[ProtouchOutcome], ...]
    initial: ProtouchInitialSelection | None = None

    def __post_init__(self) -> None:
        if len(self.selections) != 13:
            raise ValueError("A Protouch ticket has exactly 13 ordered matches")
        if any(not selection or len(selection) > 3 for selection in self.selections):
            raise ValueError("Every selection must contain one to three L/D/V outcomes")
        validate_multiple_limits(self.selections)


def selection_counts(selections: tuple[frozenset[ProtouchOutcome], ...]) -> tuple[int, int]:
    return sum(len(item) == 2 for item in selections), sum(len(item) == 3 for item in selections)


def validate_multiple_limits(selections: tuple[frozenset[ProtouchOutcome], ...]) -> None:
    doubles, triples = selection_counts(selections)
    if triples == 0 and doubles <= RULE.max_doubles_only:
        return
    if doubles == 0 and triples <= RULE.max_triples_only:
        return
    if doubles <= RULE.max_mixed_doubles and triples <= RULE.max_mixed_triples:
        return
    raise ValueError("Official multiple limits exceeded")


def expanded_line_count(ticket: ProtouchTicket) -> int:
    result = 1
    for selection in ticket.selections:
        result *= len(selection)
    return result


def ticket_cost(ticket: ProtouchTicket, rule: ProtouchMultipleRuleVersion = RULE) -> int:
    return expanded_line_count(ticket) * rule.unit_cost_mxn


def expand(ticket: ProtouchTicket) -> tuple[tuple[ProtouchOutcome, ...], ...]:
    return tuple(product(*(sorted(values, key=str) for values in ticket.selections)))


def settle(
    ticket: ProtouchTicket,
    official: tuple[ProtouchOutcome, ...],
    initial_result: ProtouchInitialSelection | None = None,
) -> dict[str, object]:
    if len(official) != 13:
        raise ValueError("Official result must contain 13 outcomes")
    matches: list[dict[str, object]] = [
        {
            "match_number": index + 1,
            "predicted": sorted(value.value for value in selected),
            "official": value.value,
            "hit": value in selected,
        }
        for index, (selected, value) in enumerate(zip(ticket.selections, official, strict=True))
    ]
    initial_hit = ticket.initial is not None and ticket.initial == initial_result
    return {
        "main_hits": sum(
            value in selected for selected, value in zip(ticket.selections, official, strict=True)
        ),
        "matches": matches,
        "initial_hit": initial_hit,
        "prize_category": None,
    }


@dataclass(frozen=True)
class ProtouchProbabilityVector:
    local: float
    difference: float
    visitor: float
    source: str
    model_type: str
    generated_at: str
    data_cutoff: str
    model_version: str
    features_available: tuple[str, ...] = ()
    features_missing: tuple[str, ...] = ()
    calibration_status: str = "not_evaluated"

    def __post_init__(self) -> None:
        if any(value < 0 or value > 1 for value in (self.local, self.difference, self.visitor)):
            raise ValueError("Probabilities must be in [0, 1]")
        if abs(self.local + self.difference + self.visitor - 1) > 1e-6:
            raise ValueError("Protouch probabilities must sum to one")


def generate_ticket(seed: int, strategy: str = "random") -> ProtouchTicket:
    if strategy not in {"random", "coverage_optimized"}:
        raise ValueError("probability_ranked is not implemented without validated probabilities")
    random = Random(seed)
    values = tuple(frozenset({random.choice(tuple(ProtouchOutcome))}) for _ in range(13))
    return ProtouchTicket(values)


def coverage_metrics(tickets: list[ProtouchTicket]) -> dict[str, object]:
    lines = [line for ticket in tickets for line in expand(ticket)]
    unique = set(lines)
    distances = [
        sum(a != b for a, b in zip(left, right, strict=True))
        for index, left in enumerate(unique)
        for right in list(unique)[index + 1 :]
    ]
    return {
        "unique_simple_lines": len(unique),
        "expanded_line_count": len(lines),
        "duplicate_line_count": len(lines) - len(unique),
        "mean_hamming_distance": sum(distances) / len(distances) if distances else 0.0,
        "min_hamming_distance": min(distances) if distances else 0,
        "initial_metrics": "separate; no multiple expansion",
    }
