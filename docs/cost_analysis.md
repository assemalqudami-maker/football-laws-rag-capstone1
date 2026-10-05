# Cost Analysis

**Pricing snapshot:** 5 October 2026  
**Production generation model:** Cohere `command-a-03-2025`  
**Production reranker:** Cohere `rerank-v4.0-pro`  
**Dense embeddings:** local `BAAI/bge-small-en-v1.5`

## Pricing basis

Cohere's current Command A documentation lists:

- **$2.50 / 1M input tokens**
- **$10.00 / 1M output tokens**

Source: https://docs.cohere.com/docs/command-a

Cohere also states that trial API-key calls are free but rate limited, while production keys are billed. Rerank is billed by search, where one search is one query over up to 100 documents before long-document chunking rules apply.

Sources:

- https://cohere.com/pricing
- https://docs.cohere.com/docs/how-does-cohere-pricing-work

The public pricing page does not expose a simple current pay-as-you-go Rerank v4 search price in the text captured for this report. Therefore the calculator keeps the rerank price as an explicit parameter. The default planning value is **$1 / 1,000 rerank searches**, matching the course RAG Engineering example; it must be replaced with the price shown for the student's production key before commercial use.

## Usage assumptions

- 10 questions per active user per month
- 3,500 billed input tokens per generated answer
- 250 billed output tokens per answer
- one Cohere rerank request per user question
- 20 candidate chunks sent to the reranker
- local dense query embedding, BM25, RRF, and Chroma
- no paid web-search/tool calls

### Estimated per-query cost

```text
Command A input:
3,500 / 1,000,000 × $2.50 = $0.008750

Command A output:
250 / 1,000,000 × $10.00 = $0.002500

Generation subtotal = $0.011250

Rerank planning assumption:
$1 / 1,000 searches = $0.001000

Estimated total = $0.012250 per query
```

## Three required scenarios

| Monthly active users | Queries/user/month | Queries/month | Generation | Rerank* | Estimated total/month |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 10 | 10,000 | $112.50 | $10.00 | **$122.50** |
| 10,000 | 10 | 100,000 | $1,125.00 | $100.00 | **$1,225.00** |
| 100,000 | 10 | 1,000,000 | $11,250.00 | $1,000.00 | **$12,250.00** |

* Rerank uses the documented planning assumption above, not an asserted current Rerank v4 production price.

## Student demo cost

For this capstone, a Cohere trial/evaluation key is suitable for development and evaluation because trial calls are free within Cohere's rate and usage limits. It must not be treated as a production/commercial deployment plan.

## RAGAS cost

The required RAGAS run is a one-time 20-question evaluation and is deliberately triggered manually. It uses Cohere Command A as the evaluator LLM and Cohere Embed v4 for embedding-dependent evaluation. It is excluded from the recurring monthly user scenarios because it is an offline evaluation workload, not part of every application query.

## Reproducibility

Run:

```bash
python scripts/cost_analysis.py
```

If the production Rerank price differs from the planning value:

```bash
python scripts/cost_analysis.py --rerank-price-per-1k <CURRENT_PRICE>
```
