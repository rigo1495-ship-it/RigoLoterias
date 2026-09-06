from datetime import date
from pathlib import Path

import pytest

from app.games.combination_domain import AdditionalNumber, CombinationDrawResult
from app.games.combination_service import generate_tickets, parse_history, stats_for
from app.games.melate.config import CONFIG as MELATE
from app.games.melate.config import RULE_VERSION as MELATE_RULE
from app.games.melate_retro.config import CONFIG as RETRO
from app.games.melate_retro.config import RULE_VERSION as RETRO_RULE

ROOT = Path(__file__).resolve().parents[2]


def test_official_retro_history_and_golden_records() -> None:
    preview = parse_history(
        (ROOT / "fixtures/melate_retro/raw/Melate-Retro.csv").read_bytes(),
        game_slug="melate_retro",
        config=RETRO,
        rule_version=RETRO_RULE,
    )
    assert len(preview.accepted) == 1666 and not preview.rejected
    assert preview.source_hash == "04f37e60e76023a96e60406bc3fba8eb5bbd5c3ce15b4d874e14cc0fc1e6f952"
    latest = preview.accepted[0]
    assert (
        latest.draw_number,
        latest.draw_date,
        latest.natural_numbers,
        latest.additional_numbers[0].value,
    ) == ("1666", date(2026, 9, 5), (7, 22, 23, 26, 27, 37), 13)
    by_id = {draw.draw_number: draw for draw in preview.accepted}
    assert by_id["834"].natural_numbers == (7, 12, 13, 16, 30, 39)
    assert by_id["1"].draw_date == date(2010, 6, 1)


def test_official_melate_history() -> None:
    preview = parse_history(
        (ROOT / "fixtures/melate/raw/Melate.csv").read_bytes(),
        game_slug="melate",
        config=MELATE,
        rule_version=MELATE_RULE,
    )
    assert len(preview.accepted) == 4261 and not preview.rejected


def test_cross_game_isolation_is_enforced() -> None:
    melate = CombinationDrawResult(
        "melate", "1", date(2026, 1, 1), (1, 2, 3, 4, 5, 56), (AdditionalNumber(6),)
    )
    retro = CombinationDrawResult(
        "melate_retro",
        "1",
        date(2026, 1, 1),
        (1, 2, 3, 4, 5, 39),
        (AdditionalNumber(6),),
    )
    assert stats_for([melate], "melate", MELATE)["draw_count"] == 1
    assert stats_for([retro], "melate_retro", RETRO)["draw_count"] == 1
    with pytest.raises(ValueError):
        stats_for([retro], "melate", MELATE)


def test_seeded_generation_and_impossible_constraints() -> None:
    assert generate_tickets(MELATE, 3, seed=7) == generate_tickets(MELATE, 3, seed=7)
    with pytest.raises(ValueError):
        generate_tickets(RETRO, 1, seed=1, required=(1,), excluded=(1,))
