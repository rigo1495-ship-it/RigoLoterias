from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable


class GameStatus(StrEnum):
    AVAILABLE = "available"
    PLANNED = "planned"
    AWAITING_RULES = "awaiting_rules"
    DISABLED = "disabled"


class Capability(StrEnum):
    HISTORY = "history"
    STATISTICS = "statistics"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    BACKTESTING = "backtesting"
    SIMULATION = "simulation"
    CONTESTS = "contests"
    SETTLEMENT = "settlement"


@runtime_checkable
class HistoricalImporter(Protocol):
    def parse(self, source: object) -> object: ...


@runtime_checkable
class StatisticsEngine(Protocol):
    def calculate(self, history: object, parameters: Mapping[str, Any]) -> object: ...


@runtime_checkable
class StrategyScorer(Protocol):
    def score(self, candidates: object, context: Mapping[str, Any]) -> object: ...


@runtime_checkable
class TicketGenerator(Protocol):
    def generate(
        self, request: object, *, random_seed: int | None = None
    ) -> object: ...


@runtime_checkable
class ResultValidator(Protocol):
    def validate(self, payload: Mapping[str, Any]) -> object: ...


@runtime_checkable
class BacktestStrategy(Protocol):
    def run(self, history: object, parameters: Mapping[str, Any]) -> object: ...


@dataclass(frozen=True)
class GameDefinition:
    slug: str
    display_name: str
    category: str
    status: GameStatus
    capabilities: frozenset[Capability]


@dataclass(frozen=True)
class GameModule:
    definition: GameDefinition
    importer: HistoricalImporter | None = None
    statistics_engine: StatisticsEngine | None = None
    strategy_scorer: StrategyScorer | None = None
    ticket_generator: TicketGenerator | None = None
    result_validator: ResultValidator | None = None
    backtest_strategy: BacktestStrategy | None = None
    simulation_engine: object | None = None
    contest_service: object | None = None
    settlement_service: object | None = None
