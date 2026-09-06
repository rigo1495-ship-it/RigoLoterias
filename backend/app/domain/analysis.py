from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AnalysisResult:
    descriptive_statistics: dict[str, Any] = field(default_factory=dict)
    heuristic_scores: dict[str, Any] = field(default_factory=dict)
    mathematical_probabilities: dict[str, Any] = field(default_factory=dict)
    model_outputs: dict[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
