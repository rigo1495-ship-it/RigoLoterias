from decimal import Decimal

from app.engines.combination.engine import expand_selection
from app.games.chispazo.config import CONFIG


def ticket_cost(selection: list[int]) -> Decimal:
    return Decimal("10.00") * len(expand_selection(selection, CONFIG))


def settle(ticket: tuple[int, ...], winning: tuple[int, ...]) -> dict[str, object]:
    hits = len(set(ticket) & set(winning))
    return {
        "hit_count": hits,
        "prize_category": {5: "first", 4: "second", 3: "third", 2: "fourth"}.get(hits),
        "prize_amount": Decimal("10.00") if hits == 2 else None,
    }
