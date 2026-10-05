# Cost Analysis

**Pricing snapshot:** 5 October 2026  
**Generation model used for the baseline:** `gpt-6-luna` (Standard, short-context tier)  
**Dense embeddings and reranking:** local open-source models, so there is no per-query embedding or reranking API charge.

The current OpenAI API pricing page lists GPT-6 Luna Standard short-context pricing at **$0.05 per 1M input tokens** and **$0.25 per 1M output tokens**.

Pricing source: https://developers.openai.com/api/docs/pricing

## Assumptions

- 10 questions per active user per month
- 3,500 input tokens per question
- 250 output tokens per answer
- local BGE embeddings
- local BM25
- local cross-encoder reranking
- no web search or other paid tools in the query path

Estimated model cost per query:

```text
input  = 3,500 / 1,000,000 × $0.05 = $0.0001750
output =   250 / 1,000,000 × $0.25 = $0.0000625
total                                  $0.0002375/query
```

| Monthly active users | Queries/user/month | Queries/month | Estimated generation cost/month |
|---:|---:|---:|---:|
| 1,000 | 10 | 10,000 | **$2.38** |
| 10,000 | 10 | 100,000 | **$23.75** |
| 100,000 | 10 | 1,000,000 | **$237.50** |

Hosting is excluded until the actual Hugging Face Spaces or Railway tier is selected. Recalculate this table with `python scripts/cost_analysis.py` whenever model pricing or measured token usage changes.
