from decimal import Decimal

from app.games.tris.domain import TrisDrawResult, TrisPrizeRule, TrisTicket


def ticket_matches(draw: TrisDrawResult, ticket: TrisTicket) -> bool:
    number = draw.winning_number
    selectors = {
        "numero_inicial": number[0],
        "numero_final": number[-1],
        "par_inicial": number[:2],
        "par_final": number[-2:],
        "directa_3": number[-3:],
        "directa_4": number[-4:],
        "directa_5": number,
    }
    return selectors[ticket.modality.value] == ticket.selected_number


def evaluate_ticket(
    draw: TrisDrawResult, ticket: TrisTicket, prize_rule: TrisPrizeRule | None = None
) -> dict[str, object]:
    matched = ticket_matches(draw, ticket)
    if prize_rule is not None and (
        not prize_rule.verified or prize_rule.modality != ticket.modality
    ):
        raise ValueError("Prize rule must be verified and match the ticket modality.")
    gross = (
        None
        if prize_rule is None or ticket.amount is None
        else (ticket.amount * prize_rule.prize_per_unit if matched else Decimal("0"))
    )
    return {
        "matched": matched,
        "gross_prize": gross,
        "net_prize": gross,
        "roi": None,
        "prize_status": "verified" if prize_rule else "unavailable",
    }
