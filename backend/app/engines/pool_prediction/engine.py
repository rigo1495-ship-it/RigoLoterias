import random
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from itertools import product
from math import log2


class MatchOutcome(StrEnum):
    HOME = "L"
    DRAW = "E"
    AWAY = "V"


class OfficialResultStatus(StrEnum):
    PLAYED_RESULT = "played_result"
    OFFICIAL_ASSIGNED_RESULT = "official_assigned_result"
    ADMINISTRATIVE_DRAW = "administrative_draw"
    CANCELLED = "cancelled"
    SUBSTITUTED = "substituted"
    PENDING = "pending"


@dataclass(frozen=True)
class PoolGameConfig:
    game_slug: str
    match_count: int
    unit_cost_mxn: int
    max_doubles: int
    max_triples: int
    supplementary_match_count: int | None = None
    supplementary_unit_cost_mxn: int | None = None


PROGOL_CONFIG = PoolGameConfig("progol", 14, 15, 8, 5, 7, 5)
REVANCHA_CONFIG = PoolGameConfig("progol_revancha", 7, 5, 3, 2)
MEDIA_SEMANA_CONFIG = PoolGameConfig("progol_media_semana", 9, 15, 3, 2)


@dataclass(frozen=True)
class PoolSelection:
    outcomes: frozenset[MatchOutcome]

    def __post_init__(self) -> None:
        if not self.outcomes or not self.outcomes <= set(MatchOutcome):
            raise ValueError("A selection must contain one to three L/E/V outcomes")


@dataclass(frozen=True)
class PoolTicket:
    selections: tuple[PoolSelection, ...]

    def validate(self, config: PoolGameConfig) -> None:
        if len(self.selections) != config.match_count:
            raise ValueError(f"Expected exactly {config.match_count} selections")
        doubles = sum(len(item.outcomes) == 2 for item in self.selections)
        triples = sum(len(item.outcomes) == 3 for item in self.selections)
        if doubles > config.max_doubles or triples > config.max_triples:
            raise ValueError("Multiple-selection limit exceeded")


@dataclass(frozen=True)
class ProbabilityVector:
    home: float
    draw: float
    away: float
    model_type: str
    generated_at: datetime
    data_cutoff: datetime
    source: str
    features_available: tuple[str, ...] = ()
    features_missing: tuple[str, ...] = ()
    model_version: str = "unversioned"

    def __post_init__(self) -> None:
        if (
            any(value < 0 or value > 1 for value in (self.home, self.draw, self.away))
            or abs(self.home + self.draw + self.away - 1) > 1e-6
        ):
            raise ValueError("Probability vector must be normalized in 0..1")
        if self.data_cutoff > self.generated_at:
            raise ValueError("data_cutoff cannot be after generated_at")


def from_legacy_code(value: int) -> MatchOutcome:
    mapping = {1: MatchOutcome.HOME, 0: MatchOutcome.DRAW, 3: MatchOutcome.AWAY}
    if value not in mapping:
        raise ValueError("Legacy outcome must be one of 1, 0, 3")
    return mapping[value]


def expanded_line_count(ticket: PoolTicket, config: PoolGameConfig) -> int:
    ticket.validate(config)
    result = 1
    for selection in ticket.selections:
        result *= len(selection.outcomes)
    return result


def expand(ticket: PoolTicket, config: PoolGameConfig) -> tuple[tuple[MatchOutcome, ...], ...]:
    ticket.validate(config)
    return tuple(product(*(tuple(sorted(item.outcomes)) for item in ticket.selections)))


def ticket_cost(ticket: PoolTicket, config: PoolGameConfig) -> int:
    return expanded_line_count(ticket, config) * config.unit_cost_mxn


def settle(
    ticket: PoolTicket, official: Sequence[MatchOutcome], config: PoolGameConfig
) -> dict[str, object]:
    ticket.validate(config)
    if len(official) != config.match_count:
        raise ValueError("Official result length does not match contest")
    per_match = [
        result in selection.outcomes
        for selection, result in zip(ticket.selections, official, strict=True)
    ]
    return {
        "hits": sum(per_match),
        "per_match": per_match,
        "expanded_line_count": expanded_line_count(ticket, config),
        "prize_amount": None,
    }


def hamming(left: Sequence[MatchOutcome], right: Sequence[MatchOutcome]) -> int:
    if len(left) != len(right):
        raise ValueError("Hamming requires equal length")
    return sum(a != b for a, b in zip(left, right, strict=True))


