"""Evaluate retrieval Recall@5 on the 30-question golden set.

Gold evidence is defined by short phrases copied from the official source.
A question is a hit when at least one returned top-5 chunk from the expected
source contains one of its gold evidence phrases.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from football_rag.retrieval import HybridRetriever  # noqa: E402

GOLDEN = ROOT / "data" / "eval" / "golden_questions.json"
OUT = ROOT / "data" / "eval" / "recall_report.json"


def norm(text: str) -> str:
    return " ".join(text.casefold().split())


def is_gold(chunk: dict, item: dict) -> bool:
    expected_sources = set(item["expected_source_ids"])
    if chunk["source_id"] not in expected_sources:
        return False
    content = norm(chunk["content"])
    return any(norm(p) in content for p in item["gold_phrases"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["bm25", "dense", "hybrid"], default="hybrid")
    parser.add_argument("--no-rerank", action="store_true")
    args = parser.parse_args()

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    if len(golden) != 30:
        raise SystemExit(f"Expected 30 golden questions, found {len(golden)}.")

    retriever = HybridRetriever(use_reranker=not args.no_rerank)

    hits = 0
    details = []

    for item in golden:
        results = retriever.retrieve(
            item["question"],
            candidate_k=20,
            final_k=5,
            mode=args.mode,
        )
        hit = any(is_gold(chunk, item) for chunk in results)
        hits += int(hit)
        details.append(
            {
                "id": item["id"],
                "question": item["question"],
                "hit": hit,
                "returned": [
                    {
                        "chunk_id": c["chunk_id"],
                        "source_id": c["source_id"],
                        "section": c.get("section"),
                        "page": c.get("page"),
                    }
                    for c in results
                ],
            }
        )
        print(f"{item['id']}: {'HIT' if hit else 'MISS'}")

    recall = hits / len(golden)
    report = {
        "mode": args.mode,
        "reranking": not args.no_rerank,
        "hits": hits,
        "questions": len(golden),
        "recall_at_5": recall,
        "target": 0.80,
        "target_met": recall >= 0.80,
        "details": details,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nRecall@5 = {hits}/{len(golden)} = {recall:.1%}")
    print("TARGET MET" if recall >= 0.80 else "TARGET NOT MET")


if __name__ == "__main__":
    main()
