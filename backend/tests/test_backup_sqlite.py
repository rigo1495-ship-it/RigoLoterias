import sqlite3
import subprocess
import sys
from pathlib import Path


def test_sqlite_backup_is_queryable_and_integrity_checked(tmp_path: Path) -> None:
    source = tmp_path / "source.sqlite3"
    destination = tmp_path / "backups" / "snapshot.sqlite3"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE marker (value TEXT)")
        connection.execute("INSERT INTO marker VALUES ('preserved')")
    script = Path(__file__).parents[2] / "scripts" / "backup_sqlite.py"
    subprocess.run([sys.executable, str(script), str(source), str(destination)], check=True)
    with sqlite3.connect(destination) as connection:
        assert connection.execute("SELECT value FROM marker").fetchone() == ("preserved",)
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
