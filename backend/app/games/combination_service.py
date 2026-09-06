import csv
import hashlib
import io
import random
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations

from app.engines.combination.engine import CombinationGameConfig, combination_statistics
from app.games.combination_domain import AdditionalNumber, CombinationDrawResult

PARSER_VERSION = "combination-csv-1"
ENGINE_VERSION = "combination-1"


@dataclass(frozen=True)
class ImportPreview:
    source_hash: str
    parser_version: str
    rule_version: str
    accepted: tuple[CombinationDrawResult, ...]
    rejected: tuple[dict[str, object], ...]
    duplicates: tuple[str, ...]


@dataclass(frozen=True)
class GenerationRequest:
    number_of_tickets: int
    ticket_size: int
    required_numbers: tuple[int, ...] = ()
    excluded_numbers: tuple[int, ...] = ()
    min_sum: int | None = None
    max_sum: int | None = None
    min_even: int | None = None
    max_even: int | None = None
    min_primes: int | None = None
    max_primes: int | None = None
    max_consecutive: int | None = None
    min_previous_repeats: int | None = None
    max_previous_repeats: int | None = None
    strategy: str = "random"
    random_seed: int = 0


def parse_history(
    raw: bytes | str,
    *,
    game_slug: str,
    config: CombinationGameConfig,
    rule_version: str,
) -> ImportPreview:
    payload = raw.encode() if isinstance(raw, str) else raw
    rows = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    accepted: list[CombinationDrawResult] = []
    rejected: list[dict[str, object]] = []
    duplicates: list[str] = []
    seen: set[str] = set()
    prefix = "F" if game_slug == "melate_retro" else "R"
    for line, row in enumerate(rows, 2):
        try:
            draw_number = str(row.get("CONCURSO", "")).strip()
            naturals = tuple(
                sorted(int(row[f"{prefix}{index}"]) for index in range(1, 7))
            )
            additional = int(row[f"{prefix}7"])
            if not draw_number or len(set(naturals)) != 6 or additional in naturals:
                raise ValueError(
                    "Missing draw, duplicate natural, or repeated additional"
                )
            if any(
                value < config.min_number or value > config.max_number
                for value in (*naturals, additional)
            ):
                raise ValueError("Number outside configured universe")
            draw = CombinationDrawResult(
                game_slug,
                draw_number,
                datetime.strptime(row["FECHA"], "%d/%m/%Y").date(),
                naturals,
                (AdditionalNumber(additional),),
            )
            if draw_number in seen:
                duplicates.append(draw_number)
            else:
                accepted.append(draw)
                seen.add(draw_number)
        except (KeyError, TypeError, ValueError) as exc:
            rejected.append({"line": line, "message": str(exc), "raw": row})
    return ImportPreview(
        hashlib.sha256(payload).hexdigest(),
        PARSER_VERSION,
        rule_version,
        tuple(accepted),
        tuple(rejected),
        tuple(duplicates),
    )


def generate_tickets(
    config: CombinationGameConfig,
    count: int,
    *,
    seed: int,
    strategy: str = "random",
    required: tuple[int, ...] = (),
    excluded: tuple[int, ...] = (),
) -> tuple[tuple[int, ...], ...]:
    if set(required) & set(excluded) or len(required) > config.natural_numbers_drawn:
        raise ValueError("Impossible constraints")
    allowed = [
        number
        for number in range(config.min_number, config.max_number + 1)
        if number not in excluded
    ]
    if len(allowed) < config.natural_numbers_drawn or any(
        number not in allowed for number in required
    ):
        raise ValueError("Impossible constraints")
    rng = random.Random(seed)
    tickets: list[tuple[int, ...]] = []
    attempts = 0
    while len(tickets) < count and attempts < max(1000, count * 100):
        remaining = [number for number in allowed if number not in required]
        candidate = tuple(
            sorted(
                (
                    *required,
                    *rng.sample(
                        remaining, config.natural_numbers_drawn - len(required)
                    ),
                )
            )
        )
        if candidate not in tickets:
            tickets.append(candidate)
        attempts += 1
    if len(tickets) != count:
        raise ValueError("Constraints cannot produce requested unique tickets")
    if strategy == "coverage_optimized":
        tickets.sort(
            key=lambda ticket: sum(
                sum(number in other for number in ticket) for other in tickets
            )
        )
    elif strategy not in {"random", "heuristic_ranked"}:
        raise ValueError("Unknown strategy")
    return tuple(tickets)


