"""Build the dense Chroma index for the football-laws corpus.

Dense model: BAAI/bge-small-en-v1.5
The BM25 index is intentionally rebuilt from chunks at query time because the
corpus is small and this avoids an opaque serialized dependency.
"""

from __future__ import annotations

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
VECTOR_DIR = ROOT / "data" / "vectorstore" / "chroma"
REPORT = ROOT / "data" / "eval" / "index_report.json"

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION = "football_laws"


def main() -> None:
    chunks = [
        json.loads(line)
        for line in CHUNKS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not chunks:
        raise SystemExit("No chunks found. Run scripts/build_chunks.py first.")

    model = SentenceTransformer(EMBED_MODEL)
    texts = [c["content"] for c in chunks]
    vectors = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(VECTOR_DIR))

    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    batch = 250
    for start in range(0, len(chunks), batch):
        part = chunks[start : start + batch]
        vec_part = vectors[start : start + batch]
        collection.add(
            ids=[c["chunk_id"] for c in part],
            documents=[c["content"] for c in part],
            embeddings=[v.tolist() for v in vec_part],
            metadatas=[
                {
                    "source_id": c["source_id"],
                    "title": c["title"],
                    "url": c["url"],
                    "season": c["season"],
                    "section": c.get("section") or "",
                    "page": c.get("page") if c.get("page") is not None else -1,
                }
                for c in part
            ],
        )

    report = {
        "embedding_model": EMBED_MODEL,
        "embedding_dimensions": int(vectors.shape[1]),
        "chunks_indexed": len(chunks),
        "collection": COLLECTION,
        "vector_store": "Chroma",
        "distance": "cosine",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
