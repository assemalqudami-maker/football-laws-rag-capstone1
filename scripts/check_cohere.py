"""Validate Cohere API access before running paid/limited evaluations."""

from __future__ import annotations

import os

import cohere


def main() -> None:
    api_key = os.getenv("COHERE_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("COHERE_API_KEY is not set.")

    chat_model = os.getenv(
        "COHERE_CHAT_MODEL",
        "command-a-03-2025",
    )
    rerank_model = os.getenv(
        "COHERE_RERANK_MODEL",
        "rerank-v4.0-pro",
    )
    embed_model = os.getenv("COHERE_EMBED_MODEL", "embed-v4.0")

    client = cohere.ClientV2(api_key=api_key)

    print(f"Checking chat model: {chat_model}")
    chat = client.chat(
        model=chat_model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: COHERE_OK",
            }
        ],
    )
    print("Chat access: OK")
    print("Chat response:", chat.message.content[0].text.strip())

    print(f"Checking rerank model: {rerank_model}")
    rerank = client.rerank(
        model=rerank_model,
        query="football referee law",
        documents=[
            "The referee enforces the Laws of the Game.",
            "This document is about cooking.",
        ],
        top_n=1,
    )
    if not rerank.results:
        raise SystemExit("Cohere rerank returned no results.")
    print("Rerank access: OK")

    print(f"Checking embed model: {embed_model}")
    embed = client.embed(
        model=embed_model,
        inputs=[
            {
                "content": [
                    {
                        "type": "text",
                        "text": "football refereeing laws",
                    }
                ]
            }
        ],
        input_type="search_query",
        embedding_types=["float"],
    )
    if not embed.embeddings.float:
        raise SystemExit("Cohere embed returned no vector.")
    print("Embed access: OK")

    print("COHERE VALIDATION PASSED")


if __name__ == "__main__":
    main()
