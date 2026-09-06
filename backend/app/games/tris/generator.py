import random
from dataclasses import dataclass
from typing import cast

from app.engines.positional.engine import positional_statistics
from app.games.tris.domain import TrisDrawResult

ENGINE_VERSION = "tris-positional-1"
RULE_VERSION = "tris-core-1"


@dataclass(frozen=True)
class GeneratedPortfolio:
    tickets: tuple[str, ...]
    metadata: dict[str, object]


def generate_portfolio(
    draws: list[TrisDrawResult],
    count: int,
    strategy: str = "random",
    seed: int | None = None,
) -> GeneratedPortfolio:
    if count < 1 or count > 10000:
        raise ValueError("count must be between 1 and 10000")
    rng = random.Random(seed)
    pool = [str(value).zfill(5) for value in range(100000)]
    if strategy == "random":
        tickets = rng.sample(pool, count)
    else:
        stats = positional_statistics(draws)
        raw_frequencies = stats["position_frequency"]
        assert isinstance(raw_frequencies, dict)
        frequencies = cast(dict[str, dict[str, int]], raw_frequencies)

        def score(number: str) -> int:
            return sum(frequencies[f"D{i + 1}"].get(digit, 0) for i, digit in enumerate(number))

        ranked = sorted(pool, key=lambda number: (-score(number), number))
        if strategy == "heuristic_ranked":
            tickets = ranked[:count]
        elif strategy == "coverage_optimized":
            candidates = ranked[: max(1000, count * 25)]
            tickets = [candidates.pop(0)]
            while len(tickets) < count:
                choice = max(
                    candidates,
                    key=lambda candidate: (
                        min(
                            sum(a != b for a, b in zip(candidate, selected, strict=True))
                            for selected in tickets
                        ),
                        score(candidate),
                        candidate,
                    ),
                )
                tickets.append(choice)
                candidates.remove(choice)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    return GeneratedPortfolio(
        tuple(tickets),
        {
            "strategy": strategy,
            "count": count,
            "seed": seed,
            "rule_version": RULE_VERSION,
            "engine_version": ENGINE_VERSION,
        },
    )
