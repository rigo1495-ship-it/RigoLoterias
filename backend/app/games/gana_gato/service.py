import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime

from app.engines.board_pattern.engine import (
    POSITIONS,
    GanaGatoBoard,
    board_statistics,
    generate_boards,
)
from app.games.gana_gato.domain import GanaGatoDrawResult, settle

PARSER_VERSION = "gana-gato-csv-1"


@dataclass(frozen=True)
class ImportPreview:
    source_hash: str
    accepted: tuple[GanaGatoDrawResult, ...]
    rejected: tuple[dict[str, object], ...]
    duplicates: tuple[str, ...]


def parse_history(raw: bytes | str) -> ImportPreview:
    payload = raw.encode() if isinstance(raw, str) else raw
    rows = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    accepted: list[GanaGatoDrawResult] = []
    rejected: list[dict[str, object]] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, 2):
        try:
            draw_number = str(row.get("CONCURSO", "")).strip()
            if not draw_number:
                raise ValueError("Missing draw number")
            board = GanaGatoBoard(tuple(int(row[f"F{index}"]) for index in range(1, 9)))
            draw = GanaGatoDrawResult(
                draw_number, datetime.strptime(row["FECHA"], "%d/%m/%Y").date(), board
            )
            if draw_number in seen:
                duplicates.append(draw_number)
            else:
                accepted.append(draw)
                seen.add(draw_number)
        except (KeyError, TypeError, ValueError) as exc:
            rejected.append({"line": line, "message": str(exc), "raw": row})
    return ImportPreview(
        hashlib.sha256(payload).hexdigest(), tuple(accepted), tuple(rejected), tuple(duplicates)
    )


def statistics(draws: list[GanaGatoDrawResult]) -> dict[str, object]:
    ordered = sorted(draws, key=lambda item: (item.draw_date, int(item.draw_number)))
    values = board_statistics([draw.board for draw in ordered])
    line_frequency = {
        "|".join(line): 0
        for line in __import__("app.engines.board_pattern.engine", fromlist=["LINES"]).LINES
    }
    line_distribution: dict[int, int] = {}
    total_matches: dict[int, int] = {}
    for previous, current in zip(ordered, ordered[1:], strict=False):
        result = settle(previous.board, current)
        line_distribution[result.line_count] = line_distribution.get(result.line_count, 0) + 1
        matches = sum(
            a == b for a, b in zip(previous.board.values, current.board.values, strict=True)
        )
        total_matches[matches] = total_matches.get(matches, 0) + 1
        for line in result.winning_lines:
            key = "|".join(line)
            line_frequency[key] += 1
    values.update(
        {
            "line_count_distribution": line_distribution,
            "line_frequency": line_frequency,
            "total_match_distribution": total_matches,
            "positions": [p.value for p in POSITIONS],
        }
    )
    return values


def walk_forward(
    draws: list[GanaGatoDrawResult], train_size: int, count: int, strategy: str, seed: int
) -> dict[str, object]:
    ordered = sorted(draws, key=lambda item: (item.draw_date, int(item.draw_number)))
    steps: list[dict[str, object]] = []
    for index in range(train_size, len(ordered)):
        target = ordered[index]
        history = ordered[:index]
        tickets = generate_boards(count, seed + index, strategy)
        results = [settle(ticket, target) for ticket in tickets]
        steps.append(
            {
                "target": target.draw_number,
                "cutoff": history[-1].draw_number,
                "history_size": len(history),
                "seed": seed + index,
                "portfolio": [ticket.values for ticket in tickets],
                "line_counts": [item.line_count for item in results],
                "prize_categories": [item.prize_category for item in results],
            }
        )
    return {"steps": steps, "targets": len(steps), "ticket_count": count, "roi": None}
