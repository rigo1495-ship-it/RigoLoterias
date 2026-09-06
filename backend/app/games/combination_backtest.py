from collections import Counter

from app.engines.combination.engine import CombinationGameConfig
from app.games.combination_domain import CombinationDrawResult
from app.games.combination_service import GenerationRequest, generate


def walk_forward(
    draws: list[CombinationDrawResult],
    game_slug: str,
    config: CombinationGameConfig,
    request: GenerationRequest,
    train_size: int,
) -> dict[str, object]:
    if any(draw.game_slug != game_slug for draw in draws):
        raise ValueError("Cross-game history contamination")
    ordered = sorted(draws, key=lambda d: (d.draw_date, int(d.draw_number)))
    steps = []
    baseline_total = 0
    hit_counts: Counter[int] = Counter()
    winning = 0
    for index in range(train_size, len(ordered)):
        history = ordered[:index]
        target = ordered[index]
        derived = GenerationRequest(
            **{**request.__dict__, "random_seed": request.random_seed + index}
        )
        tickets = generate(config, derived, history[-1].natural_numbers)
        baseline = generate(
            config,
            GenerationRequest(
                request.number_of_tickets,
                request.ticket_size,
                random_seed=request.random_seed + index,
            ),
            history[-1].natural_numbers,
        )
        hits = [len(set(ticket) & set(target.natural_numbers)) for ticket in tickets]
        base_hits = [len(set(ticket) & set(target.natural_numbers)) for ticket in baseline]
        baseline_total += sum(value == 6 for value in base_hits)
        hit_counts.update(hits)
        winning += sum(value == 6 for value in hits)
        steps.append(
            {
                "target_draw_id": target.draw_number,
                "history_cutoff": history[-1].draw_number,
                "history_draw_count": len(history),
                "strategy": request.strategy,
                "parameters": request.__dict__,
                "random_seed": request.random_seed + index,
                "generated_tickets": tickets,
                "result": target.natural_numbers,
                "metrics": {"hits": hits},
            }
        )
    total = len(steps) * request.number_of_tickets
    winning_draws = sum(any(value == 6 for value in step["metrics"]["hits"]) for step in steps)  # type: ignore[index]
    return {
        "draws_tested": len(steps),
        "tickets_generated": total,
        "winning_tickets": winning,
        "winning_draws": winning_draws,
        "ticket_hit_rate": winning / total if total else 0.0,
        "draw_hit_rate": winning_draws / len(steps) if steps else 0.0,
        "hits_by_natural_count": dict(hit_counts),
        "additional_hits": 0,
        "hits_per_1000_tickets": winning * 1000 / total if total else 0.0,
        "average_hits": (sum(k * v for k, v in hit_counts.items()) / total if total else 0.0),
        "max_hits": max(hit_counts, default=0),
        "roi": None,
        "return_per_peso_wagered": None,
        "random_baseline": {
            "tickets_generated": total,
            "winning_tickets": baseline_total,
        },
        "steps": steps,
    }
