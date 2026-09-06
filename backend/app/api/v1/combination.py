from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CombinationDrawResultModel
from app.db.session import build_engine
from app.engines.combination.engine import (
    CombinationGameConfig,
    theoretical_probability,
)
from app.games.chispazo.config import CONFIG as CHISPAZO_CONFIG
from app.games.chispazo.config import RULE_VERSION as CHISPAZO_RULE
from app.games.combination_backtest import walk_forward
from app.games.combination_domain import AdditionalNumber, CombinationDrawResult
from app.games.combination_service import (
    GenerationRequest,
    coverage_metrics,
    generate,
    parse_history,
    stats_for,
)
from app.games.melate.config import CONFIG as MELATE_CONFIG
from app.games.melate.config import RULE_VERSION as MELATE_RULE
from app.games.melate_retro.config import CONFIG as RETRO_CONFIG
from app.games.melate_retro.config import RULE_VERSION as RETRO_RULE

router = APIRouter(tags=["Combination games"])
engine = build_engine()
runs: dict[tuple[str, int], dict[str, object]] = {}
GAMES = {
    "chispazo": (CHISPAZO_CONFIG, CHISPAZO_RULE),
    "melate": (MELATE_CONFIG, MELATE_RULE),
    "melate_retro": (RETRO_CONFIG, RETRO_RULE),
}


class ImportBody(BaseModel):
    csv_text: str
    commit: bool = False
    source: str = "official"


class PortfolioBody(BaseModel):
    number_of_tickets: int = Field(10, ge=1, le=1000)
    ticket_size: int = 6
    required_numbers: list[int] = []
    excluded_numbers: list[int] = []
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


class BacktestBody(BaseModel):
    train_size: int = Field(25, ge=1)
    number_of_tickets: int = Field(10, ge=1)
    strategy: str = "random"
    random_seed: int = 0


def identity(slug: str) -> tuple[CombinationGameConfig, str]:
    if slug not in GAMES:
        raise HTTPException(404, "Unknown combination game")
    return GAMES[slug]


@router.get("/{slug}/config")
def game_config(slug: str) -> dict[str, object]:
    config, rule = identity(slug)
    return {
        **config.__dict__,
        "game_slug": slug,
        "rule_version": rule,
        "status": "available",
    }


def history(slug: str) -> list[CombinationDrawResult]:
    with Session(engine) as session:
        rows = session.scalars(
            select(CombinationDrawResultModel).where(CombinationDrawResultModel.game_slug == slug)
        ).all()
        return [
            CombinationDrawResult(
                row.game_slug,
                row.draw_number,
                row.draw_date,
                tuple(row.natural_numbers_json),
                tuple(AdditionalNumber(value) for value in row.additional_numbers_json),
            )
            for row in rows
        ]


@router.get("/{slug}/draws")
def draws(slug: str) -> list[dict[str, object]]:
    identity(slug)
    return [
        {
            "game_slug": draw.game_slug,
            "draw_number": draw.draw_number,
            "draw_date": draw.draw_date.isoformat(),
            "natural_numbers": draw.natural_numbers,
            "additional_numbers": [item.value for item in draw.additional_numbers],
        }
        for draw in sorted(
            history(slug),
            key=lambda item: (item.draw_date, item.draw_number),
            reverse=True,
        )
    ]


@router.get("/{slug}/draws/latest")
def latest(slug: str) -> dict[str, object]:
    values = draws(slug)
    if not values:
        raise HTTPException(404, "No draws imported")
    return values[0]


