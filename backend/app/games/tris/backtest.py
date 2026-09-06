from typing import cast

from app.games.tris.domain import TrisDrawResult
from app.games.tris.generator import generate_portfolio


def walk_forward_backtest(
    draws: list[TrisDrawResult],
    *,
    train_size: int = 10,
    ticket_count: int = 10,
    strategy: str = "heuristic_ranked",
    seed: int = 0,
) -> dict[str, object]:
    ordered = sorted(draws, key=lambda draw: (draw.draw_date, draw.draw_number))
    steps: list[dict[str, object]] = []
    baseline_hits = analytic_hits = winning_draws = 0
    for target_index in range(train_size, len(ordered)):
        history, target = ordered[:target_index], ordered[target_index]
        analytic = generate_portfolio(history, ticket_count, strategy, seed + target_index)
        baseline = generate_portfolio(history, ticket_count, "random", seed + target_index)
        hits = int(target.winning_number in analytic.tickets)
        base_hits = int(target.winning_number in baseline.tickets)
        analytic_hits += hits
        baseline_hits += base_hits
        winning_draws += bool(hits)
        steps.append(
            {
                "target_draw_number": target.draw_number,
                "history_end_draw_number": history[-1].draw_number,
                "tickets_generated": ticket_count,
                "hits": hits,
                "baseline_hits": base_hits,
                "tickets": analytic.tickets,
            }
        )
    tested = len(steps)
    total_tickets = tested * ticket_count
    return {
        "strategy": strategy,
        "seed": seed,
        "draws_tested": tested,
        "tickets_generated": total_tickets,
        "winning_tickets": analytic_hits,
        "winning_draws": winning_draws,
        "ticket_hit_rate": analytic_hits / total_tickets if total_tickets else 0.0,
        "draw_hit_rate": winning_draws / tested if tested else 0.0,
        "hits_by_level": {"directa_5": analytic_hits},
        "hits_per_1000": analytic_hits * 1000 / total_tickets if total_tickets else 0.0,
        "average_hits": analytic_hits / tested if tested else 0.0,
        "max_hits": max((cast(int, step["hits"]) for step in steps), default=0),
        "roi": None,
        "random_baseline": {
            "tickets_generated": total_tickets,
            "winning_tickets": baseline_hits,
        },
        "steps": steps,
    }
