# Phase C — Melate + Melate Retro completion report

## 1. Final statuses
Melate and Melate Retro are `available`; TRIS remains `available`. Chispazo remains `planned`.

## 2. Official rule sources
Melate uses the Lotería Nacional product page and 2025-02-19 regulation. Retro uses its official product page and regulation last reformed 2012-03-07. Details are in `docs/game-rules/`.

## 3–6. Historical provenance and records
Official CSV URLs are documented in the rule files. Melate SHA-256 `91926689f94cef1ae9088a3578b3026d7fb6e4a13be837ac7a164cb964fc53d8`: 4,261 accepted, 0 rejected, draws 1 (1984-08-19) through 4261 (2026-09-04). Retro SHA-256 `04f37e60e76023a96e60406bc3fba8eb5bbd5c3ce15b4d874e14cc0fc1e6f952`: 1,666 accepted, 0 rejected, draws 1 (2010-06-01) through 1666 (2026-09-05). No missing range is present in either draw-number sequence.

## 7. CombinationEngine
The generic engine contains no game slug branches. Configuration supplies universe, natural/additional counts, ticket sizes and ordering.

## 8. GenerationRequest filters
Bounded reproducible generation supports ticket count/size, required/excluded numbers, sum, parity, primes, consecutive and previous-draw-repeat bounds, strategy and seed. Impossible constraints fail before or within a finite bounded search.

## 9. Coverage metrics
`unique_numbers_covered` is union cardinality; overlap metrics are pairwise intersection mean/maximum; pair/triple coverage is observed unique subsets divided by all universe pairs/triples. These do not claim improved prize probability.

## 10–12. Backtesting and anti-lookahead
Walk-forward steps use only the strict prefix before each target and record target, cutoff, history count, parameters, seed, tickets and hits. A random baseline receives the same game, targets, ticket size and ticket count. Tests mutate targets/future draws and verify reproducibility and strict cutoff.

## 13. Melate source-vs-target
The comparator records inputs, outputs, normalization, equivalence and divergence class for parser, frequency/delay, nCr and expansion. Browser crypto generation is correctly classified non-reproducible rather than given a fabricated golden.

## 14. Retro temporal golden evidence
Golden records cover recent draw 1666, middle draw 834 and earliest draw 1. They validate raw official CSV to semantic natural/additional records. Golden SHA-256: `53e4580a176021a146b89163b5dec97ab998e09435b0f12eb29c302b219926ee`.

## 15. Cross-game isolation
Persistence uniqueness is `(game_slug, draw_number)`; queries, run keys, statistics and backtests include game identity. Tests cover equal draw IDs and reject mixed histories. TRIS uses its independent table and engine.

## 16–17. API and frontend
Versioned endpoints expose config, draws/latest, preview/import, statistics, analysis, portfolios with coverage, backtests/get and simulations for each slug. Expected domain errors return 422/404. Shared pages implement loading, empty data, error, success, generation and explicit `not_implemented`; config limits are exposed by the backend.

## 18. Database migrations
Additive revision `20260906_03` creates combination history and compound uniqueness/indexes. Tests cover empty-to-head and Phase-B-head-to-head; Alembic reports no drift.

## 19–21. Tests, quality gates and TRIS regression
Backend: 44 tests passed; Ruff, Black, strict mypy and Alembic check passed. Frontend: 8 Vitest tests passed; ESLint, TypeScript and the production Vite build passed. Golden, comparator, generation, coverage, migration, API, isolation and anti-lookahead tests are included. Existing TRIS tests remain part of the full suite and pass.

## 22. Hash verification
MELATE CONTROL before/after hashes match: README `d6ff89d2…`, analysis.py `2f5752fd…`, app.js `27c880a4…`, index.html `e8043f9f…`, test_analysis.py `8d0862f1…`, tests.js `f96007f1…`. `source_modified=false`.

## 23. Known limitations
LT, CA and PC remain `not_implemented`. Heuristics are not probabilities. Prize/cost/tax rules are not installed; ROI and return per peso remain null.

## 24. Phase D preconditions
Phase D requires separate authorization, verified Chispazo rules and source inventory. No Phase D work occurred here.

## 25. git status --short
The closing report records a clean working tree after the Phase C commits.
