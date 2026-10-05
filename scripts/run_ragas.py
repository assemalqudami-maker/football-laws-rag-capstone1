"""Run the required 20-question RAGAS evaluation with Cohere."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from cohere import Cohere

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from football_rag.generation import FootballLawsRAG  # noqa: E402
from ragas.embeddings.base import embedding_factory  # noqa: E402
from ragas.llms import llm_factory  # noqa: E402
from ragas.metrics.collections import AnswerRelevancy, Faithfulness  # noqa: E402

DATASET = ROOT / "data" / "eval" / "ragas_questions.json"
OUT = ROOT / "data" / "eval" / "ragas_report.json"


async def main() -> None:
    questions = json.loads(DATASET.read_text(encoding="utf-8"))
    if len(questions) != 20:
        raise SystemExit(f"Expected 20 RAGAS questions, found {len(questions)}.")

    api_key = os.getenv("COHERE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("COHERE_API_KEY is required for RAGAS evaluation.")

    judge_model = os.getenv(
        "RAGAS_JUDGE_MODEL",
        "command-a-plus-05-2026",
    )
    embed_model = os.getenv("RAGAS_EMBED_MODEL", "embed-v4.0")

    judge_client = Cohere(api_key=api_key)
    judge_llm = llm_factory(
        judge_model,
        provider="cohere",
        client=judge_client,
    )
    judge_embeddings = embedding_factory(
        "litellm",
        model=f"cohere/{embed_model}",
        api_key=api_key,
    )

    faithfulness = Faithfulness(llm=judge_llm)
    relevancy = AnswerRelevancy(
        llm=judge_llm,
        embeddings=judge_embeddings,
    )

    rag = FootballLawsRAG()
    rows = []

    for item in questions:
        rag_result = rag.answer(item["question"])

        faith = await faithfulness.ascore(
            user_input=item["question"],
            response=rag_result.answer,
            retrieved_contexts=rag_result.contexts,
        )
        rel = await relevancy.ascore(
            user_input=item["question"],
            response=rag_result.answer,
        )

        row = {
            "id": item["id"],
            "question": item["question"],
            "reference_answer": item["reference_answer"],
            "answer": rag_result.answer,
            "faithfulness": float(faith.value),
            "answer_relevancy": float(rel.value),
            "source_ids": [s["source_id"] for s in rag_result.sources],
        }
        rows.append(row)
        print(
            f"{item['id']}: faithfulness={row['faithfulness']:.3f} "
            f"relevancy={row['answer_relevancy']:.3f}"
        )

    avg_faith = sum(r["faithfulness"] for r in rows) / len(rows)
    avg_rel = sum(r["answer_relevancy"] for r in rows) / len(rows)
    overall = (avg_faith + avg_rel) / 2

    report = {
        "questions": len(rows),
        "provider": "Cohere",
        "judge_model": judge_model,
        "embedding_model": embed_model,
        "generation_model": os.getenv(
            "COHERE_CHAT_MODEL",
            "command-a-plus-05-2026",
        ),
        "rerank_model": os.getenv(
            "COHERE_RERANK_MODEL",
            "rerank-v4.0-pro",
        ),
        "metrics": {
            "faithfulness_mean": avg_faith,
            "answer_relevancy_mean": avg_rel,
            "ragas_mean": overall,
        },
        "items": rows,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
