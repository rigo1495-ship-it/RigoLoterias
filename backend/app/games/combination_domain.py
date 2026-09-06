from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.engines.combination.engine import CombinationGameConfig, normalize_selection


@dataclass(frozen=True)
class AdditionalNumber:
    value: int


@dataclass(frozen=True)
class CombinationDrawResult:
    game_slug: str
    draw_number: str
    draw_date: date
    natural_numbers: tuple[int, ...]
    additional_numbers: tuple[AdditionalNumber, ...] = ()


@dataclass(frozen=True)
class CombinationTicket:
    numbers: tuple[int, ...]

    @classmethod
    def create(cls, values: list[int], config: CombinationGameConfig) -> "CombinationTicket":
        return cls(normalize_selection(values, config))


@dataclass(frozen=True)
class CombinationPrizeRule:
    natural_hits: int
    additional_hits: int
    prize_per_unit: Decimal
    version: str
    source: str
    verified: bool
