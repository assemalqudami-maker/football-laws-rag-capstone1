# Final Capstone Submission — Track B

**Project:** Football Laws Referee RAG  
**Supervisor:** Dr. Yousif Alyousifi  
**Language:** English  
**Domain:** Association football refereeing and the IFAB Laws of the Game

## 1. Public GitHub repository

https://github.com/assemalqudami-maker/football-laws-rag-capstone1

## 2. Live demo

https://football-laws-rag-production.up.railway.app

The production service is deployed on Railway and the public Streamlit health endpoint returns HTTP 200.

## 3. Architecture Decision Record

`docs/ADR.md`

The ADR documents the official-IFAB source policy, structure-aware chunking, local BGE embeddings, Chroma, BM25 + dense retrieval, RRF fusion, Cohere Rerank v4.0 Pro, Cohere Command A generation, Streamlit, and Railway deployment.

## 4. RAGAS evaluation

20-question Cohere RAGAS evaluation:

| Metric | Score |
|---|---:|
| Faithfulness | **0.9675** |
| Answer Relevancy | **0.7635** |
| Mean RAGAS score | **0.8655** |

Detailed report: `docs/ragas_report.md`

## 5. Cost analysis

Three required usage scenarios are documented in:

`docs/cost_analysis.md`

The analysis covers 1K, 10K, and 100K monthly active users and separates Cohere generation and reranking assumptions.

## Additional retrieval result

The final production retriever uses hybrid dense + BM25 retrieval, RRF fusion, and Cohere Rerank v4.0 Pro.

**Recall@5: 93.3% (28/30)**

Required target: **>= 80%**

Detailed report: `docs/retrieval_evaluation.md`

## Corpus

- 31 official IFAB English sources
- 29 HTML sources
- 2 PDF sources
- 71,191 extracted words
- 1,031 chunks
- source-content lock for reproducibility
- no exact full-document duplicates detected

## Remaining usability evidence

The software and five formal submission items are complete. The course specification also requires testing the interface with three real users. Results must be recorded honestly in `docs/user_testing.md`; they must not be fabricated.
