from collections.abc import Callable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PoolContestResultModel
from app.db.session import build_engine
from app.engines.pool_prediction.engine import (
    MEDIA_SEMANA_CONFIG,
    PROGOL_CONFIG,
    MatchOutcome,
    PoolGameConfig,
    PoolSelection,
    PoolTicket,
    coverage_metrics,
    expanded_line_count,
    generate_ticket,
    settle,
    ticket_cost,
)
from app.games.pool_service import (
    PARSER_VERSION,
    RULE_VERSION,
    PoolContestResult,
    backtest,
    parse_history,
    stats,
)

router = APIRouter(tags=["Pool games"])
engine = build_engine()
runs: dict[tuple[str, int], dict[str, object]] = {}
GAMES = {"progol": PROGOL_CONFIG, "progol_media_semana": MEDIA_SEMANA_CONFIG}


class ImportBody(BaseModel):
    csv_text: str
    revancha_csv_text: str | None = None
    commit: bool = False
    source: str = "official"


class PortfolioBody(BaseModel):
    number_of_portfolios: int = Field(1, ge=1, le=100)
    budget: int | None = Field(None, ge=1)
    fixed_outcomes: dict[int, str] = {}
    excluded_outcomes: dict[int, list[str]] = {}
    max_doubles: int | None = Field(None, ge=0)
    max_triples: int | None = Field(None, ge=0)
    strategy: str = "random_uniform"
    random_seed: int = 0


class BacktestBody(BaseModel):
    train_size: int = Field(25, ge=1)
    number_of_portfolios: int = Field(1, ge=1, le=100)
    strategy: str = "random_uniform"
    random_seed: int = 0


class SettlementBody(BaseModel):
    selections: list[list[str]]


def identity(slug: str) -> PoolGameConfig:
    if slug not in GAMES:
        raise HTTPException(404, "Unknown pool game")
    return GAMES[slug]


def history(slug: str) -> list[PoolContestResult]:
    with Session(engine) as session:
        rows = session.scalars(
            select(PoolContestResultModel).where(PoolContestResultModel.game_slug == slug)
        ).all()
        return [
            PoolContestResult(
                row.game_slug,
                row.contest_number,
                row.contest_date,
                tuple(MatchOutcome(value) for value in row.outcomes_json),
                tuple(MatchOutcome(value) for value in row.revancha_outcomes_json),
            )
            for row in rows
        ]


@router.get("/{slug}/config")
def config(slug: str) -> dict[str, object]:
    game = identity(slug)
    return {
        "game_slug": slug,
        "status": "available",
        "match_count": game.match_count,
        "allowed_outcomes": [item.value for item in MatchOutcome],
        "max_doubles": game.max_doubles,
        "max_triples": game.max_triples,
        "unit_cost_mxn": game.unit_cost_mxn,
        "supplementary": (
            {
                "name": "revancha",
                "match_count": game.supplementary_match_count,
                "unit_cost_mxn": game.supplementary_unit_cost_mxn,
            }
            if slug == "progol"
            else None
        ),
        "rule_version": RULE_VERSION,
        "prediction_modes": {
            "market_only": "not_implemented",
            "elo": "not_implemented",
            "form": "not_implemented",
            "ensemble": "not_implemented",
        },
    }


def serialize(draw: PoolContestResult) -> dict[str, object]:
    return {
        "contest_number": draw.contest_number,
        "contest_date": draw.contest_date.isoformat(),
        "official_outcomes": [item.value for item in draw.official_outcomes],
        "revancha_outcomes": [item.value for item in draw.revancha_outcomes],
    }


@router.get("/{slug}/contests")
def contests(slug: str) -> list[dict[str, object]]:
    identity(slug)
    return [
        serialize(item)
        for item in sorted(
            history(slug),
            key=lambda item: (item.contest_date, item.contest_number),
            reverse=True,
        )
    ]


@router.get("/{slug}/contests/latest")
def latest(slug: str) -> dict[str, object]:
    values = contests(slug)
    if not values:
        raise HTTPException(404, "No contests imported")
    return values[0]


@router.get("/{slug}/contests/{contest_id}")
def contest(slug: str, contest_id: str) -> dict[str, object]:
    identity(slug)
    result = next((item for item in history(slug) if item.contest_number == contest_id), None)
    if result is None:
        raise HTTPException(404, "Contest not found")
    return serialize(result)


