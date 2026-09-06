#!/usr/bin/env python3
"""Offline retrospective board-space evaluator with explicit temporal splits."""
import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.engines.board_pattern.engine import boards, evaluate_lines  # noqa: E402
from app.games.gana_gato.service import parse_history  # noqa: E402


def evaluate(path: Path, train_end: int, validation_end: int) -> None:
    draws = parse_history(path.read_bytes()).accepted
    ordered = sorted(draws, key=lambda item: item.draw_date)
    splits = {"train": ordered[:train_end], "validation": ordered[train_end:validation_end], "test": ordered[validation_end:]}
    for index, board in enumerate(boards(), 1):
        distributions = {name: Counter(len(evaluate_lines(board, draw.board)) for draw in subset) for name, subset in splits.items()}
        if index <= 5 or index == 390625:
            print(board.values, {name: dict(value) for name, value in distributions.items()})
    print("evaluated_boards=390625 methodology=retrospective_no_future_probability_claim")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--train-end", type=int, required=True)
    parser.add_argument("--validation-end", type=int, required=True)
    args = parser.parse_args()
    evaluate(args.csv, args.train_end, args.validation_end)
