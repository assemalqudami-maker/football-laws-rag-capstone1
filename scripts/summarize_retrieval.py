"""Combine retrieval evaluation variants into one comparison report."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "data" / "eval"
OUT_JSON = EVAL / "retrieval_summary.json"
OUT_MD = EVAL / "retrieval_summary.md"

VARIANTS = [
    ("BM25", "recall_bm25.json"),
    ("Dense", "recall_dense.json"),
    ("Hybrid (RRF)", "recall_hybrid.json"),
    ("Hybrid + rerank", "recall_hybrid_rerank.json"),
]


def main() -> None:
    rows = []
    for label, filename in VARIANTS:
        report = json.loads((EVAL / filename).read_text(encoding="utf-8"))
        rows.append(
            {
                "variant": label,
                "hits": report["hits"],
                "questions": report["questions"],
                "recall_at_5": report["recall_at_5"],
                "target_met": report["target_met"],
                "file": filename,
            }
        )

    best = max(rows, key=lambda row: row["recall_at_5"])
    result = {
        "target": 0.80,
        "best_variant": best["variant"],
        "best_recall_at_5": best["recall_at_5"],
        "target_met": best["recall_at_5"] >= 0.80,
        "variants": rows,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    md = [
        "# Retrieval Evaluation Summary",
        "",
        "| Variant | Hits | Recall@5 | Target met |",
        "|---|---:|---:|:---:|",
    ]
    for row in rows:
        md.append(
            f"| {row['variant']} | {row['hits']}/{row['questions']} | "
            f"{row['recall_at_5']:.1%} | "
            f"{'Yes' if row['target_met'] else 'No'} |"
        )

    md += [
        "",
        f"**Best variant:** {best['variant']} — {best['recall_at_5']:.1%} Recall@5.",
        "",
        "The capstone target is Recall@5 >= 80% on the fixed 30-question golden set.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2))

    if not result["target_met"]:
        raise SystemExit("No retrieval variant met the 80% Recall@5 target.")


if __name__ == "__main__":
    main()
