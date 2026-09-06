# Melate rules

- Rule version: `melate-2025-02-19`.
- Retrieved: 2026-09-06.
- Official sources: https://www.loterianacional.gob.mx/Melate/Melate and https://www.loterianacional.gob.mx/Documentos/Legal/ReglamentoJuegos/DOF19022025ReglamentoMelateRR.pdf
- `official_game_rule`: choose 6–10 distinct numbers from 1–56; a draw has six natural numbers and one distinct additional number. A multiple selection expands to every six-number subset. Revancha and Revanchita reuse a Melate selection but are separate draws; they are not separate canonical GameModules in Phase C.
- `mathematical_definition`: a simple first-prize outcome has probability `1/C(56,6)`; a k-number multiple expands to `C(k,6)` simple tickets.
- `descriptive_statistic`: frequency, delay, intervals, patterns and cooccurrence describe history only.
- `heuristic`: rankings and coverage optimization are not probabilities.
- `source_implementation_behavior`: MELATE CONTROL parsing, combinatorics and walk-forward behavior are comparison references, not official rules.

Costs, prizes, tax and ROI remain unavailable because Phase C does not install a verified PrizeRuleVersion.
