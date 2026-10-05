# Retrieval Evaluation Report

**Evaluation date:** 5 October 2026  
**Golden set:** 30 fixed football-law questions  
**Metric:** Recall@5  
**Required target:** >= 80%  
**Best result:** **93.3% (28/30)**

## Results

| Retrieval configuration | Hits | Recall@5 | Target |
|---|---:|---:|:---:|
| BM25 | 27/30 | **90.0%** | Pass |
| Dense retrieval | 26/30 | **86.7%** | Pass |
| Hybrid dense + BM25 (RRF) | 26/30 | **86.7%** | Pass |
| Hybrid + cross-encoder reranking | 28/30 | **93.3%** | **Pass** |

## Selected production retriever

The production pipeline uses:

1. dense search with `BAAI/bge-small-en-v1.5`;
2. BM25 lexical search;
3. Reciprocal Rank Fusion (RRF);
4. cross-encoder reranking with `cross-encoder/ms-marco-MiniLM-L-6-v2`;
5. final Top-5 evidence chunks.

Although BM25 alone performed strongly, the required architecture includes hybrid retrieval and reranking. The reranked hybrid configuration also produced the best measured result, improving Recall@5 from 86.7% before reranking to 93.3%.

## Evaluation protocol

- The golden set is stored in `data/eval/golden_questions.json`.
- Each question has manually authored evidence anchors tied to expected official IFAB source IDs.
- After chunking, `scripts/label_gold_chunks.py` resolves those anchors into concrete chunk IDs.
- Retrieval is then measured against those fixed chunk IDs.
- The same gold labels are used for BM25, dense, hybrid, and reranked evaluation.
- The target is not changed to fit a retrieval configuration.

The corpus build produced **1,031 chunks** for this run.

## Reproduce

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
python scripts/evaluate_recall.py --mode hybrid
```

The automated GitHub Actions retrieval workflow completed successfully and uploaded the detailed JSON reports as a workflow artifact.
