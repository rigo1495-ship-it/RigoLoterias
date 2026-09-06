#!/usr/bin/env python3
"""Compare only deterministic, audited PROGOL RIGO ELITE concepts."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))
from app.engines.pool_prediction.engine import MEDIA_SEMANA_CONFIG, MatchOutcome, PoolSelection, PoolTicket, expanded_line_count, from_legacy_code  # noqa: E402


def main() -> None:
    assert [from_legacy_code(value).value for value in (1, 0, 3)] == ["L", "E", "V"]
    for doubles, triples, expected in ((0, 0, 1), (3, 0, 8), (0, 2, 9), (3, 2, 72)):
        selections = [PoolSelection(frozenset({MatchOutcome.HOME})) for _ in range(9)]
        for index in range(doubles): selections[index] = PoolSelection(frozenset({MatchOutcome.HOME, MatchOutcome.DRAW}))
        for index in range(doubles, doubles + triples): selections[index] = PoolSelection(frozenset(MatchOutcome))
        assert expanded_line_count(PoolTicket(tuple(selections)), MEDIA_SEMANA_CONFIG) == expected
    print("source_vs_target=equal deterministic_mapping_and_expansion; probability_and_ev=reject_unknown_source")


if __name__ == "__main__": main()
