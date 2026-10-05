"""Audit the freshly collected corpus before ingestion."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ROOT / "data" / "processed" / "documents.jsonl"
OUT_JSON = ROOT / "data" / "eval" / "corpus_audit.json"
OUT_MD = ROOT / "data" / "eval" / "corpus_audit.md"


def canonical(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", " ", text).strip()


def digest(text: str) -> str:
    return hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()


def main() -> None:
    docs = [
        json.loads(line)
        for line in DOCUMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not docs:
        raise SystemExit("No processed documents found.")

    rows = []
    by_hash: dict[str, list[str]] = {}

    for doc in docs:
        text = "\n".join(block["text"] for block in doc["blocks"])
        h = digest(text)
        by_hash.setdefault(h, []).append(doc["source_id"])
        rows.append(
            {
                "source_id": doc["source_id"],
                "title": doc["title"],
                "language": doc["language"],
                "format": doc["format"],
                "characters": len(text),
                "words": len(text.split()),
                "blocks": len(doc["blocks"]),
                "sha256_normalized_text": h,
            }
        )

    duplicate_groups = [ids for ids in by_hash.values() if len(ids) > 1]
    too_small = [r["source_id"] for r in rows if r["words"] < 100]

    audit = {
        "document_count": len(rows),
        "language_counts": {},
        "format_counts": {},
        "total_characters": sum(r["characters"] for r in rows),
        "total_words": sum(r["words"] for r in rows),
        "exact_duplicate_groups": duplicate_groups,
        "documents_under_100_words": too_small,
        "documents": rows,
    }

    for row in rows:
        audit["language_counts"][row["language"]] = (
            audit["language_counts"].get(row["language"], 0) + 1
        )
        audit["format_counts"][row["format"]] = (
            audit["format_counts"].get(row["format"], 0) + 1
        )

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    lines = [
        "# Corpus Audit",
        "",
        f"- Documents: **{audit['document_count']}**",
        f"- Total words: **{audit['total_words']:,}**",
        f"- Total characters: **{audit['total_characters']:,}**",
        f"- Languages: **{audit['language_counts']}**",
        f"- Formats: **{audit['format_counts']}**",
        f"- Exact duplicate groups: **{len(duplicate_groups)}**",
        f"- Documents under 100 words: **{len(too_small)}**",
        "",
        "## Per-source statistics",
        "",
        "| Source ID | Words | Blocks | Format |",
        "|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['source_id']} | {row['words']:,} | {row['blocks']} | {row['format']} |"
        )

    if duplicate_groups:
        lines += ["", "## Exact duplicate groups", ""]
        for group in duplicate_groups:
            lines.append("- " + ", ".join(group))

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({k: v for k, v in audit.items() if k != "documents"}, indent=2))

    if not (20 <= len(rows) <= 50):
        raise SystemExit("Corpus document count is outside the required 20–50 range.")
    if duplicate_groups:
        raise SystemExit("Exact duplicate full documents detected.")
    if too_small:
        raise SystemExit("One or more documents are suspiciously small.")


if __name__ == "__main__":
    main()
