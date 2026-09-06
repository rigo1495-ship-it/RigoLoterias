# Inventario fuente Gana Gato

- Fuente read-only: `/Users/rigobertorodriguezortega/Documents/Codex/2026-07-11/gatosolver-data-ganagato-csv-src-parser/GatoSolver`
- Rama/HEAD: `main` / `4a5127ce28d3a6ab9c66abe8ae3310befdc17dbe`
- Estado: previamente sucio, con archivos modificados, eliminados y no rastreados; no fue reparado ni alterado.
- Los archivos relevantes pertenecientes realmente a HEAD se inspeccionaron con `git show HEAD:path`: `src/rules.py`, `src/parser.py`, `src/evaluator.py`, `src/generator.py`, `src/optimizer.py`, `src/statistics_engine.py`, `src/backtest.py`, `src/validation.py`, documentación, CSV y tests.

Clasificación: reglas exactas y evaluación de líneas — adaptar; parser — reescribir para el CSV oficial; generación/diversidad/cobertura — reutilizar concepto; optimizador/estadísticas/backtest — adaptar con anti-lookahead; datos y UI — referencia; tabla de premios/ROI fuente — rechazar sin verificación oficial. Los SHA-256 previos están registrados en el reporte de fase; la integración no depende de GatoSolver en runtime.

La nomenclatura fuente F1…F8 se adapta posicionalmente a A1,A2,A3,B1,B3,C1,C2,C3. Sus líneas `(0,1,2),(3,4),(5,6,7),(0,3,5),(1,6),(2,4,7),(0,7),(2,5)` son equivalentes al centro omitido por ser comodín.
