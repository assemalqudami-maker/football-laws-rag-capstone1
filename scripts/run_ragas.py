"""Run the required 20-question RAGAS evaluation with Cohere.

This file intentionally uses Instructor's current Cohere V2 integration instead
of importing the non-existent `cohere.Cohere` class.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import TypeVar

import instructor
from cohere.errors import TooManyRequestsError
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Ragas 0.4.3 still imports the removed legacy module
# langchain_community.chat_models.vertexai at package import time.
# This project does not use Vertex AI, so provide a tiny compatibility shim
# instead of installing Google/Vertex dependencies solely for an unused type
# check. Remove this once Ragas releases the upstream import fix.
import types  # noqa: E402

_vertex_module_name = "langchain_community.chat_models.vertexai"
if _vertex_module_name not in sys.modules:
    _vertex_module = types.ModuleType(_vertex_module_name)

    class _UnusedChatVertexAI:
        pass

    _vertex_module.ChatVertexAI = _UnusedChatVertexAI
    sys.modules[_vertex_module_name] = _vertex_module

from football_rag.generation import FootballLawsRAG  # noqa: E402
from ragas.embeddings.base import embedding_factory  # noqa: E402
from ragas.llms.base import InstructorBaseRagasLLM  # noqa: E402
from ragas.metrics.collections import AnswerRelevancy, Faithfulness  # noqa: E402

DATASET = ROOT / "data" / "eval" / "ragas_questions.json"
OUT = ROOT / "data" / "eval" / "ragas_report.json"

ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class CohereRagasLLM(InstructorBaseRagasLLM):
    """Small RAGAS adapter around Instructor's Cohere V2 client."""

    def __init__(self, model: str, api_key: str) -> None:
        self.model = model
        provider_model = f"cohere/{model}"

        self.sync_client = instructor.from_provider(
            provider_model,
            api_key=api_key,
            max_tokens=2048,
        )
        self.async_client = instructor.from_provider(
            provider_model,
            async_client=True,
            api_key=api_key,
            max_tokens=2048,
        )

    def generate(
        self,
        prompt: str,
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        return self.sync_client.create(
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            temperature=0.01,
        )

    async def agenerate(
        self,
        prompt: str,
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        return await self.async_client.create(
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            temperature=0.01,
        )


def is_rate_limit_error(exc: Exception) -> bool:
    return (
        isinstance(exc, TooManyRequestsError)
        or "429" in str(exc)
        or "too many requests" in str(exc).lower()
        or "rate limit" in str(exc).lower()
    )


async def retry_async(label: str, call):
    backoff = float(os.getenv("COHERE_429_BACKOFF_SECONDS", "65"))
    max_retries = int(os.getenv("COHERE_MAX_RETRIES", "4"))

    for attempt in range(1, max_retries + 2):
        try:
            return await call()
        except Exception as exc:
            if not is_rate_limit_error(exc) or attempt > max_retries:
                raise
            print(
                f"[Cohere] {label} rate-limited; sleeping "
                f"{backoff:.0f}s before retry {attempt}/{max_retries}."
            )
            await asyncio.sleep(backoff)


def retry_sync(label: str, call):
    backoff = float(os.getenv("COHERE_429_BACKOFF_SECONDS", "65"))
    max_retries = int(os.getenv("COHERE_MAX_RETRIES", "4"))

    for attempt in range(1, max_retries + 2):
        try:
            return call()
        except Exception as exc:
            if not is_rate_limit_error(exc) or attempt > max_retries:
                raise
            print(
                f"[Cohere] {label} rate-limited; sleeping "
                f"{backoff:.0f}s before retry {attempt}/{max_retries}."
            )
            time.sleep(backoff)


async def main() -> None:
    questions = json.loads(DATASET.read_text(encoding="utf-8"))
    if len(questions) != 20:
        raise SystemExit(f"Expected 20 RAGAS questions, found {len(questions)}.")

    api_key = os.getenv("COHERE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("COHERE_API_KEY is required for RAGAS evaluation.")

    judge_model = os.getenv(
        "RAGAS_JUDGE_MODEL",
        "command-a-03-2025",
    )
    embed_model = os.getenv("RAGAS_EMBED_MODEL", "embed-v4.0")

    judge_llm = CohereRagasLLM(
        model=judge_model,
        api_key=api_key,
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
    inter_question_delay = float(
        os.getenv("RAGAS_INTER_QUESTION_DELAY_SECONDS", "18")
    )

    for index, item in enumerate(questions, start=1):
        rag_result = retry_sync(
            f"{item['id']} generation",
            lambda: rag.answer(item["question"]),
        )

        faith = await retry_async(
            f"{item['id']} faithfulness",
            lambda: faithfulness.ascore(
                user_input=item["question"],
                response=rag_result.answer,
                retrieved_contexts=rag_result.contexts,
            ),
        )
        rel = await retry_async(
            f"{item['id']} answer relevancy",
            lambda: relevancy.ascore(
                user_input=item["question"],
                response=rag_result.answer,
            ),
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

        if index < len(questions) and inter_question_delay > 0:
            print(
                f"[Cohere] Trial-key pacing: sleeping "
                f"{inter_question_delay:.1f}s before next RAGAS question."
            )
            await asyncio.sleep(inter_question_delay)

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
            "command-a-03-2025",
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
