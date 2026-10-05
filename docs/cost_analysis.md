# Cost Analysis

**Pricing snapshot:** 5 October 2026  
**Generation model:** `gpt-6-luna` (Standard processing, short-context requests)  
**Dense embeddings and reranking:** local open-source models, so the baseline has no per-query embedding or reranking API charge.

The OpenAI API model/pricing documentation lists GPT-6 Luna Standard text pricing at **$0.10 per 1M input tokens** and **$0.50 per 1M output tokens** as of this snapshot.

Pricing sources:

- https://developers.openai.com/api/docs/models/gpt-6-luna
- https://developers.openai.com/api/docs/pricing

## Assumptions

- 10 questions per active user per month
- 3,500 input tokens per question, including retrieved context and instructions
- 250 output tokens per answer
- local BGE dense embeddings
- local BM25
- local cross-encoder reranking
- no paid web-search/tool calls in the query path

Estimated model cost per query:

```text
input  = 3,500 / 1,000,000 × $0.10 = $0.000350
output =   250 / 1,000,000 × $0.50 = $0.000125
total                                  $0.000475/query
```

| Monthly active users | Queries/user/month | Queries/month | Estimated generation cost/month |
|---:|---:|---:|---:|
| 1,000 | 10 | 10,000 | **$4.75** |
| 10,000 | 10 | 100,000 | **$47.50** |
| 100,000 | 10 | 1,000,000 | **$475.00** |

## What is not included

Hosting/compute is intentionally excluded until the actual Hugging Face Spaces or Railway tier is selected. Network egress, taxes, regional processing premiums, Fast mode, and unusually long prompts are also excluded. The final submission should replace the assumed 3,500/250 token profile with measured production logs if they materially differ.

## Reproducibility

Run:

```bash
python scripts/cost_analysis.py
```

The calculator exposes the request count, token volumes, and model prices as command-line arguments so the table can be regenerated whenever pricing or measured usage changes.
