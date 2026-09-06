# Phase D — Chispazo completion report

1. Final status: Chispazo, TRIS, Melate and Retro are `available`.
2. Rules: official product page and regulation, version `chispazo-2012-03-07`.
3. Provenance: official CSV SHA-256 `4d9e15816a9614e2d96fd0d41885a08a4ea1256660e22c6a6066e47fad2f1a06`.
4. History: 12,234 accepted, 0 rejected; draw 1 (1999-01-05) to 12234 (2026-09-05).
5. Sessions: official 15:00/21:00 schedule; CSV lacks labels, so same-day order uses numeric draw number without inferring variants.
6. Config/parser: 1–28, five naturals, zero additional, sizes 5/6/7; strict validation and provenance.
7. Statistics/signals: shared descriptive engine; FR/CO/RE/PA/PR descriptive; LT/CA/PC deferred.
8. Generation/expansion: canonical filters and seeded strategies; `C(5,5)=1`, `C(6,5)=6`, `C(7,5)=21`.
9. Cost/settlement: MXN 10 per simple; structural 5/4/3/2 categories; fixed two-hit MXN 10, variable amounts null.
10. Coverage: unique numbers, overlap, pair and triple coverage use universe 28.
11. Backtest: strict walk-forward, equal random baseline, recorded cutoff, null ROI. Same-day test proves 12233 precedes 12234.
12. Isolation/API/frontend: identity scopes data and runs; shared versioned API and combination page expose all canonical operations and states.
13. Migration: no new revision required because additive `20260906_03` already supports zero additional values and compound identity. Empty/previous-head upgrades and drift checks pass.
14. Tests/gates: 48 backend and 7 frontend tests pass. Ruff, Black, strict mypy, Alembic, ESLint, TypeScript and the production Vite build pass; all prior-game regressions are included.
15. Safety: official raw SHA-256 `4d9e15816a9614e2d96fd0d41885a08a4ea1256660e22c6a6066e47fad2f1a06`; golden SHA-256 `32874aa7e4e37a7405c3a500c6a88fc51cb8ac6822785eee03f155706e1b21c4`. No source project was modified.
16. Limitations: CSV has no session labels; variable prizes/ROI unavailable; LT/CA/PC not implemented.
17. Phase E requires separate authorization and verified Gana Gato sources. No Phase E work occurred.
18. `git status --short`: clean after Phase D commits.