def do_import(slug: str, body: ImportBody) -> dict[str, object]:
    game = identity(slug)
    preview = parse_history(
        body.csv_text, game, body.revancha_csv_text if slug == "progol" else None
    )
    if body.commit:
        with Session(engine) as session:
            known = set(
                session.scalars(
                    select(PoolContestResultModel.contest_number).where(
                        PoolContestResultModel.game_slug == slug
                    )
                )
            )
            for item in preview.accepted:
                if item.contest_number not in known:
                    session.add(
                        PoolContestResultModel(
                            game_slug=slug,
                            contest_number=item.contest_number,
                            contest_date=item.contest_date,
                            outcomes_json=[value.value for value in item.official_outcomes],
                            revancha_outcomes_json=[
                                value.value for value in item.revancha_outcomes
                            ],
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


@router.post("/{slug}/imports")
def imports(slug: str, body: ImportBody) -> dict[str, object]:
    return do_import(slug, body)


@router.post("/{slug}/imports/preview")
def preview(slug: str, body: ImportBody) -> dict[str, object]:
    return do_import(slug, body.model_copy(update={"commit": False}))


@router.get("/{slug}/statistics")
def statistics(slug: str) -> dict[str, object]:
    return stats(history(slug), identity(slug))


@router.get("/{slug}/analysis")
def analysis(slug: str) -> dict[str, object]:
    return {
        "statistics": statistics(slug),
        "prediction_modes": {
            "market_only": "not_implemented",
            "elo": "not_implemented",
            "form": "not_implemented",
            "ensemble": "not_implemented",
        },
        "public_selection_share": (
            "not_imported; official momios are not treated as market probabilities"
        ),
        "limitations": "Descriptive historical analysis only.",
    }


def to_ticket(body: SettlementBody, game: PoolGameConfig) -> PoolTicket:
    return PoolTicket(
        tuple(
            PoolSelection(frozenset(MatchOutcome(value) for value in selection))
            for selection in body.selections
        )
    )


@router.post("/{slug}/portfolios")
def portfolios(slug: str, body: PortfolioBody) -> dict[str, object]:
    game = identity(slug)
    try:
        fixed = {index: MatchOutcome(value) for index, value in body.fixed_outcomes.items()}
        excluded = {
            index: {MatchOutcome(value) for value in values}
            for index, values in body.excluded_outcomes.items()
        }
        tickets = [
            generate_ticket(
                game,
                body.random_seed + index,
                body.strategy,
                fixed=fixed,
                excluded=excluded,
                max_doubles=body.max_doubles,
                max_triples=body.max_triples,
            )
            for index in range(body.number_of_portfolios)
        ]
        costs = [ticket_cost(ticket, game) for ticket in tickets]
        if body.budget is not None and sum(costs) > body.budget:
            raise ValueError("Requested portfolio exceeds budget")
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "tickets": [
            [[value.value for value in selection.outcomes] for selection in ticket.selections]
            for ticket in tickets
        ],
        "line_count": sum(expanded_line_count(ticket, game) for ticket in tickets),
        "cost_mxn": sum(costs),
        "coverage": coverage_metrics(tickets, game),
        "metadata": {
            "seed": body.random_seed,
            "strategy": body.strategy,
            "rule_version": RULE_VERSION,
        },
    }


@router.post("/{slug}/contests/{contest_id}/settle")
def settlement(slug: str, contest_id: str, body: SettlementBody) -> dict[str, object]:
    game = identity(slug)
    result = next((item for item in history(slug) if item.contest_number == contest_id), None)
    if result is None:
        raise HTTPException(404, "Contest not found")
    try:
        return settle(to_ticket(body, game), result.official_outcomes, game)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/{slug}/backtests")
def backtests(slug: str, body: BacktestBody) -> dict[str, object]:
    result = backtest(
        history(slug),
        identity(slug),
        body.train_size,
        body.number_of_portfolios,
        body.random_seed,
        body.strategy,
    )
    identifier = len(runs) + 1
    result.update(
        {
            "id": identifier,
            "status": "completed",
            "game_slug": slug,
            "parameters": body.model_dump(),
        }
    )
    runs[(slug, identifier)] = result
    return result


@router.get("/{slug}/backtests/{identifier}")
def get_backtest(slug: str, identifier: int) -> dict[str, object]:
    identity(slug)
    if (slug, identifier) not in runs:
        raise HTTPException(404, "Backtest not found")
    return runs[(slug, identifier)]


@router.post("/{slug}/simulations")
def simulations(slug: str, body: PortfolioBody) -> dict[str, object]:
    return {"status": "completed", "baseline": "random_uniform", **portfolios(slug, body)}


# Pool game routes are registered as literals so they do not shadow the existing
# combination-game `/{slug}/...` routes.
router.routes.clear()


def _config_route(slug: str) -> Callable[[], dict[str, object]]:
    def endpoint() -> dict[str, object]:
        return config(slug)

    return endpoint


def _contests_route(slug: str) -> Callable[[], list[dict[str, object]]]:
    def endpoint() -> list[dict[str, object]]:
        return contests(slug)

    return endpoint


def _latest_route(slug: str) -> Callable[[], dict[str, object]]:
    def endpoint() -> dict[str, object]:
        return latest(slug)

    return endpoint


def _contest_route(slug: str) -> Callable[[str], dict[str, object]]:
    def endpoint(contest_id: str) -> dict[str, object]:
        return contest(slug, contest_id)

    return endpoint


def _imports_route(slug: str) -> Callable[[ImportBody], dict[str, object]]:
    def endpoint(body: ImportBody) -> dict[str, object]:
        return imports(slug, body)

    return endpoint


def _preview_route(slug: str) -> Callable[[ImportBody], dict[str, object]]:
    def endpoint(body: ImportBody) -> dict[str, object]:
        return preview(slug, body)

    return endpoint


def _statistics_route(slug: str) -> Callable[[], dict[str, object]]:
    def endpoint() -> dict[str, object]:
        return statistics(slug)

    return endpoint


def _analysis_route(slug: str) -> Callable[[], dict[str, object]]:
    def endpoint() -> dict[str, object]:
        return analysis(slug)

    return endpoint


def _portfolios_route(slug: str) -> Callable[[PortfolioBody], dict[str, object]]:
    def endpoint(body: PortfolioBody) -> dict[str, object]:
        return portfolios(slug, body)

    return endpoint


def _settlement_route(slug: str) -> Callable[[str, SettlementBody], dict[str, object]]:
    def endpoint(contest_id: str, body: SettlementBody) -> dict[str, object]:
        return settlement(slug, contest_id, body)

    return endpoint


def _backtests_route(slug: str) -> Callable[[BacktestBody], dict[str, object]]:
    def endpoint(body: BacktestBody) -> dict[str, object]:
        return backtests(slug, body)

    return endpoint


def _get_backtest_route(slug: str) -> Callable[[int], dict[str, object]]:
    def endpoint(identifier: int) -> dict[str, object]:
        return get_backtest(slug, identifier)

    return endpoint


def _simulations_route(slug: str) -> Callable[[PortfolioBody], dict[str, object]]:
    def endpoint(body: PortfolioBody) -> dict[str, object]:
        return simulations(slug, body)

    return endpoint


for _slug in GAMES:
    _prefix = f"/{_slug}"
    router.add_api_route(f"{_prefix}/config", _config_route(_slug), methods=["GET"])
    router.add_api_route(f"{_prefix}/contests/latest", _latest_route(_slug), methods=["GET"])
    router.add_api_route(
        f"{_prefix}/contests/{{contest_id}}", _contest_route(_slug), methods=["GET"]
    )
    router.add_api_route(f"{_prefix}/contests", _contests_route(_slug), methods=["GET"])
    router.add_api_route(f"{_prefix}/imports/preview", _preview_route(_slug), methods=["POST"])
    router.add_api_route(f"{_prefix}/imports", _imports_route(_slug), methods=["POST"])
    router.add_api_route(f"{_prefix}/statistics", _statistics_route(_slug), methods=["GET"])
    router.add_api_route(f"{_prefix}/analysis", _analysis_route(_slug), methods=["GET"])
    router.add_api_route(f"{_prefix}/portfolios", _portfolios_route(_slug), methods=["POST"])
    router.add_api_route(
        f"{_prefix}/contests/{{contest_id}}/settle", _settlement_route(_slug), methods=["POST"]
    )
    router.add_api_route(
        f"{_prefix}/backtests/{{identifier}}", _get_backtest_route(_slug), methods=["GET"]
    )
    router.add_api_route(f"{_prefix}/backtests", _backtests_route(_slug), methods=["POST"])
    router.add_api_route(f"{_prefix}/simulations", _simulations_route(_slug), methods=["POST"])
