from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from enum import StrEnum

POSITIONS = ("D1", "D2", "D3", "D4", "D5")


def validate_digits(value: str, length: int = 5) -> str:
    if (
        not isinstance(value, str)
        or len(value) != length
        or not value.isascii()
        or not value.isdigit()
    ):
        raise ValueError(f"Expected exactly {length} ASCII digits.")
    return value


class TrisModality(StrEnum):
    NUMERO_INICIAL = "numero_inicial"
    NUMERO_FINAL = "numero_final"
    PAR_INICIAL = "par_inicial"
    PAR_FINAL = "par_final"
    DIRECTA_3 = "directa_3"
    DIRECTA_4 = "directa_4"
    DIRECTA_5 = "directa_5"

    @property
    def digits(self) -> int:
        return {
            "numero_inicial": 1,
            "numero_final": 1,
            "par_inicial": 2,
            "par_final": 2,
            "directa_3": 3,
            "directa_4": 4,
            "directa_5": 5,
        }[self.value]


@dataclass(frozen=True)
class TrisDrawResult:
    draw_number: str
    draw_date: date
    winning_number: str
    draw_time: time | None = None
    draw_name: str = "Sin horario"
    source: str = "manual"
    verified: bool = False

    def __post_init__(self) -> None:
        validate_digits(self.winning_number)

    @property
    def digits(self) -> tuple[int, int, int, int, int]:
        return tuple(int(value) for value in self.winning_number)  # type: ignore[return-value]


@dataclass(frozen=True)
class TrisTicket:
    modality: TrisModality
    selected_number: str
    amount: Decimal | None = None

    def __post_init__(self) -> None:
        validate_digits(self.selected_number, self.modality.digits)


@dataclass(frozen=True)
class TrisPrizeRule:
    modality: TrisModality
    prize_per_unit: Decimal
    rule_version: str
    source: str
    verified: bool
