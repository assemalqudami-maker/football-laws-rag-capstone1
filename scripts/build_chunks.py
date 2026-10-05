"""Build structure-aware chunks from data/processed/documents.jsonl.

The baseline keeps IFAB section headings attached to their text, uses a
token-aware sliding window only when a section is long, and preserves all
citation metadata.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import tiktoken

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "documents.jsonl"
OUTPUT = ROOT / "data" / "processed" / "chunks.jsonl"
REPORT = ROOT / "data" / "eval" / "chunk_report.json"

ENC = tiktoken.get_encoding("cl100k_base")
TARGET_TOKENS = 600
OVERLAP_TOKENS = 90


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_tokens(text: str, size: int, overlap: int) -> list[str]:
    ids = ENC.encode(text)
    if len(ids) <= size:
        return [text]

    parts = []
    step = size - overlap
    for start in range(0, len(ids), step):
        part = ENC.decode(ids[start : start + size]).strip()
        if part:
            parts.append(part)
        if start + size >= len(ids):
            break
    return parts


def main() -> None:
    docs = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "strategy": "section-aware token windows",
        "tokenizer": "tiktoken cl100k_base",
        "target_tokens": TARGET_TOKENS,
        "overlap_tokens": OVERLAP_TOKENS,
        "source_count": len(docs),
        "chunk_count": 0,
        "by_source": {},
        "token_stats": {},
    }

    token_lengths: list[int] = []

    with OUTPUT.open("w", encoding="utf-8") as out:
        for doc in docs:
            # Combine adjacent HTML blocks that share a section. PDF page blocks
            # remain separate because page-level citation precision matters.
            groups = []
            current_key = None
            current_texts = []

            for block in doc["blocks"]:
                key = (block.get("page"), block.get("section") or "")
                if key != current_key and current_texts:
                    groups.append((current_key, current_texts))
                    current_texts = []
                current_key = key
                current_texts.append(clean(block["text"]))

            if current_texts:
                groups.append((current_key, current_texts))

            source_chunks = 0
            for group_index, (key, texts) in enumerate(groups):
                page, section = key
                body = "\n".join(t for t in texts if t)
                if not body:
                    continue

                windows = split_tokens(body, TARGET_TOKENS, OVERLAP_TOKENS)
                for window_index, window in enumerate(windows):
                    heading = section.strip() or doc["title"]
                    content = f"{heading}\n\n{window}".strip()
                    token_count = len(ENC.encode(content))
                    token_lengths.append(token_count)

                    chunk_id = (
                        f"{doc['source_id']}::g{group_index:04d}::w{window_index:02d}"
                    )
                    record = {
                        "chunk_id": chunk_id,
                        "source_id": doc["source_id"],
                        "title": doc["title"],
                        "url": doc["url"],
                        "season": doc["season"],
                        "language": doc["language"],
                        "format": doc["format"],
                        "section": section,
                        "page": page,
                        "content": content,
                        "token_count": token_count,
                    }
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    source_chunks += 1

            report["by_source"][doc["source_id"]] = source_chunks
            report["chunk_count"] += source_chunks
            print(f"[OK] {doc['source_id']}: {source_chunks} chunks")

    token_lengths.sort()
    if token_lengths:
        n = len(token_lengths)
        report["token_stats"] = {
            "min": token_lengths[0],
            "median": token_lengths[n // 2],
            "p90": token_lengths[min(n - 1, int(n * 0.90))],
            "max": token_lengths[-1],
        }

    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nBuilt {report['chunk_count']} chunks.")
    print(json.dumps(report["token_stats"], indent=2))


if __name__ == "__main__":
    main()
