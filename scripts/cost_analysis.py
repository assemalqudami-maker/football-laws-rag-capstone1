"""Recalculate monthly generation-token cost scenarios."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries-per-user", type=float, default=10)
    parser.add_argument("--input-tokens", type=float, default=3500)
    parser.add_argument("--output-tokens", type=float, default=250)
    parser.add_argument("--input-price", type=float, default=0.05,
                        help="USD per 1M input tokens")
    parser.add_argument("--output-price", type=float, default=0.25,
                        help="USD per 1M output tokens")
    args = parser.parse_args()

    per_query = (
        args.input_tokens / 1_000_000 * args.input_price
        + args.output_tokens / 1_000_000 * args.output_price
    )

    print(f"Estimated model cost/query: USD {per_query:.8f}")
    print("| Users | Queries/month | Model cost/month |")
    print("|---:|---:|---:|")
    for users in (1_000, 10_000, 100_000):
        queries = users * args.queries_per_user
        cost = queries * per_query
        print(f"| {users:,} | {queries:,.0f} | USD {cost:,.2f} |")


if __name__ == "__main__":
    main()
