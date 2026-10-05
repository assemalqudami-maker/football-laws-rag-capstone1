"""Resolve the 30 golden questions to concrete chunk IDs.

The human-authored golden file contains expected source IDs and short evidence
phrases from the official IFAB source. This script runs after chunking and maps
those anchors to one or more exact chunk IDs. It fails if any question cannot
be grounded in the built corpus.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
GOLDEN = ROOT / "data" / "eval" / "golden_questions.json"
OUT = ROOT / "data" / "eval" / "golden_questions_labeled.json"


def norm(text: str) -> str:
    return " ".join(text.casefold().replace("’", "'").split())


def main() -> None:
    chunks = [
        json.loads(line)
        for line in CHUNKS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    questions = json.loads(GOLDEN.read_text(encoding="utf-8"))

    if len(questions) != 30:
        raise SystemExit(f"Expected 30 golden questions, found {len(questions)}.")

    failures = []
    labelled = []

    for item in questions:
        expected_sources = set(item["expected_source_ids"])
        phrases = [norm(p) for p in item["gold_phrases"]]

        matches = []
        for chunk in chunks:
            if chunk["source_id"] not in expected_sources:
                continue
            content = norm(chunk["content"])
            if any(phrase in content for phrase in phrases):
                matches.append(chunk["chunk_id"])

        record = dict(item)
        record["gold_chunk_ids"] = sorted(set(matches))
        labelled.append(record)

        if not record["gold_chunk_ids"]:
            failures.append(
                {
                    "id": item["id"],
                    "question": item["question"],
                    "expected_source_ids": item["expected_source_ids"],
                    "gold_phrases": item["gold_phrases"],
                }
            )
            print(f"[MISS] {item['id']}: no gold chunk resolved")
        else:
            print(
                f"[OK] {item['id']}: "
                f"{len(record['gold_chunk_ids'])} gold chunk(s)"
            )

    OUT.write_text(json.dumps(labelled, indent=2), encoding="utf-8")

    if failures:
        print("\nUnresolved golden questions:")
        print(json.dumps(failures, indent=2))
        raise SystemExit(1)

    print(f"\nResolved all {len(labelled)} golden questions.")


if __name__ == "__main__":
    main()
