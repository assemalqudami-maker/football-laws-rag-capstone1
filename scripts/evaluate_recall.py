"""Evaluate retrieval Recall@5 on the 30-question golden set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from football_rag.retrieval import HybridRetriever  # noqa: E402

GOLDEN = ROOT / "data" / "eval" / "golden_questions_labeled.json"
OUT = ROOT / "data" / "eval" / "recall_report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["bm25", "dense", "hybrid"],
        default="hybrid",
    )
    parser.add_argument("--no-rerank", action="store_true")
    parser.add_argument(
        "--reranker-provider",
        choices=["local", "cohere"],
        default="local",
        help="Used only when reranking is enabled.",
    )
    args = parser.parse_args()

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    if len(golden) != 30:
        raise SystemExit(f"Expected 30 golden questions, found {len(golden)}.")

    retriever = HybridRetriever(
        use_reranker=not args.no_rerank,
        reranker_provider=args.reranker_provider,
    )

    hits = 0
    details = []

    for item in golden:
        gold_ids = set(item.get("gold_chunk_ids", []))
        if not gold_ids:
            raise SystemExit(
                f"{item['id']} has no gold_chunk_ids. "
                "Run scripts/label_gold_chunks.py first."
            )

        results = retriever.retrieve(
            item["question"],
            candidate_k=20,
            final_k=5,
            mode=args.mode,
        )
        returned_ids = [chunk["chunk_id"] for chunk in results]
        matched = sorted(gold_ids.intersection(returned_ids))
        hit = bool(matched)
        hits += int(hit)

        details.append(
            {
                "id": item["id"],
                "question": item["question"],
                "hit": hit,
                "matched_gold_chunk_ids": matched,
                "gold_chunk_ids": sorted(gold_ids),
                "returned": [
                    {
                        "chunk_id": c["chunk_id"],
                        "source_id": c["source_id"],
                        "section": c.get("section"),
                        "page": c.get("page"),
                        "rerank_score": c.get("rerank_score"),
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
        "reranker_provider": (
            args.reranker_provider if not args.no_rerank else None
        ),
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
