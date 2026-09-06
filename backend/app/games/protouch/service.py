import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import cast

from app.engines.protouch.engine import ProtouchOutcome, generate_ticket, settle

PARSER_VERSION = "protouch-official-csv-1"
RULE_VERSION = "protouch-reglamento-2012-03-07"


@dataclass(frozen=True)
class ProtouchContestResult:
    contest_number: str
    contest_date: date
    outcomes: tuple[ProtouchOutcome, ...]
    prize_pool_mxn: int


def parse_history(raw: bytes | str) -> dict[str, object]:
    payload = raw.encode() if isinstance(raw, str) else raw
    accepted: list[ProtouchContestResult] = []
    rejected: list[dict[str, object]] = []
    seen: set[str] = set()
    for line, row in enumerate(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))), 2):
        try:
            number = str(row["CONCURSO"]).strip()
            if not number or number in seen:
                raise ValueError("missing or duplicate contest number")
            outcomes = tuple(ProtouchOutcome(row[f"R{index}"].strip()) for index in range(1, 14))
            if len(outcomes) != 13:
                raise ValueError("requires exactly 13 outcomes")
            accepted.append(
                ProtouchContestResult(
                    number,
                    datetime.strptime(row["FECHA"], "%d/%m/%Y").date(),
                    outcomes,
                    int(row["BOLSA"]),
                )
            )
            seen.add(number)
        except (KeyError, TypeError, ValueError) as exc:
            rejected.append({"line": line, "message": str(exc), "raw": row})
    return {
        "source_hash": hashlib.sha256(payload).hexdigest(),
        "accepted": tuple(accepted),
        "rejected": tuple(rejected),
        "accepted_rows": len(accepted),
        "rejected_rows": len(rejected),
    }


def statistics(draws: list[ProtouchContestResult]) -> dict[str, object]:
    ordered = sorted(draws, key=lambda item: (item.contest_date, item.contest_number))
    total = max(1, len(ordered) * 13)
    frequencies = {
        value.value: sum(value in item.outcomes for item in ordered) for value in ProtouchOutcome
    }
    by_position = {
        str(index): {
            value.value: sum(item.outcomes[index - 1] is value for item in ordered)
            for value in ProtouchOutcome
        }
        for index in range(1, 14)
    }
    return {
        "label": "descriptive_statistics",
        "contest_count": len(ordered),
        "frequency": frequencies,
        "frequency_rate": {key: value / total for key, value in frequencies.items()},
        "by_match_position": by_position,
        "difference_per_contest": [
            sum(value is ProtouchOutcome.DIFFERENCE for value in item.outcomes) for item in ordered
        ],
        "initial": "not_available_in_official_history_csv",
    }


def backtest(
    draws: list[ProtouchContestResult], train_size: int, count: int, seed: int
) -> dict[str, object]:
    ordered = sorted(draws, key=lambda item: (item.contest_date, item.contest_number))
    steps = []
    hits = []
    for index in range(train_size, len(ordered)):
        target = ordered[index]
        cutoff = datetime.combine(ordered[index - 1].contest_date, time.max).isoformat()
        tickets = [generate_ticket(seed + index * 100 + offset) for offset in range(count)]
        outcome_hits = [
            cast(int, settle(ticket, target.outcomes)["main_hits"]) for ticket in tickets
        ]
        hits.extend(outcome_hits)
        steps.append(
            {
                "contest_id": target.contest_number,
                "prediction_cutoff": cutoff,
                "source_data_cutoff": cutoff,
                "strategy": "random_uniform",
                "model_version": "descriptive-pattern-1",
                "seed": seed + index * 100,
                "expanded_line_count": count,
                "official_result": [value.value for value in target.outcomes],
                "main_hits": outcome_hits,
                "initial_hit": None,
            }
        )
    return {
        "mode": "descriptive_pattern_backtest",
        "predictive_football_backtest": "not_implemented",
        "contests_tested": len(steps),
        "simple_lines_generated": len(hits),
        "mean_hits": sum(hits) / len(hits) if hits else 0,
        "max_hits": max(hits, default=0),
        "distribution_hits_0_to_13": {str(value): hits.count(value) for value in range(14)},
        "roi": None,
        "steps": steps,
    }
