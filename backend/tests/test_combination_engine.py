import math

import pytest

from app.engines.combination.engine import (
    expand_selection,
    ncr,
    normalize_selection,
    theoretical_probability,
)
from app.games.melate.config import CONFIG as MELATE
from app.games.melate_retro.config import CONFIG as RETRO


def test_ncr_small_exhaustive() -> None:
    for n in range(1, 10):
        for r in range(n + 1):
            assert ncr(n, r) == math.factorial(n) // (math.factorial(r) * math.factorial(n - r))


@pytest.mark.parametrize("size", [6, 7, 8, 9, 10])
def test_expansion_count_and_uniqueness(size: int) -> None:
    expanded = expand_selection(list(range(1, size + 1)), MELATE)
    assert len(expanded) == ncr(size, 6) == len(set(expanded))


def test_validation_and_normalization() -> None:
    assert normalize_selection([6, 2, 4, 1, 3, 5], MELATE) == (1, 2, 3, 4, 5, 6)
    with pytest.raises(ValueError):
        normalize_selection([1, 2, 3, 4, 5, 5], MELATE)
    with pytest.raises(ValueError):
        normalize_selection([1, 2, 3, 4, 5, 40], RETRO)


def test_configs_and_probability_are_independent() -> None:
    assert MELATE.max_number == 56 and RETRO.max_number == 39
    assert theoretical_probability(MELATE) == 1 / math.comb(56, 6)
    assert theoretical_probability(RETRO) == 1 / math.comb(39, 6)
