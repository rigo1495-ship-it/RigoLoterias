from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_baseline_migration_creates_canonical_schema(tmp_path: Path) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    database_path = tmp_path / "canonical.sqlite3"
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")

    command.upgrade(config, "head")

    tables = set(inspect(create_engine(f"sqlite:///{database_path}")).get_table_names())
    assert "alembic_version" in tables
    assert {"games", "draws", "backtest_runs", "audit_events"} <= tables
    assert "combination_draw_results" in tables


def test_upgrade_from_phase_b_head(tmp_path: Path) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    database_path = tmp_path / "phase_b.sqlite3"
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    command.upgrade(config, "20260906_02")
    command.upgrade(config, "head")
    inspector = inspect(create_engine(f"sqlite:///{database_path}"))
    assert "combination_draw_results" in inspector.get_table_names()
    indexes = {
        item["name"] for item in inspector.get_indexes("combination_draw_results")
    }
    assert "uq_combination_game_draw" in indexes
