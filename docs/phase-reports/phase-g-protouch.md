# Phase G — Protouch

## Final status

`available`. Protouch completes the eight-game platform core scope.

## Rules, history and domain

Official rule version is `protouch-reglamento-2012-03-07`. The domain has 13 ordered matches, L/D/V football semantics, ±6 boundary tests, separate regulation/overtime provenance, a nine-outcome Protouch Inicial model, official multiple rules, derived MXN 10 cost, main/Initial settlement separation, and explicit special-resolution types. Prize amount resolution remains official-contest data only.

Official raw history is `fixtures/protouch/raw/Protouch.csv`, retrieved 2026-09-06, SHA-256 `f64f8bf5d04447a4aa6d2423224056d34979d92ca5eb943346f46b0fa401cf4e`, parser `protouch-official-csv-1`. It contains 796 data rows from contest 89 (1988-09-04) through 885 (2026-08-29), columns `NPRODUCTO, CONCURSO, R1..R13, BOLSA, FECHA`. The strict parser accepted 784 and rejected 12 legacy rows containing `E`, preserving the raw source and refusing to reinterpret an undocumented fourth outcome. No Initial column exists, so no Initial mapping is invented.

## Implementation

The dedicated `ProtouchEngine` provides validation, official outcome mapping, expansion, costs, settlement, probability contracts, random/coverage generation and descriptive walk-forward backtest. Statistics are explicitly descriptive. Football predictions, market-to-Protouch conversion, Elo, team-strength, ensemble, reproducible Monte Carlo and predictive football backtest are `not_implemented` until real provenance-bearing data exists.

API exposes config, contests, imports/preview, statistics, analysis, portfolios, backtests and evaluation; missing resources return 404 and invalid payloads 422. The specific frontend renders 13 L/D/V rows, Initial, live multiple expansion/cost and does not render fictitious probability bars. Cross-game isolation uses `ProtouchOutcome`, never Progol HOME/DRAW/AWAY semantics.

## Source audit and comparison

See [source inventory](../migration/protouch-source-inventory.md) and `scripts/compare_source_outputs/protouch/compare.py`. Only deterministic mapping/expansion/settlement concepts are adapted. Unsupported source probability, optimization and Monte Carlo logic is rejected. Source hashes are recorded there; no source file/database was modified.

## Migration, quality and limitations

Migration `20260906_06` is additive (`protouch_contest_results`) and supports baseline-to-head and Phase-F-to-head upgrades. Tests cover match structure, ±6, Initial validation, limits, 324 expansion, cost, settlement, parser and registry. Existing available games remain available: TRIS, Melate, Melate Retro, Chispazo, Gana Gato, Progol and Progol Media Semana.

Known limitation: official raw history lacks current card teams, kickoff, designated Initial match and Initial result; the UI/API deliberately do not fabricate them. Historical portfolio backtest is random/descriptive and has no ROI without official contest payout data.

## Scope and git status

PLATFORM CORE SCOPE COMPLETE — 8 GAMES. No additional game is in scope. Final `git status --short`: clean.