def pool_statistics(
    history: Sequence[Sequence[MatchOutcome]], config: PoolGameConfig, window: int = 25
) -> dict[str, object]:
    if any(len(row) != config.match_count for row in history):
        raise ValueError("Cross-game or malformed history")
    recent = history[-window:]
    transitions = {
        str(position): dict(
            Counter(
                zip(
                    (row[position].value for row in history),
                    (row[position].value for row in history[1:]),
                    strict=False,
                )
            )
        )
        for position in range(config.match_count)
    }
    patterns = Counter("".join(value.value for value in row) for row in history)
    frequency = Counter(value.value for row in history for value in row)
    total = sum(frequency.values())
    entropy = (
        -sum((count / total) * log2(count / total) for count in frequency.values())
        if total
        else 0.0
    )
    return {
        "contest_count": len(history),
        "frequency": dict(frequency),
        "position_frequency": {
            str(position + 1): dict(Counter(row[position].value for row in history))
            for position in range(config.match_count)
        },
        "recent_frequency": dict(Counter(value.value for row in recent for value in row)),
        "transitions_by_position": transitions,
        "full_pattern_frequency": dict(patterns),
        "entropy": entropy,
        "consecutive_hamming": [
            hamming(left, right) for left, right in zip(history, history[1:], strict=False)
        ],
    }


def generate_ticket(
    config: PoolGameConfig,
    seed: int,
    strategy: str = "random_uniform",
    probabilities: Sequence[ProbabilityVector] = (),
    fixed: dict[int, MatchOutcome] | None = None,
    excluded: dict[int, set[MatchOutcome]] | None = None,
    max_doubles: int | None = None,
    max_triples: int | None = None,
) -> PoolTicket:
    fixed, excluded = fixed or {}, excluded or {}
    if strategy == "probability_ranked" and len(probabilities) != config.match_count:
        raise ValueError("probability_ranked requires a valid vector for every match")
    if strategy not in {"random_uniform", "simple", "coverage_optimized", "probability_ranked"}:
        raise ValueError("Unknown strategy")
    rng = random.Random(seed)
    selections: list[PoolSelection] = []
    for index in range(config.match_count):
        if index in fixed:
            options = {fixed[index]}
        else:
            allowed = list(set(MatchOutcome) - excluded.get(index, set()))
            if not allowed:
                raise ValueError("Impossible excluded outcomes")
            if strategy == "probability_ranked":
                vector = probabilities[index]
                ranked = sorted(
                    zip(
                        (MatchOutcome.HOME, MatchOutcome.DRAW, MatchOutcome.AWAY),
                        (vector.home, vector.draw, vector.away),
                        strict=True,
                    ),
                    key=lambda item: item[1],
                    reverse=True,
                )
                options = {ranked[0][0]}
            else:
                options = {rng.choice(allowed)}
        selections.append(PoolSelection(frozenset(options)))
    ticket = PoolTicket(tuple(selections))
    ticket.validate(
        PoolGameConfig(
            config.game_slug,
            config.match_count,
            config.unit_cost_mxn,
            config.max_doubles if max_doubles is None else min(max_doubles, config.max_doubles),
            config.max_triples if max_triples is None else min(max_triples, config.max_triples),
            config.supplementary_match_count,
            config.supplementary_unit_cost_mxn,
        )
    )
    return ticket


def coverage_metrics(tickets: Sequence[PoolTicket], config: PoolGameConfig) -> dict[str, object]:
    lines = [line for ticket in tickets for line in expand(ticket, config)]
    distances = [
        hamming(left, right) for index, left in enumerate(lines) for right in lines[index + 1 :]
    ]
    coverage = {
        str(position + 1): sorted({line[position].value for line in lines})
        for position in range(config.match_count)
    }
    pairs = {
        (position, line[position].value, line[position + 1].value)
        for line in lines
        for position in range(config.match_count - 1)
    }
    return {
        "expanded_line_count": len(lines),
        "unique_simple_lines": len(set(lines)),
        "duplicate_line_count": len(lines) - len(set(lines)),
        "mean_ticket_hamming_distance": sum(distances) / len(distances) if distances else 0.0,
        "min_ticket_hamming_distance": min(distances, default=0),
        "position_outcome_coverage": coverage,
        "pair_outcome_coverage": len(pairs),
    }
