#!/usr/bin/env python3
"""Deterministic adapter comparison against the documented GatoSolver HEAD contract."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))
from app.engines.board_pattern.engine import GanaGatoBoard, evaluate_lines, hamming_distance, prize_category  # noqa: E402

SOURCE_LINES = ((0, 1, 2), (3, 4), (5, 6, 7), (0, 3, 5), (1, 6), (2, 4, 7), (0, 7), (2, 5))


def source_count(ticket: tuple[int, ...], draw: tuple[int, ...]) -> int:
    return sum(all(ticket[index] == draw[index] for index in line) for line in SOURCE_LINES)


def main() -> None:
    cases = [((1,) * 8, (1,) * 8), ((1,) * 8, (2,) * 8), ((1, 2, 3, 4, 5, 1, 2, 3), (1, 2, 4, 4, 5, 2, 2, 3))]
    rows = []
    for ticket, draw in cases:
        target = len(evaluate_lines(GanaGatoBoard(ticket), GanaGatoBoard(draw)))
        source = source_count(ticket, draw)
        rows.append({"ticket": ticket, "draw": draw, "source_lines": source, "target_lines": target, "category": prize_category(target), "hamming": hamming_distance(GanaGatoBoard(ticket), GanaGatoBoard(draw)), "classification": "equal" if source == target else "target_bug"})
    assert all(row["source_lines"] == row["target_lines"] for row in rows)
    print(json.dumps({"source_head": "4a5127ce28d3a6ab9c66abe8ae3310befdc17dbe", "cases": rows}, indent=2))


if __name__ == "__main__":
    main()