def generate(
    config: CombinationGameConfig,
    request: GenerationRequest,
    previous_draw: tuple[int, ...] = (),
) -> tuple[tuple[int, ...], ...]:
    if request.ticket_size not in config.ticket_sizes_allowed:
        raise ValueError("Ticket size is not allowed")
    if (
        request.number_of_tickets < 1
        or request.min_sum is not None
        and request.max_sum is not None
        and request.min_sum > request.max_sum
    ):
        raise ValueError("Impossible constraints")
    required, excluded = set(request.required_numbers), set(request.excluded_numbers)
    universe = set(range(config.min_number, config.max_number + 1))
    if (
        required & excluded
        or not required <= universe
        or not excluded <= universe
        or len(required) > request.ticket_size
    ):
        raise ValueError("Impossible constraints")
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53}
    rng = random.Random(request.random_seed)
    candidates: list[tuple[int, ...]] = []
    attempts = 0
    allowed = sorted(universe - excluded)
    remaining = [n for n in allowed if n not in required]
    while len(candidates) < request.number_of_tickets and attempts < max(
        5000, request.number_of_tickets * 500
    ):
        ticket = tuple(
            sorted(
                (*required, *rng.sample(remaining, request.ticket_size - len(required)))
            )
        )
        attempts += 1
        even = sum(n % 2 == 0 for n in ticket)
        prime = sum(n in primes for n in ticket)
        consecutive = sum(b == a + 1 for a, b in zip(ticket, ticket[1:], strict=False))
        repeats = len(set(ticket) & set(previous_draw))
        total = sum(ticket)
        valid = (
            (request.min_sum is None or total >= request.min_sum)
            and (request.max_sum is None or total <= request.max_sum)
            and (request.min_even is None or even >= request.min_even)
            and (request.max_even is None or even <= request.max_even)
            and (request.min_primes is None or prime >= request.min_primes)
            and (request.max_primes is None or prime <= request.max_primes)
            and (
                request.max_consecutive is None
                or consecutive <= request.max_consecutive
            )
            and (
                request.min_previous_repeats is None
                or repeats >= request.min_previous_repeats
            )
            and (
                request.max_previous_repeats is None
                or repeats <= request.max_previous_repeats
            )
        )
        if valid and ticket not in candidates:
            candidates.append(ticket)
    if len(candidates) < request.number_of_tickets:
        raise ValueError(
            "Constraints cannot produce requested tickets within bounded search"
        )
    if request.strategy == "coverage_optimized":
        pool = candidates.copy()
        selected = [pool.pop(0)]
        while pool and len(selected) < request.number_of_tickets:
            choice = min(
                pool, key=lambda t: (max(len(set(t) & set(s)) for s in selected), t)
            )
            selected.append(choice)
            pool.remove(choice)
        candidates = selected
    elif request.strategy not in {"random", "heuristic_ranked"}:
        raise ValueError("Unknown strategy")
    return tuple(candidates)


def coverage_metrics(
    tickets: tuple[tuple[int, ...], ...], config: CombinationGameConfig
) -> dict[str, float | int]:
    overlaps = [len(set(a) & set(b)) for a, b in combinations(tickets, 2)]
    pairs = {pair for ticket in tickets for pair in combinations(ticket, 2)}
    triples = {triple for ticket in tickets for triple in combinations(ticket, 3)}
    universe = config.max_number - config.min_number + 1
    return {
        "unique_numbers_covered": len({n for t in tickets for n in t}),
        "mean_ticket_overlap": sum(overlaps) / len(overlaps) if overlaps else 0.0,
        "max_ticket_overlap": max(overlaps, default=0),
        "pair_coverage": len(pairs) / __import__("math").comb(universe, 2),
        "triple_coverage": len(triples) / __import__("math").comb(universe, 3),
    }


def stats_for(
    draws: list[CombinationDrawResult], game_slug: str, config: CombinationGameConfig
) -> dict[str, object]:
    if any(draw.game_slug != game_slug for draw in draws):
        raise ValueError("Cross-game history contamination")
    return combination_statistics(
        [
            draw.natural_numbers
            for draw in sorted(
                draws, key=lambda item: (item.draw_date, item.draw_number)
            )
        ],
        config,
    )
