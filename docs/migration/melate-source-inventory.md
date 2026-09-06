# MELATE CONTROL source inventory

Reference root: `/Users/rigobertorodriguezortega/Documents/Codex/2026-07-18/files-mentioned-by-the-user-act` (read-only).

| Path | Bytes | SHA-256 | Responsibility | Dependencies | Target | Classification |
|---|---:|---|---|---|---|---|
| `README.md` | 2496 | `d6ff89d27b6e5ad152125ac27ef9e32a9484242a2845f213d1299959d1af947f` | Scope and disclaimers | none | rules docs | reference only |
| `analysis.py` | 36295 | `2f5752fd4f72b44ce131111d38d4ffe4725d0bc909b28b302130dd0bc4fbb221` | parser, statistics, walk-forward | pandas/numpy | combination service/engine | adapt |
| `app.js` | 30772 | `27c880a411f101dc819a1348705c10424749c929c8421fa019cfb075523ddcca` | UI, nCr, expansion, generation | browser APIs | engine/frontend | reuse concept |
| `index.html` | 14987 | `e8043f9fbf602d197c731a6f60b55d4bef93eaeab0356991fc93eea0c629321e` | single-page UI | app.js | shared frontend | rewrite |
| `test_analysis.py` | 3626 | `8d0862f129aefd5283847fb563e6605e6f583b8560bd31310527fe9841ce7577` | analysis tests | pytest | golden tests | adapt |
| `tests.js` | 2644 | `f96007f14d479f922b46b12b2737ef6e11f5dd09a0c8afd4488ea061157aa360` | combinatorics tests | Node | engine tests | adapt |

Hardcoded source values include universe 1–56, six-number tickets and local editable costs/prizes. Only the structural rules independently confirmed by official documentation are adopted. Revancha/Revanchita remain related draw products, not Melate Retro. Retro validation uses official rules, official CSV, golden fixtures and invariants because no Retro source application exists.
