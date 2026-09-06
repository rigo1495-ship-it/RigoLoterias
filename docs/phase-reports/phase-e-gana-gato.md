# Phase E — Gana Gato

## 1. Final status
Gana Gato está `available`; TRIS, Melate, Melate Retro y Chispazo permanecen `available`. Phase F/Progol no fue iniciada.

## 2. Official rules
La página y el reglamento oficiales confirman ocho selecciones 1–5, centro comodín, tablero 3×3, ocho líneas, categorías por líneas y apuesta vigente de MXN 10.

## 3. Rule version
`gana-gato-mx-2012-03-07`; costo separado como `gana-gato-cost-2026-09-06`.

## 4. Source inventory
Documentado en `docs/migration/gana-gato-source-inventory.md`, incluida la clasificación reuse/adapt/rewrite/reference/reject.

## 5. GatoSolver HEAD
Fuente read-only en `/Users/rigobertorodriguezortega/Documents/Codex/2026-07-11/gatosolver-data-ganagato-csv-src-parser/GatoSolver`, rama `main`, HEAD `4a5127ce28d3a6ab9c66abe8ae3310befdc17dbe`. Su working tree ya estaba sucio y no se modificó.

## 6. Historical provenance
`https://www.loterianacional.gob.mx/Documentos/Historicos/GanaGato.csv`, recuperado 2026-09-06, parser `gana-gato-csv-1`, SHA-256 `d8519f2b59d65db7017321dcbfab8f08306e078517230669c8b9008bdb9b8e15`.

## 7. Record count
3,058 aceptados; 0 rechazados; 0 concursos duplicados en el raw oficial.

## 8. Earliest/latest draw
Concurso 1, 2006-11-04; concurso 3058, 2026-09-05.

## 9. Board model
`GanaGatoBoard`, `GanaGatoDrawResult`, `GanaGatoTicket`, `BoardPosition`, `WinningLine`, `LineEvaluation` preservan las ocho posiciones; CENTER no forma parte del payload.

## 10. Canonical lines
Una tabla única define 3 horizontales, 3 verticales y 2 diagonales. CENTER satisface automáticamente las cuatro líneas que lo cruzan.

## 11. Parser
Valida concurso, fecha `%d/%m/%Y`, ocho F1…F8, rango 1–5, incompletos y duplicados sin ordenar ni deduplicar valores válidos.

## 12. Line evaluator
Evalúa igualdad por posición y produce exclusivamente 0…8 líneas. Los fixtures matemáticos y casos source-vs-target cubren extremos y centro.

## 13. Prize categories
7/8→1, 6→2, 5→3, 4→4, 3→5, 2→6, 1→7, 0→nula. Montos no inferidos.

## 14. Cost rules
MXN 10 está versionado en el adapter de settlement, no en BoardPatternEngine. `prize_amount` y ROI son nulos.

## 15. Statistics
Frecuencia global y posicional, ventana reciente, atrasos, intervalos, repetición anterior, matches, distribución/frecuencia de líneas, patrones, Hamming consecutivo y coocurrencia posicional.

## 16. Generation
Estrategias `random`, `heuristic_ranked` y `coverage_optimized`, con semilla, restricciones requeridas/excluidas por posición y Hamming mínimo; búsqueda acotada y reproducible.

## 17. Hamming/diversity
Distancia 0…8 sin CENTER; media/mínimo/máximo, únicos, duplicados y cobertura posición-valor.

## 18. Coverage
La optimización greedy maximiza separación dentro de su pool. Se informa cobertura posición-valor y patrones de línea uniforme sin afirmar ventaja predictiva.

## 19. 390625-board validation
Constante formal `5**8 == 390625`, iterator perezoso y prueba de cardinalidad/contrato.

## 20. Exhaustive-analysis methodology
`scripts/gana_gato_exhaustive.py` evalúa offline el universo por lotes lógicos contra splits explícitos y reporta `historical_line_distribution`; no corre por request.

## 21. Overfitting protection
El script exige cortes train/validation/test. No selecciona con todo el histórico para luego presentar ese mismo período como evaluación.

## 22. Backtest
Walk-forward registra target, cutoff, history size, estrategia, parámetros, seed, portfolio, líneas y categorías; baseline usa la misma cantidad de tickets.

## 23. Anti-lookahead
Historia estrictamente anterior. Tests verifican target mutado, futuros mutados/eliminados, cutoff, semilla y tamaño de portfolio.

## 24. Source-vs-target
Comparador determinista confirma equivalencia de parsing posicional conceptual, líneas, categoría y Hamming. Diferencias económicas del fuente se rechazan por falta de autoridad oficial.

## 25. API
Expone config, draws/latest, preview/import, statistics, analysis, portfolios, backtests/get, simulations y board/evaluate. Validaciones esperables responden 404/422.

## 26. Frontend
Página dedicada con geometría 3×3, ocho selectores, centro no editable, estados, secciones de historia/estadística/patrones/generación/cobertura/backtest y aviso no predictivo.

## 27. Cross-game isolation
Persistencia, router y motor son especializados; Gana Gato no usa CombinationEngine. La suite completa conserva contratos de los cuatro juegos disponibles previos.

## 28. Migration
`20260906_04_gana_gato` es aditiva. Verificados empty→head, Phase B→head, Phase D (`20260906_03`)→head y `alembic check` sin deriva.

## 29. Tests
Backend: 59 passed. Frontend: 6 passed. Incluyen dominio, parser/golden, settlement, generación, anti-lookahead, API, aislamiento y migraciones.

## 30. Quality gates
Ruff, Black check, mypy y Alembic check pasan. ESLint, TypeScript, Vitest y Vite build pasan. Comparator pasa.

## 31. Existing-game regression
TRIS, Melate, Melate Retro y Chispazo continúan disponibles y sus tests de imports, estadísticas, generación, backtests, simulación y settlement no presentan regresiones.

## 32. Source hash verification
Hashes HEAD relevantes antes/después: CSV `88c377cb…8bcb`; rules `a6a9d28b…a2a98`; parser `098f69c0…3738f`; evaluator `638fb274…bfcd`; generator `d8340d8c…15e3`; optimizer `96b18e5f…06e4`; statistics `a6c7431f…2448c`; backtest `0350ca3e…c712`. HEAD, rama y estado fuente permanecen sin cambios adicionales.

## 33. Known limitations
No hay importes de premios históricos por ganador verificados; por ello no se calcula ROI. Heurísticas y análisis exhaustivo son retrospectivos y descriptivos.

## 34. Phase F preconditions
Phase F requiere autorización expresa y su propio gate de reglas/datos para Progol. Ningún código de Progol fue activado.

## 35. git status --short
Antes de Phase E: limpio. Al cierre técnico previo al commit: únicamente archivos de Phase E. Tras los commits de cierre: limpio.
