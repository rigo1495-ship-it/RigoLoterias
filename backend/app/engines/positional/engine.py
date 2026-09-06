from collections import Counter, defaultdict
from statistics import mean, median, pstdev

from app.games.tris.domain import POSITIONS, TrisDrawResult


def positional_statistics(
    draws: list[TrisDrawResult], windows: tuple[int, ...] = (10, 20, 50, 100)
) -> dict[str, object]:
    ordered = sorted(draws, key=lambda draw: (draw.draw_date, draw.draw_number))
    numbers = [draw.winning_number for draw in ordered]
    global_counts = Counter(digit for number in numbers for digit in number)
    by_position = {
        position: Counter(number[index] for number in numbers)
        for index, position in enumerate(POSITIONS)
    }
    delays: dict[str, dict[str, int | None]] = {}
    intervals: dict[str, dict[str, dict[str, float | int | None]]] = {}
    for index, position in enumerate(POSITIONS):
        delays[position] = {}
        intervals[position] = {}
        for digit in "0123456789":
            appearances = [i for i, number in enumerate(numbers) if number[index] == digit]
            gaps = [right - left for left, right in zip(appearances, appearances[1:], strict=False)]
            delays[position][digit] = len(numbers) - 1 - appearances[-1] if appearances else None
            intervals[position][digit] = {
                "appearances": len(appearances),
                "mean": mean(gaps) if gaps else None,
                "median": median(gaps) if gaps else None,
                "stdev": pstdev(gaps) if len(gaps) > 1 else None,
            }
    transitions: dict[str, dict[str, dict[str, int]]] = {}
    for index, position in enumerate(POSITIONS):
        matrix: dict[str, Counter[str]] = defaultdict(Counter)
        for previous, current in zip(numbers, numbers[1:], strict=False):
            matrix[previous[index]][current[index]] += 1
        transitions[position] = {digit: dict(counts) for digit, counts in matrix.items()}
    pair_counts = {
        f"{POSITIONS[i]}-{POSITIONS[j]}": dict(Counter(number[i] + number[j] for number in numbers))
        for i in range(5)
        for j in range(i + 1, 5)
    }
    patterns = {
        "digit_sums": dict(Counter(sum(map(int, number)) for number in numbers)),
        "parity": dict(
            Counter("even" if int(number[-1]) % 2 == 0 else "odd" for number in numbers)
        ),
        "distinct_digits": dict(Counter(len(set(number)) for number in numbers)),
        "internal_repeats": sum(len(set(number)) < 5 for number in numbers),
        "repeats_from_previous": [
            sum(a == b for a, b in zip(numbers[i - 1], numbers[i], strict=True))
            for i in range(1, len(numbers))
        ],
        "adjacent_consecutive": sum(
            any(abs(int(a) - int(b)) == 1 for a, b in zip(number, number[1:], strict=False))
            for number in numbers
        ),
    }
    recent = {
        str(window): {
            position: dict(Counter(number[index] for number in numbers[-window:]))
            for index, position in enumerate(POSITIONS)
        }
        for window in windows
    }
    signals = {
        "FR": {"status": "descriptive", "meaning": "frecuencia reciente"},
        "RE": {"status": "descriptive", "meaning": "repetición interna"},
        "PA": {"status": "descriptive", "meaning": "paridad final"},
        "PR": {"status": "descriptive", "meaning": "repetición contra sorteo previo"},
        "CO": {"status": "descriptive", "meaning": "dígitos consecutivos adyacentes"},
        "LT": {
            "status": "not_implemented",
            "reason": "regla no definida inequívocamente",
        },
        "CA": {
            "status": "not_implemented",
            "reason": "regla no definida inequívocamente",
        },
        "PC": {
            "status": "not_implemented",
            "reason": "regla no definida inequívocamente",
        },
    }
    return {
        "draw_count": len(numbers),
        "global_frequency": dict(global_counts),
        "position_frequency": {key: dict(value) for key, value in by_position.items()},
        "recent_frequency": recent,
        "delays": delays,
        "intervals": intervals,
        "transitions": transitions,
        "position_pairs": pair_counts,
        "patterns": patterns,
        "signals": signals,
    }
