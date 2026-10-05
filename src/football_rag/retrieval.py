"""Hybrid retrieval: BGE dense search + BM25 + RRF + configurable reranking."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import chromadb
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

ROOT = Path(__file__).resolve().parents[2]
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
VECTOR_DIR = ROOT / "data" / "vectorstore" / "chroma"

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
LOCAL_RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
COHERE_RERANK_MODEL = os.getenv("COHERE_RERANK_MODEL", "rerank-v4.0-pro")
COLLECTION = "football_laws"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


class HybridRetriever:
    def __init__(
        self,
        use_reranker: bool = True,
        reranker_provider: str | None = None,
    ) -> None:
        self.chunks = [
            json.loads(line)
            for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.by_id = {c["chunk_id"]: c for c in self.chunks}
        self.ids = [c["chunk_id"] for c in self.chunks]

        self.bm25 = BM25Okapi([tokenize(c["content"]) for c in self.chunks])
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.client = chromadb.PersistentClient(path=str(VECTOR_DIR))
        self.collection = self.client.get_collection(COLLECTION)

        self.use_reranker = use_reranker
        self.reranker_provider = (
            reranker_provider
            or os.getenv("RERANK_PROVIDER", "cohere")
        ).strip().lower()

        self.local_reranker = None
        self.cohere_client = None

        if self.use_reranker:
            if self.reranker_provider == "local":
                self.local_reranker = CrossEncoder(LOCAL_RERANK_MODEL)
            elif self.reranker_provider == "cohere":
                api_key = os.getenv("COHERE_API_KEY", "").strip()
                if not api_key:
                    raise RuntimeError(
                        "COHERE_API_KEY is required when RERANK_PROVIDER=cohere."
                    )
                import cohere

                self.cohere_client = cohere.ClientV2(api_key=api_key)
            else:
                raise ValueError(
                    "reranker_provider must be 'cohere' or 'local'."
                )

    def dense(self, question: str, k: int = 20) -> list[str]:
        q = QUERY_PREFIX + question.strip()
        vector = self.embedder.encode([q], normalize_embeddings=True)[0]
        result = self.collection.query(
            query_embeddings=[vector.tolist()],
            n_results=min(k, len(self.chunks)),
        )
        return result["ids"][0]

    def lexical(self, question: str, k: int = 20) -> list[str]:
        scores = self.bm25.get_scores(tokenize(question))
        order = np.argsort(scores)[::-1][: min(k, len(self.chunks))]
        return [self.ids[int(i)] for i in order]

    @staticmethod
    def rrf(lists: list[list[str]], constant: int = 60) -> list[str]:
        scores: dict[str, float] = {}
        for ranked in lists:
            for rank, chunk_id in enumerate(ranked, start=1):
                scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (
                    constant + rank
                )
        return sorted(scores, key=scores.get, reverse=True)

    def _rerank_local(
        self,
        question: str,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        pairs = [(question, c["content"]) for c in candidates]
        scores = self.local_reranker.predict(pairs)
        ranked = sorted(
            zip(candidates, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )
        return [dict(c, rerank_score=float(s)) for c, s in ranked]

    def _rerank_cohere(
        self,
        question: str,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        response = self.cohere_client.rerank(
            model=COHERE_RERANK_MODEL,
            query=question,
            documents=[c["content"] for c in candidates],
            top_n=len(candidates),
        )

        ranked = []
        for item in response.results:
            candidate = candidates[item.index]
            ranked.append(
                dict(
                    candidate,
                    rerank_score=float(item.relevance_score),
                )
            )
        return ranked

    def retrieve(
        self,
        question: str,
        candidate_k: int = 20,
        final_k: int = 5,
        mode: str = "hybrid",
    ) -> list[dict[str, Any]]:
        if mode == "dense":
            candidate_ids = self.dense(question, candidate_k)
        elif mode == "bm25":
            candidate_ids = self.lexical(question, candidate_k)
        elif mode == "hybrid":
            candidate_ids = self.rrf(
                [
                    self.dense(question, candidate_k),
                    self.lexical(question, candidate_k),
                ]
            )[:candidate_k]
        else:
            raise ValueError("mode must be dense, bm25, or hybrid")

        candidates = [self.by_id[cid] for cid in candidate_ids]

        if self.use_reranker and candidates:
            if self.reranker_provider == "cohere":
                candidates = self._rerank_cohere(question, candidates)
            else:
                candidates = self._rerank_local(question, candidates)

        return candidates[:final_k]
