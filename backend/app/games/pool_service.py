import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import cast

from app.engines.pool_prediction.engine import (
    MatchOutcome,
    PoolGameConfig,
    generate_ticket,
    pool_statistics,
    settle,
)

PARSER_VERSION = "pool-results-csv-1"
RULE_VERSION = "progol-mx-official-2026-09-06"


@dataclass(frozen=True)
class PoolContestResult:
    game_slug: str
    contest_number: str
    contest_date: date
    official_outcomes: tuple[MatchOutcome, ...]
    revancha_outcomes: tuple[MatchOutcome, ...] = ()


@dataclass(frozen=True)
class ImportPreview:
    source_hash: str
    accepted: tuple[PoolContestResult, ...]
    rejected: tuple[dict[str, object], ...]
    duplicates: tuple[str, ...]


def parse_history(
    raw: bytes | str, config: PoolGameConfig, revancha: bytes | str | None = None
) -> ImportPreview:
    payload = raw.encode() if isinstance(raw, str) else raw
    supplementary: dict[str, tuple[MatchOutcome, ...]] = {}
    if revancha is not None:
        secondary = revancha.encode() if isinstance(revancha, str) else revancha
        for row in csv.DictReader(io.StringIO(secondary.decode("utf-8-sig"))):
            supplementary[str(row.get("CONCURSO", "")).strip()] = tuple(
                MatchOutcome(row[f"R{index}"]) for index in range(1, 8)
            )
    accepted: list[PoolContestResult] = []
    rejected: list[dict[str, object]] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    for line, row in enumerate(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))), 2):
        try:
            number = str(row.get("CONCURSO", "")).strip()
            outcomes = tuple(
                MatchOutcome(row[f"R{index}"].strip()) for index in range(1, config.match_count + 1)
            )
            if not number:
                raise ValueError("Missing contest number")
            if number in seen:
                duplicates.append(number)
            else:
                accepted.append(
                    PoolContestResult(
                        config.game_slug,
                        number,
                        datetime.strptime(row["FECHA"], "%d/%m/%Y").date(),
                        outcomes,
                        supplementary.get(number, ()),
                    )
                )
                seen.add(number)
        except (KeyError, ValueError, TypeError) as exc:
            rejected.append({"line": line, "message": str(exc), "raw": row})
    return ImportPreview(
        hashlib.sha256(payload).hexdigest(), tuple(accepted), tuple(rejected), tuple(duplicates)
    )


def stats(draws: list[PoolContestResult], config: PoolGameConfig) -> dict[str, object]:
    ordered = sorted(draws, key=lambda item: (item.contest_date, item.contest_number))
    return pool_statistics([draw.official_outcomes for draw in ordered], config)


def backtest(
    draws: list[PoolContestResult],
    config: PoolGameConfig,
    train_size: int,
    count: int,
    seed: int,
    strategy: str,
) -> dict[str, object]:
    ordered = sorted(draws, key=lambda item: (item.contest_date, item.contest_number))
    steps: list[dict[str, object]] = []
    all_hits: list[int] = []
    baseline_hits: list[int] = []
    for index in range(train_size, len(ordered)):
        target = ordered[index]
        cutoff = datetime.combine(ordered[index - 1].contest_date, time.max)
        tickets = [
            generate_ticket(config, seed + index * 100 + offset, strategy)
            for offset in range(count)
        ]
        baseline = [
            generate_ticket(config, seed + index * 100 + offset, "random_uniform")
            for offset in range(count)
        ]
        hits = [
            cast(int, settle(ticket, target.official_outcomes, config)["hits"])
            for ticket in tickets
        ]
        base = [
            cast(int, settle(ticket, target.official_outcomes, config)["hits"])
            for ticket in baseline
        ]
        all_hits.extend(hits)
        baseline_hits.extend(base)
        steps.append(
            {
                "contest_id": target.contest_number,
                "prediction_cutoff": cutoff.isoformat(),
                "source_data_cutoff": cutoff.isoformat(),
                "model_version": "descriptive-pattern-1",
                "features": [],
                "missing_features": ["teams", "market", "elo", "form"],
                "seed": seed + index * 100,
                "official_result": [outcome.value for outcome in target.official_outcomes],
                "hits": hits,
                "baseline_hits": base,
            }
        )
    return {
        "contests_tested": len(steps),
        "simple_lines_generated": len(all_hits),
        "total_hits": sum(all_hits),
        "mean_hits": sum(all_hits) / len(all_hits) if all_hits else 0.0,
        "max_hits": max(all_hits, default=0),
        "distribution_by_hit_count": {
            str(value): all_hits.count(value) for value in range(config.match_count + 1)
        },
        "random_baseline": {
            "simple_lines_generated": len(baseline_hits),
            "total_hits": sum(baseline_hits),
        },
        "roi": None,
        "steps": steps,
    }
