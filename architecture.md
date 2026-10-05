# Architecture

## Status

The corpus, chunking pipeline, dense index, hybrid retrieval, reranking, and Streamlit interface are implemented. The selected retrieval configuration achieves **Recall@5 = 93.3% (28/30)** on the fixed 30-question golden set, exceeding the required 80% target.

Remaining release steps are credential-dependent: run the 20-question RAGAS evaluation, deploy the Docker image publicly on Railway, and complete three real-user tests.

## High-level pipeline

```text
Official IFAB sources
        |
        v
Source validation + snapshot collection
        |
        v
HTML/PDF extraction
        |
        v
Normalization + metadata preservation
        |
        v
Structure-aware chunking
        |
        +----------------------+
        |                      |
        v                      v
BGE dense retrieval         BM25
        |                      |
        +----------+-----------+
                   v
             RRF fusion
                   |
                   v
        Cohere Rerank v4.0 Pro
                   |
                   v
             Top-5 evidence
                   |
                   v
       Grounded Cohere Command A response
          with source citations
```

## 1. Domain and source strategy

**Decision:** use official IFAB material only for the initial corpus.

**Why:** football refereeing is rules-based and authoritative wording matters. Mixing blogs, forums, social posts, or commentary into the core index would increase ambiguity and weaken source provenance.

The target edition is **2026/27**. The corpus contains **31 English IFAB source records** and passed automated collection and audit checks.

The repository stores:

- a version-controlled source manifest;
- a normalized source-content lock in `data/source_lock.json`;
- reproducible collection/extraction code.

Raw IFAB snapshots are not committed to Git. The lock file allows the build to detect upstream content drift before silently changing the indexed corpus.

## 2. Extraction

**HTML:** BeautifulSoup  
**PDF:** PyMuPDF

Each extracted record preserves:

- source ID;
- title;
- official URL;
- language;
- season/version;
- format;
- section heading;
- PDF page number when applicable;
- original extracted text.

## 3. Chunking

**Decision:** structure-aware section/page chunking with a maximum token window and overlap for long sections.

Configuration:

- tokenizer: `cl100k_base`;
- maximum window: about **600 tokens**;
- overlap for split long sections: **90 tokens**;
- preserve headings and PDF page boundaries.

Measured corpus output:

- **1,031 chunks**
- minimum: 14 tokens
- median: **103 tokens**
- 90th percentile: **190 tokens**
- maximum: 609 tokens

### Why the median is much smaller than 600

IFAB rules contain many short headings, bullets, conditions, exceptions, and sanctions. The pipeline intentionally keeps these short semantic units intact rather than merging unrelated provisions merely to reach a target size. The 600-token value is therefore a ceiling/window for long sections, not a forced fixed chunk size.

This preserves legal/rule structure and still produced the best measured retrieval result when combined with reranking.

## 4. Embeddings

**Decision:** `BAAI/bge-small-en-v1.5`.

Reasons:

- the application and corpus are English-only;
- the model is compact enough for CPU deployment;
- embeddings can be generated locally;
- it avoids recurring embedding API cost;
- it achieved strong measured retrieval performance on this corpus.

Query embeddings use the recommended retrieval query prefix and normalized vectors.

## 5. Vector database

**Decision:** Chroma with cosine distance.

Reasons:

- the corpus is small;
- local persistence is simple;
- metadata is preserved with each chunk;
- no separate managed vector service is required;
- it deploys inside the same container as the application.

Alternatives considered included Qdrant and pgvector. They would add operational complexity without a demonstrated benefit for this corpus size.

## 6. Hybrid retrieval

The production retriever combines:

- dense vector search;
- BM25 lexical search;
- Reciprocal Rank Fusion (RRF).

Why hybrid retrieval fits this domain:

- exact rule terms such as DOGSO, VAR, offside, handball, and measurements benefit from lexical matching;
- semantic paraphrases benefit from dense retrieval;
- RRF combines the two rankings without requiring their raw scores to share a scale.

## 7. Reranking

**Decision:** Cohere `rerank-v4.0-pro` for production. A local `cross-encoder/ms-marco-MiniLM-L-6-v2` remains only as a credential-free CI baseline.

The retriever first collects a broader candidate set, then sends up to 20 candidates to Cohere Rerank and returns the final Top 5 evidence chunks.

Measured Recall@5:

- BM25: **90.0%**
- Dense: **86.7%**
- Hybrid RRF: **86.7%**
- Hybrid + reranking: **93.3%**

The 93.3% result is the local baseline. The production Cohere reranker uses the same candidate set and golden labels; its final Recall@5 is measured in the manual Cohere evaluation workflow after the API key is configured.

## 8. Generation

**Decision:** Cohere Chat API with `command-a-03-2025`, configurable through `COHERE_CHAT_MODEL`.

The generation prompt requires the model to:

- answer only from retrieved IFAB evidence;
- use bracket citations linked to the retrieved source list;
- preserve precise rule meaning;
- state when the supplied evidence is insufficient;
- avoid presenting the application as an official match authority.

Cohere receives the retrieved IFAB evidence through its document-grounding interface. The same provider is used for final answer generation and the RAGAS evaluator to keep the credential and model stack consistent.

## 9. Evaluation

### Retrieval

- fixed 30-question golden set;
- evidence anchors tied to official IFAB source IDs;
- anchors resolved to concrete chunk IDs after chunking;
- Recall@5 target: >= 80%;
- measured best result: **93.3% (28/30)**.

See `docs/retrieval_evaluation.md`.

### Generation

A separate 20-question RAGAS evaluation set is prepared. It uses Cohere Command A as the evaluator LLM and Cohere Embed v4 for embedding-dependent metrics. The workflow measures:

- Faithfulness;
- Answer Relevancy.

The RAGAS workflow is manual to avoid accidental API-budget consumption.

## 10. Interface

**Decision:** Streamlit.

Implemented features:

- English-only interface;
- simple username/password authentication from environment variables;
- question input;
- example questions;
- grounded answer;
- expandable retrieved evidence;
- official source links;
- response latency;
- short recent-question history.

## 11. Deployment

**Decision:** Railway using the repository Dockerfile.

Why Railway:

- direct GitHub repository deployment;
- Dockerfile support;
- environment-variable secrets;
- public generated domains;
- automatic redeployment on repository updates.

The image:

1. installs CPU-only PyTorch and runtime dependencies;
2. caches the local BGE dense embedding model;
3. validates and downloads the locked IFAB corpus;
4. extracts and audits source text;
5. builds chunks and the Chroma index;
6. starts Streamlit on Railway's `PORT`.

## 12. Reproducibility and cost control

- corpus source IDs and URLs are version-controlled;
- normalized source hashes are locked;
- upstream source drift causes the audit to fail;
- raw source text is not republished in Git;
- dense embeddings remain local while production reranking and generation use the Cohere API;
- RAGAS runs only through a manual workflow;
- the cost model is reproducible in `scripts/cost_analysis.py`;
- model and evaluation choices are documented rather than claimed without measurement.
