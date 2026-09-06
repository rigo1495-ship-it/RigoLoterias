from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import GanaGatoDrawResultModel
from app.db.session import build_engine
from app.engines.board_pattern.engine import (
    BOARD_SPACE_SIZE,
    GanaGatoBoard,
    diversity_metrics,
    generate_boards,
)
from app.games.gana_gato.domain import COST_RULE_VERSION, RULE_VERSION, GanaGatoDrawResult, settle
from app.games.gana_gato.service import PARSER_VERSION, parse_history, statistics, walk_forward

router = APIRouter(prefix="/gana_gato", tags=["Gana Gato"])
engine = build_engine()
runs: dict[int, dict[str, object]] = {}


class ImportBody(BaseModel):
    csv_text: str
    commit: bool = False
    source: str = "official"


class PortfolioBody(BaseModel):
    number_of_tickets: int = Field(10, ge=1, le=1000)
    required_position_values: dict[str, int] = {}
    excluded_position_values: dict[str, list[int]] = {}
    minimum_hamming_distance: int = Field(0, ge=0, le=8)
    strategy: str = "random"
    random_seed: int = 0


class BacktestBody(BaseModel):
    train_size: int = Field(25, ge=1)
    number_of_tickets: int = Field(10, ge=1, le=1000)
    strategy: str = "random"
    random_seed: int = 0


class EvaluationBody(BaseModel):
    ticket: list[int]
    result: list[int]


def history() -> list[GanaGatoDrawResult]:
    with Session(engine) as session:
        return [
            GanaGatoDrawResult(row.draw_number, row.draw_date, GanaGatoBoard(tuple(row.board_json)))
            for row in session.scalars(select(GanaGatoDrawResultModel)).all()
        ]


def serialize(draw: GanaGatoDrawResult) -> dict[str, object]:
    return {
        "draw_number": draw.draw_number,
        "draw_date": draw.draw_date.isoformat(),
        "board": draw.board.values,
        "positions": draw.board.as_mapping(),
    }


@router.get("/config")
def config() -> dict[str, object]:
    return {
        "game_slug": "gana_gato",
        "status": "available",
        "positions": ["A1", "A2", "A3", "B1", "B3", "C1", "C2", "C3"],
        "center": "wildcard",
        "values": [1, 2, 3, 4, 5],
        "board_space_size": BOARD_SPACE_SIZE,
        "rule_version": RULE_VERSION,
        "cost_rule_version": COST_RULE_VERSION,
        "ticket_cost_mxn": 10,
    }


@router.get("/draws")
def draws() -> list[dict[str, object]]:
    return [
        serialize(draw)
        for draw in sorted(
            history(), key=lambda item: (item.draw_date, int(item.draw_number)), reverse=True
        )
    ]


@router.get("/draws/latest")
def latest() -> dict[str, object]:
    values = draws()
    if not values:
        raise HTTPException(404, "No draws imported")
    return values[0]


def do_import(body: ImportBody) -> dict[str, object]:
    preview = parse_history(body.csv_text)
    if body.commit:
        with Session(engine) as session:
            known = set(session.scalars(select(GanaGatoDrawResultModel.draw_number)))
            for draw in preview.accepted:
                if draw.draw_number not in known:
                    session.add(
                        GanaGatoDrawResultModel(
                            draw_number=draw.draw_number,
                            draw_date=draw.draw_date,
                            board_json=list(draw.board.values),
                            source=body.source,
                            source_hash=preview.source_hash,
                            parser_version=PARSER_VERSION,
                            rule_version=RULE_VERSION,
                        )
                    )
            session.commit()
    return {
        "source_hash": preview.source_hash,
        "parser_version": PARSER_VERSION,
        "rule_version": RULE_VERSION,
        "accepted_rows": len(preview.accepted),
        "rejected_rows": len(preview.rejected),
        "duplicates": preview.duplicates,
        "errors": preview.rejected,
    }


@router.post("/imports")
def imports(body: ImportBody) -> dict[str, object]:
    return do_import(body)


@router.post("/imports/preview")
def preview(body: ImportBody) -> dict[str, object]:
    return do_import(body.model_copy(update={"commit": False}))


@router.get("/statistics")
def stats() -> dict[str, object]:
    return statistics(history())


@router.get("/analysis")
def analysis() -> dict[str, object]:
    return {
        "statistics": statistics(history()),
        "board_space_size": BOARD_SPACE_SIZE,
        "purpose": "descriptive_not_predictive",
        "roi": None,
    }


@router.post("/portfolios")
def portfolios(body: PortfolioBody) -> dict[str, object]:
    try:
        tickets = generate_boards(
            body.number_of_tickets,
            body.random_seed,
            body.strategy,
            body.minimum_hamming_distance,
            body.required_position_values,
            body.excluded_position_values,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "tickets": [ticket.values for ticket in tickets],
        "coverage": diversity_metrics(tickets),
        "metadata": {
            "seed": body.random_seed,
            "strategy": body.strategy,
            "rule_version": RULE_VERSION,
        },
    }


@router.post("/board/evaluate")
def evaluate(body: EvaluationBody) -> dict[str, object]:
    try:
        result = settle(
            GanaGatoBoard(tuple(body.ticket)),
            GanaGatoDrawResult("manual", date.today(), GanaGatoBoard(tuple(body.result))),
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return asdict(result)


@router.post("/backtests")
def backtests(body: BacktestBody) -> dict[str, object]:
    result = walk_forward(
        history(), body.train_size, body.number_of_tickets, body.strategy, body.random_seed
    )
    identifier = len(runs) + 1
    result.update(
        {
            "id": identifier,
            "status": "completed",
            "strategy": body.strategy,
            "parameters": body.model_dump(),
            "limitations": "Retrospective; no verified prize amounts or ROI.",
        }
    )
    runs[identifier] = result
    return result


@router.get("/backtests/{identifier}")
def get_backtest(identifier: int) -> dict[str, object]:
    if identifier not in runs:
        raise HTTPException(404, "Backtest not found")
    return runs[identifier]


@router.post("/simulations")
def simulations(body: PortfolioBody) -> dict[str, object]:
    portfolio = portfolios(body)
    return {"status": "completed", "simulation": "portfolio_diversity", **portfolio}
