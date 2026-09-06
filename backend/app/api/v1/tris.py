from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TrisDrawResultModel
from app.db.session import build_engine
from app.engines.positional.engine import positional_statistics
from app.games.tris.backtest import walk_forward_backtest
from app.games.tris.domain import TrisDrawResult
from app.games.tris.generator import generate_portfolio
from app.games.tris.importer import TrisHistoricalImporter
from app.games.tris.simulation import simulate

router = APIRouter(prefix="/tris", tags=["TRIS"])
_engine = build_engine()
_backtests: dict[int, dict[str, object]] = {}


class ImportRequest(BaseModel):
    csv_text: str
    commit: bool = False


class PortfolioRequest(BaseModel):
    count: int = Field(10, ge=1, le=1000)
    strategy: str = "random"
    seed: int | None = None


class BacktestRequest(BaseModel):
    train_size: int = Field(10, ge=1)
    ticket_count: int = Field(10, ge=1, le=1000)
    strategy: str = "heuristic_ranked"
    seed: int = 0


class SimulationRequest(BaseModel):
    tickets: list[str]
    iterations: int = Field(1000, ge=1, le=100000)
    seed: int = 0


def _serialize(draw: TrisDrawResult) -> dict[str, object]:
    value = asdict(draw)
    value["draw_date"] = draw.draw_date.isoformat()
    value["draw_time"] = draw.draw_time.isoformat() if draw.draw_time else None
    return value


def _domain(row: TrisDrawResultModel) -> TrisDrawResult:
    return TrisDrawResult(
        row.draw_number,
        row.draw_date,
        row.winning_number,
        (__import__("datetime").time.fromisoformat(row.draw_time) if row.draw_time else None),
        row.draw_name,
        row.source,
        row.verified,
    )


def _history() -> list[TrisDrawResult]:
    with Session(_engine) as session:
        return [_domain(row) for row in session.scalars(select(TrisDrawResultModel)).all()]


@router.get("/draws")
def draws() -> list[dict[str, object]]:
    return [
        _serialize(draw)
        for draw in sorted(
            _history(),
            key=lambda item: (item.draw_date, item.draw_number),
            reverse=True,
        )
    ]


@router.get("/draws/latest")
def latest() -> dict[str, object]:
    values = draws()
    if not values:
        raise HTTPException(404, "No TRIS draws imported.")
    return values[0]


@router.post("/imports")
def import_draws(request: ImportRequest) -> dict[str, object]:
    preview = TrisHistoricalImporter().parse(request.csv_text)
    if request.commit:
        with Session(_engine) as session:
            for draw in preview.accepted:
                existing = session.scalar(
                    select(TrisDrawResultModel).where(
                        TrisDrawResultModel.draw_number == draw.draw_number
                    )
                )
                if existing is None:
                    session.add(
                        TrisDrawResultModel(
                            draw_number=draw.draw_number,
                            draw_date=draw.draw_date,
                            draw_time=(draw.draw_time.isoformat() if draw.draw_time else None),
                            draw_name=draw.draw_name,
                            winning_number=draw.winning_number,
                            source=draw.source,
                            verified=draw.verified,
                        )
                    )
            session.commit()
    return {
        "source_hash": preview.source_hash,
        "rows_total": preview.rows_total,
        "rows_accepted": len(preview.accepted),
        "rows_rejected": len(preview.rejected),
        "duplicates": preview.duplicates,
        "committed": len(preview.accepted) if request.commit else 0,
        "errors": preview.rejected,
    }


@router.get("/statistics")
def statistics() -> dict[str, object]:
    return positional_statistics(_history())


@router.get("/analysis")
def analysis() -> dict[str, object]:
    history = _history()
    stats = positional_statistics(history)
    return {
        "as_of": max((draw.draw_date for draw in history), default=date.today()).isoformat(),
        "statistics": stats,
        "claim": "descriptive_not_predictive",
    }


@router.post("/portfolios")
def portfolio(request: PortfolioRequest) -> dict[str, object]:
    generated = generate_portfolio(_history(), request.count, request.strategy, request.seed)
    return {"tickets": generated.tickets, "metadata": generated.metadata}


@router.post("/backtests")
def backtest(request: BacktestRequest) -> dict[str, object]:
    result = walk_forward_backtest(
        _history(),
        train_size=request.train_size,
        ticket_count=request.ticket_count,
        strategy=request.strategy,
        seed=request.seed,
    )
    identifier = len(_backtests) + 1
    _backtests[identifier] = result
    return {"id": identifier, **result}


@router.get("/backtests/{identifier}")
def get_backtest(identifier: int) -> dict[str, object]:
    if identifier not in _backtests:
        raise HTTPException(404, "Backtest not found.")
    return {"id": identifier, **_backtests[identifier]}


@router.post("/simulations")
def simulation(request: SimulationRequest) -> dict[str, object]:
    return simulate(request.tickets, request.iterations, request.seed)
