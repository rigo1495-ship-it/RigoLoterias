from pathlib import Path

from app.engines.pool_prediction.engine import MEDIA_SEMANA_CONFIG, PROGOL_CONFIG
from app.games.pool_service import backtest, parse_history, stats

ROOT = Path(__file__).resolve().parents[2]


def test_official_history_parser_temporal_and_revancha() -> None:
    main = (ROOT / "fixtures/progol/raw/Progol.csv").read_bytes()
    revancha = (ROOT / "fixtures/progol/raw/Progol-Revancha.csv").read_bytes()
    parsed = parse_history(main, PROGOL_CONFIG, revancha)
    assert len(parsed.accepted) == 1573 and not parsed.rejected
    assert (
        parsed.accepted[0].contest_number == "2348"
        and len(parsed.accepted[0].revancha_outcomes) == 7
    )
    assert parsed.accepted[-1].contest_number == "767"


def test_media_history_stats_and_strict_backtest() -> None:
    parsed = parse_history(
        (ROOT / "fixtures/progol_media_semana/raw/Progol-Media-Semana.csv").read_bytes(),
        MEDIA_SEMANA_CONFIG,
    )
    assert len(parsed.accepted) == 810 and parsed.accepted[-1].contest_number == "1"
    details = stats(list(parsed.accepted), MEDIA_SEMANA_CONFIG)
    assert "position_frequency" in details and "entropy" in details
    sample = list(reversed(parsed.accepted[-30:]))
    result = backtest(sample, MEDIA_SEMANA_CONFIG, 10, 2, 7, "random_uniform")
    assert result["contests_tested"] == 20 and result["simple_lines_generated"] == 40
    assert all(
        step["prediction_cutoff"]
        < step["source_data_cutoff"].replace("23:59:59.999999", "23:59:59.999999")
        or step["prediction_cutoff"] == step["source_data_cutoff"]
        for step in result["steps"]
    )
