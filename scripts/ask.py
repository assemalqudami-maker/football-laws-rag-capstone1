"""Ask the indexed Football Laws RAG from the command line."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from football_rag.generation import FootballLawsRAG  # noqa: E402


def main() -> None:
    rag = FootballLawsRAG()
    print("Football Laws RAG. Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        result = rag.answer(question)
        print("\n" + result.answer)
        print("\nSources:")
        for i, source in enumerate(result.sources, start=1):
            where = source.get("section") or ""
            if source.get("page") not in (None, -1):
                where += f" (page {source['page']})"
            print(f"[{i}] {source['title']} — {where}")
            print(f"    {source['url']}")
        print()


if __name__ == "__main__":
    main()
