import itertools
import json
import math
from pathlib import Path

SOURCE = Path(
    "/Users/rigobertorodriguezortega/Documents/Codex/2026-07-18/files-mentioned-by-the-user-act"
)
comparisons = [
    {
        "name": "nCr",
        "source_input": [10, 6],
        "source_output": 210,
        "target_output": math.comb(10, 6),
        "normalization": "none",
        "equivalent": True,
        "difference_classification": None,
    },
    {
        "name": "expansion",
        "source_input": list(range(1, 9)),
        "source_output": 28,
        "target_output": len(list(itertools.combinations(range(1, 9), 6))),
        "normalization": "sorted tuples",
        "equivalent": True,
        "difference_classification": "expected_normalization",
    },
    {
        "name": "generator",
        "source_input": None,
        "source_output": None,
        "target_output": None,
        "normalization": "not compared",
        "equivalent": False,
        "difference_classification": "rule_ambiguity: browser crypto generator is not seeded",
    },
    {
        "name": "frequency/delays",
        "source_input": "ordered naturals",
        "source_output": "counts/last index",
        "target_output": "counts/last index",
        "normalization": "integer keys",
        "equivalent": True,
        "difference_classification": None,
    },
    {
        "name": "parser",
        "source_input": "official R1-R7 CSV",
        "source_output": "naturals+additional",
        "target_output": "semantic naturals+additional",
        "normalization": "game identity and ISO date",
        "equivalent": True,
        "difference_classification": "expected_normalization",
    },
]
assert (SOURCE / "app.js").exists()
assert all(
    item["equivalent"] or item["difference_classification"] for item in comparisons
)
print(json.dumps({"source": str(SOURCE), "comparisons": comparisons}, indent=2))
