"""Extract clean English text from downloaded IFAB HTML/PDF sources.

Input:
  data/sources_manifest.csv
  data/raw/*

Output:
  data/processed/documents.jsonl
  data/eval/extraction_report.json

The public repository intentionally ignores downloaded raw/processed corpus files.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Iterable

import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sources_manifest.csv"
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
EVAL = ROOT / "data" / "eval"


def normalize_ws(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def html_to_blocks(path: Path) -> list[dict]:
    soup = BeautifulSoup(path.read_bytes(), "html.parser")

    for node in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        node.decompose()

    root = soup.find("main") or soup.find("article") or soup.body or soup

    blocks: list[dict] = []
    section = ""

    for node in root.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = normalize_ws(node.get_text(" ", strip=True))
        if not text:
            continue

        if node.name in {"h1", "h2", "h3", "h4"}:
            section = text
            continue

        # Remove obvious navigation/footer fragments that can survive in the main tree.
        low = text.lower()
        if low in {"previous", "next", "back", "menu"}:
            continue

        blocks.append(
            {
                "section": section,
                "page": None,
                "text": text,
            }
        )

    # Preserve order while removing exact duplicate adjacent/non-adjacent blocks.
    seen = set()
    deduped = []
    for block in blocks:
        key = (block["section"], block["text"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(block)
    return deduped


def pdf_to_blocks(path: Path) -> list[dict]:
    doc = fitz.open(path)
    blocks: list[dict] = []

    for page_index in range(len(doc)):
        text = normalize_ws(doc[page_index].get_text("text"))
        if not text:
            continue

        # PDF extraction is page-preserving at this stage. Chunking happens later.
        blocks.append(
            {
                "section": "",
                "page": page_index + 1,
                "text": text,
            }
        )

    return blocks


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    EVAL.mkdir(parents=True, exist_ok=True)

    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    out_path = PROCESSED / "documents.jsonl"
    report = {
        "source_count": len(rows),
        "extracted_sources": 0,
        "failed_sources": [],
        "documents": [],
    }

    with out_path.open("w", encoding="utf-8") as out:
        for row in rows:
            source_id = row["source_id"].strip()
            rel = row.get("local_path", "").strip()
            fmt = row["format"].strip().upper()

            if row.get("status", "").strip() != "downloaded" or not rel:
                report["failed_sources"].append(
                    {"source_id": source_id, "reason": "source was not downloaded"}
                )
                continue

            path = ROOT / rel
            if not path.exists():
                report["failed_sources"].append(
                    {"source_id": source_id, "reason": f"missing local file: {rel}"}
                )
                continue

            try:
                blocks = pdf_to_blocks(path) if fmt == "PDF" else html_to_blocks(path)
            except Exception as exc:
                report["failed_sources"].append(
                    {"source_id": source_id, "reason": f"extraction error: {exc}"}
                )
                continue

            char_count = sum(len(b["text"]) for b in blocks)
            if not blocks or char_count < 300:
                report["failed_sources"].append(
                    {
                        "source_id": source_id,
                        "reason": f"too little extracted text ({char_count} chars)",
                    }
                )
                continue

            record = {
                "source_id": source_id,
                "title": row["title"].strip(),
                "organization": row["organization"].strip(),
                "url": row["url"].strip(),
                "language": row["language"].strip(),
                "season": row["season"].strip(),
                "format": fmt,
                "blocks": blocks,
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

            report["documents"].append(
                {
                    "source_id": source_id,
                    "blocks": len(blocks),
                    "characters": char_count,
                    "pages": max(
                        [b["page"] for b in blocks if b["page"] is not None],
                        default=None,
                    ),
                }
            )
            report["extracted_sources"] += 1
            print(f"[OK] {source_id}: {len(blocks)} blocks, {char_count:,} chars")

    report_path = EVAL / "extraction_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"\nExtracted {report['extracted_sources']}/{report['source_count']} sources. "
        f"Report: {report_path.relative_to(ROOT)}"
    )

    if report["failed_sources"]:
        print("\nExtraction failures:")
        for item in report["failed_sources"]:
            print(f"- {item['source_id']}: {item['reason']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
