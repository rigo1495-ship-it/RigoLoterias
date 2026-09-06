"""Manual deterministic comparator; excludes unproven source probability/Monte Carlo logic."""
from app.engines.protouch.engine import resolve_protouch_outcome

def compare_outcome(home: int, away: int, source_value: str) -> dict[str, str]:
    target = resolve_protouch_outcome(home, away).value
    return {"source": source_value, "target": target, "classification": "expected_normalization" if source_value == target else "rule_difference"}
