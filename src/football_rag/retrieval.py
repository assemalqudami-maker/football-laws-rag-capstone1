"""Hybrid retrieval: BGE dense search + BM25 + RRF + cross-encoder rerank."""

from __future__ import annotations

import json
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
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
COLLECTION = "football_laws"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


class HybridRetriever:
    def __init__(self, use_reranker: bool = True) -> None:
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
        self.reranker = CrossEncoder(RERANK_MODEL) if use_reranker else None

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
            pairs = [(question, c["content"]) for c in candidates]
            scores = self.reranker.predict(pairs)
            ranked = sorted(
                zip(candidates, scores),
                key=lambda item: float(item[1]),
                reverse=True,
            )
            candidates = [dict(c, rerank_score=float(s)) for c, s in ranked]

        return candidates[:final_k]
