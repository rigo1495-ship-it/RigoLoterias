import random
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations, product
from statistics import mean


class BoardPosition(StrEnum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B3 = "B3"
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"


POSITIONS = tuple(BoardPosition)
CENTER = "CENTER"
WinningLine = tuple[str, str, str]
LINES: tuple[WinningLine, ...] = (
    ("A1", "A2", "A3"),
    ("B1", CENTER, "B3"),
    ("C1", "C2", "C3"),
    ("A1", "B1", "C1"),
    ("A2", CENTER, "C2"),
    ("A3", "B3", "C3"),
    ("A1", CENTER, "C3"),
    ("A3", CENTER, "C1"),
)
BOARD_SPACE_SIZE = 5**8


@dataclass(frozen=True)
class GanaGatoBoard:
    values: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.values) != 8 or any(value < 1 or value > 5 for value in self.values):
            raise ValueError("Board requires eight positional values in 1..5")

    def at(self, position: str | BoardPosition) -> int:
        return self.values[POSITIONS.index(BoardPosition(position))]

    def as_mapping(self) -> dict[str, int]:
        return {position.value: self.at(position) for position in POSITIONS}


@dataclass(frozen=True)
class LineEvaluation:
    winning_lines: tuple[WinningLine, ...]

    @property
    def line_count(self) -> int:
        return len(self.winning_lines)


def evaluate_lines(ticket: GanaGatoBoard, draw: GanaGatoBoard) -> tuple[WinningLine, ...]:
    return tuple(
        line
        for line in LINES
        if all(position == CENTER or ticket.at(position) == draw.at(position) for position in line)
    )


def prize_category(line_count: int) -> int | None:
    if not 0 <= line_count <= 8:
        raise ValueError("line_count outside 0..8")
    return None if line_count == 0 else 1 if line_count >= 7 else 8 - line_count


def hamming_distance(left: GanaGatoBoard, right: GanaGatoBoard) -> int:
    return sum(a != b for a, b in zip(left.values, right.values, strict=True))


def boards() -> Iterator[GanaGatoBoard]:
    return (GanaGatoBoard(tuple(values)) for values in product(range(1, 6), repeat=8))


def generate_boards(
    count: int,
    seed: int,
    strategy: str = "random",
    minimum_distance: int = 0,
    required: Mapping[str, int] | None = None,
    excluded: Mapping[str, Sequence[int]] | None = None,
) -> tuple[GanaGatoBoard, ...]:
    required, excluded = required or {}, excluded or {}
    names = {position.value for position in POSITIONS}
    if (
        count < 1
        or not 0 <= minimum_distance <= 8
        or strategy not in {"random", "heuristic_ranked", "coverage_optimized"}
    ):
        raise ValueError("Invalid generation request")
    if any(
        key not in names or value not in range(1, 6) or value in excluded.get(key, ())
        for key, value in required.items()
    ) or any(
        key not in names or not set(values) <= set(range(1, 6)) or len(set(values)) == 5
        for key, values in excluded.items()
    ):
        raise ValueError("Impossible position constraints")
    rng = random.Random(seed)
    candidates: list[GanaGatoBoard] = []
    pool_size = max(count, count * 40 if strategy == "coverage_optimized" else count)
    for _ in range(max(10_000, pool_size * 1_000)):
        values = tuple(
            required.get(
                position.value,
                rng.choice(
                    [
                        value
                        for value in range(1, 6)
                        if value not in excluded.get(position.value, ())
                    ]
                ),
            )
            for position in POSITIONS
        )
        candidate = GanaGatoBoard(values)
        if candidate not in candidates:
            candidates.append(candidate)
        if len(candidates) >= pool_size:
            break
    selected: list[GanaGatoBoard] = []
    while candidates and len(selected) < count:
        valid = [
            item
            for item in candidates
            if all(hamming_distance(item, prior) >= minimum_distance for prior in selected)
        ]
        if not valid:
            break
        choice = (
            max(
                valid,
                key=lambda item: (
                    min(hamming_distance(item, prior) for prior in selected),
                    item.values,
                ),
            )
            if strategy == "coverage_optimized" and selected
            else valid[0]
        )
        selected.append(choice)
        candidates.remove(choice)
    if len(selected) != count:
        raise ValueError("Constraints cannot produce requested boards")
    return tuple(selected)


def diversity_metrics(items: Sequence[GanaGatoBoard]) -> dict[str, object]:
    distances = [hamming_distance(a, b) for a, b in combinations(items, 2)]
    coverage = {
        position.value: sorted({board.at(position) for board in items}) for position in POSITIONS
    }
    return {
        "mean_hamming_distance": mean(distances) if distances else 0.0,
        "min_hamming_distance": min(distances, default=0),
        "max_hamming_distance": max(distances, default=0),
        "unique_boards": len(set(items)),
        "duplicate_board_count": len(items) - len(set(items)),
        "position_value_coverage": coverage,
        "position_value_coverage_ratio": sum(len(values) for values in coverage.values()) / 40,
        "winning_line_pattern_coverage": len(
            {line for board in items for line in _uniform_lines(board)}
        ),
    }


def _uniform_lines(board: GanaGatoBoard) -> tuple[WinningLine, ...]:
    return tuple(
        line
        for line in LINES
        if len({board.at(position) for position in line if position != CENTER}) == 1
    )


def _intervals(history: Sequence[GanaGatoBoard], position: BoardPosition, value: int) -> list[int]:
    hits = [index for index, board in enumerate(history) if board.at(position) == value]
    return [right - left for left, right in zip(hits, hits[1:], strict=False)]


def board_statistics(
    history: Sequence[GanaGatoBoard], recent_window: int = 25
) -> dict[str, object]:
    recent = history[-recent_window:]
    repeat_counts = [
        8 - hamming_distance(left, right) for left, right in zip(history, history[1:], strict=False)
    ]
    return {
        "draw_count": len(history),
        "global_frequency": dict(Counter(value for board in history for value in board.values)),
        "position_frequency": {p.value: dict(Counter(b.at(p) for b in history)) for p in POSITIONS},
        "recent_position_frequency": {
            p.value: dict(Counter(b.at(p) for b in recent)) for p in POSITIONS
        },
        "delays": {
            p.value: {
                v: next((i for i, b in enumerate(reversed(history)) if b.at(p) == v), len(history))
                for v in range(1, 6)
            }
            for p in POSITIONS
        },
        "intervals": {
            p.value: {v: _intervals(history, p, v) for v in range(1, 6)} for p in POSITIONS
        },
        "previous_draw_repeat_distribution": dict(Counter(repeat_counts)),
        "consecutive_hamming_distribution": dict(Counter(8 - count for count in repeat_counts)),
        "board_pattern_frequency": {
            "-".join(map(str, key)): value
            for key, value in Counter(board.values for board in history).items()
        },
        "positional_cooccurrence": {
            f"{left.value}:{right.value}": {
                f"{a}:{b}": count
                for (a, b), count in Counter(
                    (board.at(left), board.at(right)) for board in history
                ).items()
            }
            for left, right in combinations(POSITIONS, 2)
        },
    }
