import math
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from statistics import mean, median, pstdev


@dataclass(frozen=True)
class CombinationGameConfig:
    min_number: int
    max_number: int
    natural_numbers_drawn: int
    additional_numbers_drawn: int
    ticket_sizes_allowed: tuple[int, ...]
    sort_numbers: bool = True

    def __post_init__(self) -> None:
        if self.min_number >= self.max_number or self.natural_numbers_drawn < 1:
            raise ValueError("Invalid combination game configuration")
        if any(size < self.natural_numbers_drawn for size in self.ticket_sizes_allowed):
            raise ValueError("Ticket sizes cannot be smaller than a simple ticket")


def ncr(n: int, r: int) -> int:
    if n < 0 or r < 0 or r > n:
        raise ValueError("nCr requires 0 <= r <= n")
    return math.comb(n, r)


def normalize_selection(
    values: list[int] | tuple[int, ...], config: CombinationGameConfig
) -> tuple[int, ...]:
    numbers = tuple(sorted(values) if config.sort_numbers else values)
    if len(numbers) not in config.ticket_sizes_allowed:
        raise ValueError("Selection size is not allowed")
    if len(set(numbers)) != len(numbers):
        raise ValueError("Duplicate numbers are not allowed")
    if any(number < config.min_number or number > config.max_number for number in numbers):
        raise ValueError("Number outside configured universe")
    return numbers


def expand_selection(
    values: list[int] | tuple[int, ...], config: CombinationGameConfig
) -> tuple[tuple[int, ...], ...]:
    normalized = normalize_selection(values, config)
    return tuple(combinations(normalized, config.natural_numbers_drawn))


def theoretical_probability(config: CombinationGameConfig) -> float:
    universe = config.max_number - config.min_number + 1
    return 1 / ncr(universe, config.natural_numbers_drawn)


def combination_statistics(
    history: list[tuple[int, ...]],
    config: CombinationGameConfig,
    windows: tuple[int, ...] = (25, 50, 100, 250),
) -> dict[str, object]:
    universe = range(config.min_number, config.max_number + 1)
    frequency = Counter(number for draw in history for number in draw)
    appearances = {
        number: [index for index, draw in enumerate(history) if number in draw]
        for number in universe
    }
    intervals = {
        number: [right - left for left, right in zip(indices, indices[1:], strict=False)]
        for number, indices in appearances.items()
    }
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53}
    return {
        "draw_count": len(history),
        "frequency": dict(frequency),
        "window_frequency": {
            str(window): dict(Counter(number for draw in history[-window:] for number in draw))
            for window in windows
        },
        "delays": {
            number: len(history) - 1 - indices[-1] if indices else None
            for number, indices in appearances.items()
        },
        "intervals": {
            number: {
                "values": gaps,
                "mean": mean(gaps) if gaps else None,
                "median": median(gaps) if gaps else None,
                "stdev": pstdev(gaps) if len(gaps) > 1 else None,
            }
            for number, gaps in intervals.items()
        },
        "patterns": {
            "sums": dict(Counter(map(sum, history))),
            "ranges": dict(Counter(max(draw) - min(draw) for draw in history)),
            "parity": dict(Counter(sum(number % 2 == 0 for number in draw) for draw in history)),
            "primes": dict(Counter(sum(number in primes for number in draw) for draw in history)),
            "consecutives": dict(
                Counter(
                    sum(right == left + 1 for left, right in zip(draw, draw[1:], strict=False))
                    for draw in history
                )
            ),
            "previous_repeats": [
                len(set(left) & set(right))
                for left, right in zip(history, history[1:], strict=False)
            ],
        },
        "pairs": {
            str(key): value
            for key, value in Counter(
                pair for draw in history for pair in combinations(draw, 2)
            ).items()
        },
        "triples": {
            str(key): value
            for key, value in Counter(
                triple for draw in history for triple in combinations(draw, 3)
            ).items()
        },
    }
