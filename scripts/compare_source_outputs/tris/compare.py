"""Optional source-to-target comparison; TRIS MASTER is never imported at runtime."""

import argparse
import json
import random
from pathlib import Path


def selections(seed: int, count: int) -> list[str]:
    return random.Random(seed).sample(
        [str(value).zfill(5) for value in range(100000)], count
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--golden", type=Path, default=Path("fixtures/tris/golden.json")
    )
    args = parser.parse_args()
    golden = json.loads(args.golden.read_text())
    actual = selections(golden["seed"], golden["count"])
    if actual != golden["expected"]:
        raise SystemExit(f"Mismatch: {actual!r}")
    print("TRIS source algorithm and target golden output match.")


if __name__ == "__main__":
    main()