@router.post("/{slug}/imports")
def imports(slug: str, body: ImportBody) -> dict[str, object]:
    config, rule = identity(slug)
    preview = parse_history(body.csv_text, game_slug=slug, config=config, rule_version=rule)
    if body.commit:
        with Session(engine) as session:
            known = set(
                session.scalars(
                    select(CombinationDrawResultModel.draw_number).where(
                        CombinationDrawResultModel.game_slug == slug
                    )
                )
            )
            for draw in preview.accepted:
                if draw.draw_number not in known:
                    session.add(
                        CombinationDrawResultModel(
                            game_slug=slug,
                            draw_number=draw.draw_number,
                            draw_date=draw.draw_date,
                            natural_numbers_json=list(draw.natural_numbers),
                            additional_numbers_json=[
                                item.value for item in draw.additional_numbers
                            ],
                            source=body.source,
                            source_hash=preview.source_hash,
                            parser_version=preview.parser_version,
                            rule_version=preview.rule_version,
                        )
                    )
            session.commit()
    return {
        "game_slug": slug,
        "source_hash": preview.source_hash,
        "parser_version": preview.parser_version,
        "rule_version": preview.rule_version,
        "accepted_rows": len(preview.accepted),
        "rejected_rows": len(preview.rejected),
        "duplicates": preview.duplicates,
        "errors": preview.rejected,
    }


@router.post("/{slug}/imports/preview")
def preview(slug: str, body: ImportBody) -> dict[str, object]:
    return imports(slug, body.model_copy(update={"commit": False}))


@router.get("/{slug}/statistics")
def statistics(slug: str) -> dict[str, object]:
    config, _ = identity(slug)
    return stats_for(history(slug), slug, config)


@router.get("/{slug}/analysis")
def analysis(slug: str) -> dict[str, object]:
    config, rule = identity(slug)
    return {
        "rule_version": rule,
        "mathematical_probability": theoretical_probability(config),
        "statistics": stats_for(history(slug), slug, config),
        "signals": {
            key: {
                "implemented": key in {"FR", "CO", "RE", "PA", "PR"},
                "definition": ("descriptive" if key in {"FR", "CO", "RE", "PA", "PR"} else None),
                "limitations": "not a probability",
            }
            for key in ("FR", "LT", "CA", "PC", "CO", "RE", "PA", "PR")
        },
    }


@router.post("/{slug}/portfolios")
def portfolios(slug: str, body: PortfolioBody) -> dict[str, object]:
    config, rule = identity(slug)
    request = GenerationRequest(**body.model_dump())
    try:
        tickets = generate(
            config, request, history(slug)[-1].natural_numbers if history(slug) else ()
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "game_slug": slug,
        "tickets": tickets,
        "metadata": {
            "seed": body.random_seed,
            "strategy": body.strategy,
            "rule_version": rule,
            "engine_version": "combination-1",
        },
        "coverage": coverage_metrics(tickets, config),
    }


@router.post("/{slug}/backtests")
def backtests(slug: str, body: BacktestBody) -> dict[str, object]:
    config, rule = identity(slug)
    request = GenerationRequest(
        body.number_of_tickets,
        config.natural_numbers_drawn,
        strategy=body.strategy,
        random_seed=body.random_seed,
    )
    result = walk_forward(history(slug), slug, config, request, body.train_size)
    result.update(
        {
            "game_slug": slug,
            "strategy": body.strategy,
            "parameters": body.model_dump(),
            "random_seed": body.random_seed,
            "rule_version": rule,
            "engine_version": "combination-1",
            "status": "completed",
            "limitations": "Descriptive historical comparison; ROI unavailable.",
        }
    )
    identifier = len(runs) + 1
    runs[(slug, identifier)] = result
    return {"id": identifier, **result}


@router.get("/{slug}/backtests/{identifier}")
def get_backtest(slug: str, identifier: int) -> dict[str, object]:
    identity(slug)
    if (slug, identifier) not in runs:
        raise HTTPException(404, "Backtest not found")
    return {"id": identifier, **runs[(slug, identifier)]}


@router.post("/{slug}/simulations")
def simulations(slug: str, body: PortfolioBody) -> dict[str, object]:
    result = portfolios(slug, body)
    return {
        "game_slug": slug,
        "iterations": body.number_of_tickets,
        "sample": result["tickets"],
        "roi": None,
    }
