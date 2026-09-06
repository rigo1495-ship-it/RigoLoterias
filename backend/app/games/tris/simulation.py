import random

from app.games.tris.domain import TrisDrawResult, TrisModality, TrisTicket
from app.games.tris.settlement import ticket_matches


def simulate(ticket_numbers: list[str], iterations: int, seed: int = 0) -> dict[str, object]:
    rng = random.Random(seed)
    tickets = [TrisTicket(TrisModality.DIRECTA_5, number) for number in ticket_numbers]
    hits = 0
    for index in range(iterations):
        number = str(rng.randrange(100000)).zfill(5)
        draw = TrisDrawResult(str(index), __import__("datetime").date.today(), number)
        hits += sum(ticket_matches(draw, ticket) for ticket in tickets)
    return {
        "iterations": iterations,
        "tickets": len(tickets),
        "hits": hits,
        "hit_rate": hits / (iterations * len(tickets)) if tickets else 0.0,
        "seed": seed,
        "roi": None,
    }
