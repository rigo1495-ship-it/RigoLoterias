from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CombinationEngine(Protocol):
    def analyze_combinations(self, history: object, config: Mapping[str, Any]) -> object: ...


@runtime_checkable
class PositionalEngine(Protocol):
    def analyze_positions(self, history: object, config: Mapping[str, Any]) -> object: ...


@runtime_checkable
class BoardPatternEngine(Protocol):
    def analyze_board_patterns(self, history: object, config: Mapping[str, Any]) -> object: ...


@runtime_checkable
class PoolPredictionEngine(Protocol):
    def predict_contest(self, contest: object, config: Mapping[str, Any]) -> object: ...


@runtime_checkable
class ProtouchEngine(Protocol):
    def predict_protouch(self, contest: object, config: Mapping[str, Any]) -> object: ...
