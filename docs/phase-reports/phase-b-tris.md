# Phase B — TRIS

## Scope delivered

- Five-digit domain preserving leading zeroes and seven source-confirmed modalities.
- CSV preview/import validation with row errors, duplicate detection and SHA-256 provenance.
- Global, positional and windowed frequencies; delays, intervals, transitions, position pairs and descriptive patterns.
- Seeded random, heuristic-ranked and coverage-oriented portfolios with versioned metadata.
- Strict walk-forward backtesting against an equal-size seeded random baseline.
- Seeded simulation, modality settlement and explicit unavailable economic results.
- Versioned `/api/v1/tris` endpoints, dedicated frontend route and Alembic migration.

## Evidence and boundaries

The source inventory and immutable snapshot hashes are recorded in `docs/migration/tris-source-inventory.md`. The source random generator is locked by `fixtures/tris/golden.json`. The copied sample is accompanied by provenance metadata.

Game mechanics and modality slices are treated as verified implementation behavior. Frequencies and patterns are descriptive only; heuristic scores are not probabilities. Prize multipliers, costs, packs, taxes and ROI remain unavailable until supplied by a verified economic rule version. LT, CA and PC remain explicitly `not_implemented` because the reference does not define them unambiguously.

## Quality gates

Backend: Black, Ruff, strict mypy, pytest and Alembic drift check. Frontend: ESLint, TypeScript, Vitest and production Vite build. The final execution results are reported in the Phase B handoff.
