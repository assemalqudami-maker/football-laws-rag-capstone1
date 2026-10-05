"""Pre-download runtime retrieval models for deterministic container startup."""

from sentence_transformers import CrossEncoder, SentenceTransformer

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def main() -> None:
    print(f"Caching embedding model: {EMBED_MODEL}")
    SentenceTransformer(EMBED_MODEL)
    print(f"Caching reranker: {RERANK_MODEL}")
    CrossEncoder(RERANK_MODEL)
    print("Model cache ready.")


if __name__ == "__main__":
    main()
