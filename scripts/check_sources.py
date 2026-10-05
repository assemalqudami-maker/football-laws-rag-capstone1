"""Check manifest quality and optionally test official source URLs."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sources_manifest.csv"


def main() -> None:
    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    errors = []
    ids = [r["source_id"].strip() for r in rows]
    urls = [r["url"].strip() for r in rows]

    for value, count in Counter(ids).items():
        if count > 1:
            errors.append(f"duplicate source_id: {value}")

    for value, count in Counter(urls).items():
        if count > 1:
            errors.append(f"duplicate URL: {value}")

    for i, row in enumerate(rows, start=2):
        if row["language"].strip() != "English":
            errors.append(f"line {i}: non-English source")
        host = urlparse(row["url"]).hostname or ""
        if not host.endswith("theifab.com"):
            errors.append(f"line {i}: non-IFAB host {host}")
        if row["format"].strip().upper() not in {"HTML", "PDF"}:
            errors.append(f"line {i}: unsupported format {row['format']}")

    print(f"Manifest rows: {len(rows)}")
    print(f"Unique source IDs: {len(set(ids))}")
    print(f"Unique URLs: {len(set(urls))}")

    if not (20 <= len(rows) <= 50):
        errors.append("source count must be between 20 and 50")

    if errors:
        print("\nFAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("\nPASS: manifest satisfies the initial source-policy checks.")


if __name__ == "__main__":
    main()
