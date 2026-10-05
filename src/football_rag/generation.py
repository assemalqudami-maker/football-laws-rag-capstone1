"""Grounded answer generation for Football Laws RAG using Cohere."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import cohere

from .retrieval import HybridRetriever

DEFAULT_MODEL = os.getenv("COHERE_CHAT_MODEL", "command-a-plus-05-2026")


@dataclass
class RAGAnswer:
    answer: str
    sources: list[dict[str, Any]]
    contexts: list[str]


class FootballLawsRAG:
    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        api_key = os.getenv("COHERE_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "COHERE_API_KEY is required for Cohere generation."
            )

        self.model = model
        self.retriever = HybridRetriever(
            use_reranker=True,
            reranker_provider="cohere",
        )
        self.client = cohere.ClientV2(api_key=api_key)

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

        documents = []
        for i, item in enumerate(sources, start=1):
            location = item.get("section") or ""
            if item.get("page") not in (None, -1):
                location = f"{location} | page {item['page']}".strip(" |")

            documents.append(
                {
                    "data": {
                        "evidence_id": str(i),
                        "title": item["title"],
                        "location": location,
                        "url": item["url"],
                        "text": item["content"],
                    }
                }
            )

        system_message = (
            "You are an educational assistant for association-football refereeing. "
            "Answer only from the supplied official IFAB documents. "
            "Do not use outside knowledge. If the evidence is insufficient or "
            "ambiguous, explicitly say that the provided sources do not establish "
            "the answer. Keep rule wording precise and concise. "
            "Do not present the answer as an official ruling for a real match."
        )

        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {
                    "role": "user",
                    "content": (
                        question
                        + "\n\nGive a concise answer and mention important "
                        "conditions or exceptions."
                    ),
                },
            ],
            documents=documents,
        )

        answer = response.message.content[0].text.strip()

        return RAGAnswer(
            answer=answer,
            sources=sources,
            contexts=[s["content"] for s in sources],
        )
