from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.engines.board_pattern.engine import (
    GanaGatoBoard,
    WinningLine,
    evaluate_lines,
    prize_category,
)

RULE_VERSION = "gana-gato-mx-2012-03-07"
COST_RULE_VERSION = "gana-gato-cost-2026-09-06"


@dataclass(frozen=True)
class GanaGatoDrawResult:
    draw_number: str
    draw_date: date
    board: GanaGatoBoard


@dataclass(frozen=True)
class GanaGatoTicket:
    board: GanaGatoBoard


@dataclass(frozen=True)
class Settlement:
    line_count: int
    winning_lines: tuple[WinningLine, ...]
    prize_category: int | None
    prize_amount: None
    ticket_cost: Decimal
    roi: None
    rule_version: str
    cost_rule_version: str


def settle(ticket: GanaGatoBoard, draw: GanaGatoDrawResult) -> Settlement:
    lines = evaluate_lines(ticket, draw.board)
    return Settlement(
        len(lines),
        lines,
        prize_category(len(lines)),
        None,
        Decimal("10.00"),
        None,
        RULE_VERSION,
        COST_RULE_VERSION,
    )
