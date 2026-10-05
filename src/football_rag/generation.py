"""Grounded answer generation for Football Laws RAG."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from .retrieval import HybridRetriever

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


@dataclass
class RAGAnswer:
    answer: str
    sources: list[dict[str, Any]]
    contexts: list[str]


class FootballLawsRAG:
    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.retriever = HybridRetriever(use_reranker=True)
        self.client = OpenAI()

    def answer(self, question: str) -> RAGAnswer:
        question = question.strip()
        if not question:
            raise ValueError("Question cannot be empty.")

        sources = self.retriever.retrieve(
            question,
            candidate_k=20,
            final_k=5,
            mode="hybrid",
        )

        context_parts = []
        for i, item in enumerate(sources, start=1):
            location = item.get("section") or ""
            if item.get("page") not in (None, -1):
                location = f"{location} | page {item['page']}".strip(" |")
            context_parts.append(
                f"[{i}] {item['title']} | {location}\n"
                f"Source: {item['url']}\n"
                f"{item['content']}"
            )

        context = "\n\n---\n\n".join(context_parts)

        instructions = (
            "You are an educational assistant for association-football refereeing. "
            "Answer ONLY from the supplied IFAB evidence. "
            "Do not use outside knowledge. If the evidence is insufficient or "
            "ambiguous, explicitly say that the provided sources do not establish "
            "the answer. Keep legal/rule wording precise. Cite supporting evidence "
            "using bracket numbers such as [1] or [2]. Do not invent citations. "
            "Do not present the answer as an official ruling for a real match."
        )

        user_input = (
            f"QUESTION:\n{question}\n\n"
            f"RETRIEVED IFAB EVIDENCE:\n{context}\n\n"
            "Give a concise answer followed by any important conditions or exceptions."
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_input,
            reasoning={"effort": "none"},
            max_output_tokens=500,
        )

        return RAGAnswer(
            answer=response.output_text.strip(),
            sources=sources,
            contexts=[s["content"] for s in sources],
        )
