# TRIS source inventory

Reference root (read-only): `/Users/rigobertorodriguezortega/Documents/Codex/2026-07-12/presentations-plugin-presentations-openai-primary-runtime-2`.

| Source path | Bytes | SHA-256 | Purpose | Target | Migration |
|---|---:|---|---|---|---|
| `config/game_rules.yaml` | 3791 | `82c57a7cd13558f4d905be5e61ff3b8219818c31c6521952ad2ea7c8bf64dfb0` | User-supplied rules | `games/tris/rules.py` | Reference; economic rules unresolved |
| `backend/tris_master/models.py` | 3661 | `52b73a7c044e2618d9063554941ff3062bb756eb55169d047a52ea1ac19c542a` | Draw/bet value objects | `games/tris/domain.py` | Adapt |
| `backend/tris_master/importer.py` | 3654 | `b4e870b60602912856e80e753cde14acced33ea2c334aa72c396ebb0d6af03d6` | CSV parser | `games/tris/importer.py` | Adapt |
| `backend/tris_master/statistics.py` | 6349 | `261c0a9da1ebcecf333fbb75cffc4923597adaca37ff38395f29cfe77315a540` | Descriptive statistics/backtest | `engines/positional/engine.py` | Adapt/extend |
| `backend/tris_master/generators/strategies.py` | 12969 | `b4dd759da016c6c6c6dbabf18ade2a66b7e5de472f190299fea12e9db93bf82e` | Seeded generators | `games/tris/generator.py` | Adapt |
| `backend/tris_master/settlement.py` | 9704 | `e0eea0b035dc643013df1c8cf13e5926d10439a02b210f7b375ec1e0b86dc530` | Match and payout behavior | `games/tris/settlement.py` | Adapt matching only |
| `backend/tris_master/simulation.py` | 3404 | `e2efe9d114b6afafe94e7e6aec994e6b1bda80893f0ddb0817ad381cf3e02673` | Seeded simulation | `games/tris/backtest.py` | Rewrite |
| `backend/tris_master/api.py` | 30810 | `c053e176f00d60093a06510c3f37cc6e8539905c65087b2a0bde2dc4d3549a2e` | HTTP handlers | `api/v1/tris.py` | Reference only |
| `frontend/src/app/page.tsx` | 33390 | `cffaf17691127e6bacd7e7cb8d4935a804a07af8545e9860aceb2e906c1f3b23` | TRIS UI | `frontend/src/games/tris` | Rewrite |
| `data/sample_draws.csv` | 136 | `333988d8ec6f5562034971bfc7f16bb59c5f4b9fe69e0970f7f920d2646730ac` | Small sample fixture | `fixtures/tris` | Authorized fixture copy |
| `data/sample_bets.csv` | 201 | `1c2e3bc2493d37ded6fb890e0fdda9e752fbfce281863192a76c3337714bcfed` | Small bet fixture | Golden tests | Reference |

## Rule classification

- **Game rules:** five ordered digits, each `0..9`; leading zeroes are significant; modality matching slices are verified as source behavior.
- **Descriptive statistics:** frequencies and observed patterns; never probabilities.
- **Heuristic strategy:** frequency ranking and coverage generation; never probability.
- **Mathematical probability:** uniform outcome-space values such as `1/10^digits` only.
- **Implementation behavior:** schedule names, packs and source-provided economic values.

The source itself says its economic rules were provided by the user and require official validation. Consequently Phase B does not install prize multipliers, taxes or packs as verified rules. Settlement reports matches and returns monetary fields as `null` without an explicitly supplied verified prize rule.

Ley del Tercio and the signals LT, CA and PC have no unambiguous source definition and remain not implemented.

