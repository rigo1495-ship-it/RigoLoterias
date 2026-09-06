# Protouch

Rule version: `protouch-reglamento-2012-03-07`; implementation reviewed 2026-09-06.

The official game has 13 ordered NFL/NCAA football matches. `L` means local wins by more than six points, `D` means the final difference is at most six points for either team, and `V` means visitor wins by more than six. `D` is never a soccer draw. The Protouch score is the official regulation score: overtime/extra quarters are excluded where the regulation requires it.

Protouch Inicial is separate and simple-only: local Q1–Q4, visitor Q1–Q4, or no touchdown (nine outcomes). The published historical CSV does not contain an Initial column, so historical Initial results are intentionally not inferred.

Multiple rules: up to eight doubles alone, five triples alone, or a mixed maximum of two doubles and four triples. A simple line costs MXN 10; 2D+4T expands to 324 lines and MXN 3,240. The 13/12/11-hit prize levels are stored separately from ticket settlement because final prize allocation depends on official contest resolution.

Suspended, unknown, postponed or replaced matches retain an explicit resolution type. `sport_final_score`, `official_regulation_score`, and `official_pool_result` are distinct provenance-bearing concepts.

Primary sources: [Protouch](https://loterianacional.gob.mx/Protouch/Protouch), [Quinielas múltiples](https://loterianacional.gob.mx/Protouch/CombinacionesMultiples), [Reglamento](https://www.loterianacional.gob.mx/Documentos/Legal/ReglamentoJuegos/Reglamento-Protouch.pdf), [datos abiertos](https://comercializadores.loterianacional.gob.mx/DatosAbiertos/NumerosGanadores).
