# Retrieval Evaluation Report

**Evaluation date:** 5 October 2026  
**Golden set:** 30 fixed football-law questions  
**Metric:** Recall@5  
**Required target:** >= 80%

## Credential-free baseline

The automatic GitHub Actions workflow uses a local cross-encoder so retrieval quality can be checked on every code change without consuming API quota.

| Retrieval configuration | Hits | Recall@5 | Target |
|---|---:|---:|:---:|
| BM25 | 27/30 | **90.0%** | Pass |
| Dense retrieval | 26/30 | **86.7%** | Pass |
| Hybrid dense + BM25 (RRF) | 26/30 | **86.7%** | Pass |
| Hybrid + local cross-encoder reranking | 28/30 | **93.3%** | Pass |

This 93.3% result proves that the hybrid candidate set contains enough relevant evidence and that reranking materially improves the final Top 5.

## Production reranker

The production system now uses Cohere **`rerank-v4.0-pro`**. Cohere is intentionally evaluated in a manual workflow because every rerank request consumes API quota.

After the repository secret `COHERE_API_KEY` is configured, the **Cohere RAGAS evaluation** workflow performs:

1. a low-cost Cohere chat/rerank/embed access test;
2. the same 30-question Recall@5 evaluation using Cohere Rerank v4.0 Pro;
3. the required 20-question RAGAS evaluation.

The Cohere Recall@5 result must be recorded here after that credentialed run; it is not fabricated from the local baseline.

## Evaluation protocol

- The golden set is stored in `data/eval/golden_questions.json`.
- Evidence anchors are tied to expected official IFAB source IDs.
- `scripts/label_gold_chunks.py` resolves those anchors to concrete chunk IDs after chunking.
- All retrieval variants use the same 30 questions and gold chunk IDs.
- Candidate retrieval uses Top 20; reranking returns the final Top 5.
- The required target remains Recall@5 >= 80%.

## Reproduce the free local baseline

```bash
python scripts/check_sources.py
python scripts/collect_sources.py
python scripts/extract_sources.py
python scripts/audit_corpus.py
python scripts/build_chunks.py
python scripts/label_gold_chunks.py
python scripts/build_index.py

python scripts/evaluate_recall.py --mode bm25 --no-rerank
python scripts/evaluate_recall.py --mode dense --no-rerank
python scripts/evaluate_recall.py --mode hybrid --no-rerank
python scripts/evaluate_recall.py --mode hybrid --reranker-provider local
```

## Reproduce the Cohere production evaluation

After setting `COHERE_API_KEY`:

```bash
python scripts/check_cohere.py
python scripts/evaluate_recall.py --mode hybrid --reranker-provider cohere
```
