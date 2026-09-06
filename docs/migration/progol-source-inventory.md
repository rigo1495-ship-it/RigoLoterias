# Inventario PROGOL RIGO ELITE

Fuente read-only: `/Users/rigobertorodriguezortega/Documents/Codex/2026-06-21/act-a-como-un-equipo-formado/outputs/PROGOL_RIGO_ELITE`.

- Workbook: `PROGOL_RIGO_ELITE_GOOGLE_SHEETS.xlsx`, 49,746 bytes, SHA-256 `a61d7438b445fec87b346f58e3abbbfe5c3b9dd1894e146fffa2c95bdb9e2f34`.
- Inspección workbook: 1,083,156 bytes, SHA-256 `88f81dc3673b09a91e96eb1e41442a074c5c8042defed61463eefb7973bd7c06`.
- Demo matches: SHA-256 `d7280e2855447daf4f05e3e4170f189f9e4b9eec2efc53de61d00c33b4fc9891`.

Auditado: `engine/rules.py` (L/E/V y ranking) y `optimization/budget.py` (producto de selecciones) se adaptan sólo para semántica determinista. Workbooks, demo matches, probabilidades/momios, modelo heuristic_market_elo, EV y simulaciones son `reference_only` o `reject`: sus fuentes y cortes temporales no son verificables. No hay dependencia runtime ni cambios en la fuente.
