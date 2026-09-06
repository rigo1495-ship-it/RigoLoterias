# Phase F — Progol y Progol Media Semana

1. **Final statuses.** Progol y Progol Media Semana están `available`; Protouch sigue `planned`.
2. **Official Progol rules.** 14 posiciones L/E/V, tiempo reglamentario; Revancha es complementaria de 7 posiciones.
3. **Official Media Semana rules.** 9 posiciones L/E/V, tiempo reglamentario.
4. **Rule versions.** `progol-mx-official-2026-09-06`.
5. **Source inventory.** Ver `docs/migration/progol-source-inventory.md`.
6. **Historical provenance.** CSV oficiales preservados en fixtures, recuperados 2026-09-06.
7. **Contest ranges/counts.** Progol 1,573; Revancha 928; Media Semana 810.
8. **Progol model.** Config de 14 partidos, orden semántico.
9. **Revancha model.** Subpool de 7, no game_slug principal.
10. **Media model.** Config independiente de 9.
11. **Outcome semantics.** Enum HOME=`L`, DRAW=`E`, AWAY=`V`; adapter explícito 1/0/3.
12. **Special handling.** Estados played, assigned, administrative, cancelled, substituted y pending están modelados; settlement conserva resultado oficial.
13. **Parser.** Valida concurso, fecha, longitud, L/E/V, duplicados y procedencia sin corrección silenciosa.
14. **Multiple expansion.** Producto de selecciones; pruebas 1…72 para Media Semana.
15. **Cost models.** Progol 15, Revancha 5, Media 15 por línea simple.
16. **Settlement.** Devuelve hits y acierto posicional; premio nulo sin resolución oficial de concurso.
17. **Contest prize resolution.** Separada del ticket: corrimientos/mayor nivel requieren fuente oficial del concurso.
18. **Statistics.** Frecuencia global/posicional, ventana, transiciones, patrones, entropía y Hamming.
19. **Prediction-data contracts.** ProbabilityVector exige normalización, fuentes, timestamps, corte, modelo y features.
20. **Implemented modes.** `random_uniform` y backtest descriptivo.
21. **Deferred modes.** market_only, elo, form y ensemble son `not_implemented`.
22. **Market/public percentages.** Momios oficiales se documentan como posible `public_selection_share`, nunca como market probability sin semántica verificable.
23. **Generation.** Restricciones por posición, presupuesto, semilla y límites de config.
24. **Coverage.** Líneas expandidas, únicas, duplicadas, Hamming y cobertura posición/par.
25. **Backtest.** Walk-forward con histórico estrictamente previo.
26. **Cutoff/no-lookahead.** Cada paso registra prediction/source cutoff; no consume resultado objetivo ni futuro.
27. **Random baseline.** `random_uniform`, mismo número de líneas por paso.
28. **Metrics.** Concursos, líneas, hits, media, máximo y distribución; ROI nulo.
29. **Isolation.** Históricos separados por slug/config; 14 y 9 jamás se mezclan.
30. **Source-vs-target.** Comparator sólo valida mapping/expansión; rechaza probabilidad y EV de fuente no verificable.
31. **API.** config, contests/latest/id, preview/import, stats, analysis, portfolios, settlement, backtests y simulations.
32. **Frontend.** Vistas deportivas de 14/9 filas L/E/V, simple/doble/triple y Revancha complementaria.
33. **Database migration.** Aditiva `20260906_05_progol`, validada empty→head y Phase E→head.
34. **Tests.** Dominio, parser, expansión, settlement, API, aislamiento y migración.
35. **Quality gates.** Backend pytest/Ruff/Black/mypy/Alembic; frontend ESLint/typecheck/Vitest/build.
36. **Existing regressions.** TRIS, Melate, Melate Retro, Chispazo y Gana Gato permanecen available y pasan su suite.
37. **Source hash verification.** Workbook y artefactos fuente conservan los hashes del inventario.
38. **Known limitations.** No equipos/quinielas actuales ni resoluciones de premio verificadas; no se inventan probabilidades ni ROI.
39. **Phase G preconditions.** Requiere autorización expresa y reglas/fuentes propias de Protouch.
40. **git status --short.** Sólo cambios Phase F antes de commit; limpio después de commits.
