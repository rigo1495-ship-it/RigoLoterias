from typing import cast

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ProtouchContestResultModel
from app.db.session import build_engine
from app.engines.protouch.engine import (
    RULE,
    InitialTeam,
    ProtouchInitialSelection,
    ProtouchOutcome,
    ProtouchTicket,
    coverage_metrics,
    generate_ticket,
    settle,
    ticket_cost,
)
from app.games.protouch.service import (
    PARSER_VERSION,
    RULE_VERSION,
    ProtouchContestResult,
    backtest,
    parse_history,
    statistics,
)

router = APIRouter(prefix="/protouch", tags=["Protouch"])
engine = build_engine()


class ImportBody(BaseModel):
    csv_text: str
    commit: bool = False
    source: str = "official-open-data"


class PortfolioBody(BaseModel):
    number_of_portfolios: int = Field(1, ge=1, le=100)
    strategy: str = "random"
    random_seed: int = 0


class SettlementBody(BaseModel):
    selections: list[list[str]]
    official: list[str]
    initial_team: str | None = None
    initial_quarter: int | None = None


def history() -> list[ProtouchContestResult]:
    with Session(engine) as session:
        return [
            ProtouchContestResult(
                item.contest_number,
                item.contest_date,
                tuple(ProtouchOutcome(value) for value in item.outcomes_json),
                item.prize_pool_mxn,
            )
            for item in session.scalars(select(ProtouchContestResultModel)).all()
        ]


def serialize(item: ProtouchContestResult) -> dict[str, object]:
    return {
        "contest_number": item.contest_number,
        "contest_date": item.contest_date.isoformat(),
        "official_outcomes": [value.value for value in item.outcomes],
        "prize_pool_mxn": item.prize_pool_mxn,
        "initial_result": None,
        "initial_result_status": "not_available_in_official_history_csv",
    }


@router.get("/config")
def config() -> dict[str, object]:
    return {
        "game_slug": "protouch",
        "status": "available",
        "match_count": 13,
        "allowed_outcomes": [value.value for value in ProtouchOutcome],
        "difference_definition": "absolute score difference <= 6",
        "initial_outcomes": 9,
        "unit_cost_mxn": RULE.unit_cost_mxn,
        "multiple_limits": {
            "doubles_only": RULE.max_doubles_only,
            "triples_only": RULE.max_triples_only,
            "mixed": {"doubles": RULE.max_mixed_doubles, "triples": RULE.max_mixed_triples},
        },
        "rule_version": RULE_VERSION,
        "prediction_modes": {
            "market_margin_model": "not_implemented",
            "elo_margin_model": "not_implemented",
            "team_strength_model": "not_implemented",
            "ensemble": "not_implemented",
        },
    }


@router.get("/contests")
def contests() -> list[dict[str, object]]:
    return [
        serialize(item)
        for item in sorted(
            history(), key=lambda item: (item.contest_date, item.contest_number), reverse=True
        )
    ]


@router.get("/contests/latest")
def latest() -> dict[str, object]:
    values = contests()
    if not values:
        raise HTTPException(404, "No contests imported")
    return values[0]


@router.get("/contests/{contest_id}")
def contest(contest_id: str) -> dict[str, object]:
    item = next((item for item in history() if item.contest_number == contest_id), None)
    if item is None:
        raise HTTPException(404, "Contest not found")
    return serialize(item)


def do_import(body: ImportBody) -> dict[str, object]:
    preview = parse_history(body.csv_text)
    if body.commit:
        with Session(engine) as session:
            known = set(session.scalars(select(ProtouchContestResultModel.contest_number)))
            for item in cast(tuple[ProtouchContestResult, ...], preview["accepted"]):
                if item.contest_number not in known:
                    session.add(
                        ProtouchContestResultModel(
                            contest_number=item.contest_number,
                            contest_date=item.contest_date,
                            outcomes_json=[value.value for value in item.outcomes],
                            prize_pool_mxn=item.prize_pool_mxn,
                            source=body.source,
                            source_hash=preview["source_hash"],
                            parser_version=PARSER_VERSION,
                            rule_version=RULE_VERSION,
                        )
                    )
            session.commit()
    return {key: value for key, value in preview.items() if key != "accepted"} | {
        "parser_version": PARSER_VERSION,
        "rule_version": RULE_VERSION,
    }


@router.post("/imports")
def imports(body: ImportBody) -> dict[str, object]:
    return do_import(body)


@router.post("/imports/preview")
def imports_preview(body: ImportBody) -> dict[str, object]:
    return do_import(body.model_copy(update={"commit": False}))


@router.get("/statistics")
def stats() -> dict[str, object]:
    return statistics(history())


@router.get("/analysis")
def analysis() -> dict[str, object]:
    return {
        "statistics": stats(),
        "predictive_model": "not_implemented",
        "public_selection_share": "not_imported; official momios are not market probabilities",
    }


@router.post("/portfolios")
def portfolios(body: PortfolioBody) -> dict[str, object]:
    try:
        tickets = [
            generate_ticket(body.random_seed + index, body.strategy)
            for index in range(body.number_of_portfolios)
        ]
        return {
            "tickets": [
                [
                    "".join(sorted(item.value for item in selection))
                    for selection in ticket.selections
                ]
                for ticket in tickets
            ],
            "line_count": sum(ticket_cost(ticket) // RULE.unit_cost_mxn for ticket in tickets),
            "cost_mxn": sum(ticket_cost(ticket) for ticket in tickets),
            "coverage": coverage_metrics(tickets),
        }
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/backtests")
def backtests(
    train_size: int = 25, number_of_portfolios: int = 1, random_seed: int = 0
) -> dict[str, object]:
    return backtest(history(), train_size, number_of_portfolios, random_seed)


@router.post("/contests/{contest_id}/evaluate")
def evaluate(contest_id: str, body: SettlementBody) -> dict[str, object]:
    try:
        ticket = ProtouchTicket(
            tuple(frozenset(ProtouchOutcome(value) for value in row) for row in body.selections),
            (
                ProtouchInitialSelection(InitialTeam(body.initial_team), body.initial_quarter)
                if body.initial_team
                else None
            ),
        )
        return settle(ticket, tuple(ProtouchOutcome(value) for value in body.official))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
