import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import date, time

from app.games.tris.domain import TrisDrawResult


@dataclass(frozen=True)
class ImportPreview:
    source_hash: str
    rows_total: int
    accepted: tuple[TrisDrawResult, ...]
    rejected: tuple[dict[str, object], ...]
    duplicates: tuple[str, ...]


class TrisHistoricalImporter:
    def parse(self, source: object) -> ImportPreview:
        if not isinstance(source, (str, bytes)):
            raise TypeError("TRIS importer accepts CSV text or bytes.")
        raw = source.encode() if isinstance(source, str) else source
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
        accepted: list[TrisDrawResult] = []
        rejected: list[dict[str, object]] = []
        seen: set[str] = set()
        duplicates: list[str] = []
        for line, row in enumerate(rows, 2):
            try:
                draw_number = str(row.get("draw_id") or row.get("CONCURSO") or "").strip()
                if not draw_number:
                    raise ValueError("Missing draw number.")
                number = row.get("winning_number")
                if number is None:
                    number = "".join(str(row.get(f"R{i}", "")).strip() for i in range(1, 6))
                draw = TrisDrawResult(
                    draw_number=draw_number,
                    draw_date=date.fromisoformat(str(row.get("draw_date") or row.get("FECHA"))),
                    draw_time=(
                        time.fromisoformat(row["draw_time"]) if row.get("draw_time") else None
                    ),
                    draw_name=str(row.get("draw_name") or "Sin horario"),
                    winning_number=str(number).strip(),
                    source=str(row.get("source") or "csv"),
                    verified=str(row.get("verified", "")).lower() in {"1", "true", "si", "sí"},
                )
                if draw_number in seen:
                    duplicates.append(draw_number)
                else:
                    accepted.append(draw)
                    seen.add(draw_number)
            except (TypeError, ValueError) as exc:
                rejected.append({"line": line, "message": str(exc), "raw": row})
        return ImportPreview(
            hashlib.sha256(raw).hexdigest(),
            len(rows),
            tuple(accepted),
            tuple(rejected),
            tuple(duplicates),
        )
