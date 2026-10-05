"""Recalculate Cohere production cost scenarios for the RAG application."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries-per-user", type=float, default=10)
    parser.add_argument("--input-tokens", type=float, default=3500)
    parser.add_argument("--output-tokens", type=float, default=250)
    parser.add_argument(
        "--input-price",
        type=float,
        default=2.50,
        help="Command A USD per 1M input tokens",
    )
    parser.add_argument(
        "--output-price",
        type=float,
        default=10.00,
        help="Command A USD per 1M output tokens",
    )
    parser.add_argument(
        "--rerank-price-per-1k",
        type=float,
        default=1.00,
        help=(
            "Planning assumption in USD per 1,000 rerank searches. "
            "Replace with the current production-key price from Cohere."
        ),
    )
    args = parser.parse_args()

    generation_per_query = (
        args.input_tokens / 1_000_000 * args.input_price
        + args.output_tokens / 1_000_000 * args.output_price
    )
    rerank_per_query = args.rerank_price_per_1k / 1000
    total_per_query = generation_per_query + rerank_per_query

    print(f"Generation cost/query: USD {generation_per_query:.6f}")
    print(f"Rerank cost/query:     USD {rerank_per_query:.6f}")
    print(f"Total model cost:      USD {total_per_query:.6f}")
    print()
    print("| Users | Queries/month | Generation | Rerank | Total |")
    print("|---:|---:|---:|---:|---:|")

    for users in (1_000, 10_000, 100_000):
        queries = users * args.queries_per_user
        generation = queries * generation_per_query
        rerank = queries * rerank_per_query
        total = generation + rerank
        print(
            f"| {users:,} | {queries:,.0f} | "
            f"USD {generation:,.2f} | USD {rerank:,.2f} | "
            f"USD {total:,.2f} |"
        )


if __name__ == "__main__":
    main()
