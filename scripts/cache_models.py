"""Pre-download the local dense embedding model for container startup."""

from sentence_transformers import SentenceTransformer

EMBED_MODEL = "BAAI/bge-small-en-v1.5"


def main() -> None:
    print(f"Caching embedding model: {EMBED_MODEL}")
    SentenceTransformer(EMBED_MODEL)
    print("Embedding model cache ready.")


if __name__ == "__main__":
    main()
