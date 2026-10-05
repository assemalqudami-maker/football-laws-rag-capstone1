# Architecture

## Status

The corpus, chunking baseline, dense index, hybrid retrieval, and reranking pipeline are implemented and measured. The selected hybrid + reranking configuration achieves **Recall@5 = 93.3% (28/30)** on the fixed golden set, exceeding the 80% capstone target. Generation, RAGAS evaluation, and public deployment remain dependent on configured deployment/API credentials.

## High-level pipeline

```text
Official IFAB sources
        |
        v
Source validation + snapshot collection
        |
        v
HTML/PDF text extraction
        |
        v
Cleaning + metadata preservation
        |
        v
Structure-aware chunking
        |
        +--------------------+
        |                    |
        v                    v
Dense embeddings          BM25 index
        |                    |
        +---------+----------+
                  v
          Hybrid retrieval
             (RRF fusion)
                  |
                  v
              Reranker
                  |
                  v
           Top evidence
                  |
                  v
          Grounded LLM answer
           with citations
```

## 1. Source collection

**Choice:** official IFAB sources only for the initial corpus.

**Why:** the domain is rules-based and authoritative wording matters. Mixing blogs, forums, or commentary into the core index would increase ambiguity and make source provenance harder to defend.

The source manifest is version-controlled. Raw downloaded snapshots are local artifacts and are not committed by default.

## 2. Extraction

- HTML: BeautifulSoup
- PDF: PyMuPDF first, with pypdf as a fallback for diagnostics

Every extracted record should preserve:

- source_id
- title
- URL
- season/version
- source type
- section heading
- law number where applicable
- page number for PDFs
- original text

## 3. Chunking

### Initial candidate

Structure-aware recursive chunking with section boundaries and overlap.

Starting configuration for evaluation:

- target size: 450–650 tokens
- overlap: 70–100 tokens
- never split a short rule bullet away from its heading when avoidable

### Why this strategy

Football laws are highly structured. A fixed-size splitter can separate a condition from its exception or sanction. Structure-aware chunks should preserve the relation between headings, bullets, exceptions, and restart/sanction rules.

### Alternatives to compare

- fixed-token chunking
- recursive chunking
- parent-child chunking

The final choice will be based on Recall@5 using the same golden set.

## 4. Embeddings

### Candidate models

1. `text-embedding-3-small`
2. a multilingual/local sentence-transformer baseline if deployment cost requires it

### Decision rule

Choose the model that gives the best retrieval quality for the cost and deployment constraints. Do not select a model only because it is popular.

## 5. Vector database

### Initial candidate: Chroma

Why it is a reasonable first choice:

- small corpus
- local development is simple
- persistence is easy
- no separate managed service is required
- suitable for a capstone prototype

### Alternatives

- Qdrant
- pgvector

If deployment persistence or filtering requirements make Chroma awkward, the project will move to Qdrant or pgvector and document the measured reason.

## 6. Hybrid retrieval

The target retriever combines:

- dense vector search
- BM25 lexical search
- Reciprocal Rank Fusion (RRF)

Why hybrid search is required here:

- law questions often contain exact terms such as "DOGSO", "deliberate play", "handball", or "penalty mark";
- dense retrieval captures semantic paraphrases;
- BM25 protects exact legal terminology and rare phrases.

## 7. Reranking

Retrieve a wider candidate set (for example 20), then rerank to a final top 5.

Candidate rerankers:

- Cohere Rerank
- BGE reranker running locally

Selection will be based on Recall@5, latency, and cost.

## 8. Generation

The generation prompt will require:

- answer only from retrieved evidence;
- cite sources;
- distinguish the law text from explanatory wording;
- abstain when evidence is insufficient.

Temperature should remain low for rule interpretation.

## 9. Evaluation

### Retrieval

- 30 golden questions
- manually labelled supporting chunks
- Recall@5 target: >= 80%

### Generation

- 20-question RAGAS evaluation set
- report at least faithfulness, answer relevance, and context relevance/precision where supported by the installed RAGAS version

## 10. Interface

**Planned:** Streamlit.

Reasons:

- fast to implement;
- simple Python integration;
- easy deployment to Hugging Face Spaces or another supported host;
- sufficient for a professional portfolio demo.

The UI will be English-only and include:

- login gate
- question box
- answer
- expandable citations/evidence
- source title and URL
- response latency

## 11. Deployment

Target: Hugging Face Spaces first, with Railway as fallback.

Final deployment choice will be based on:

- persistence requirements
- secrets handling
- memory limits
- cold-start time
- model footprint
- current pricing/free-tier availability

## 12. Reproducibility and cost control

- never re-embed unchanged files;
- hash source snapshots;
- cache embeddings;
- separate ingestion from query execution;
- test evaluation on small samples before full RAGAS runs;
- log model, parameters, corpus version, and date for every evaluation run.


## Measured retrieval result

On the fixed 30-question golden set:

- BM25: 90.0% Recall@5
- Dense: 86.7% Recall@5
- Hybrid RRF: 86.7% Recall@5
- Hybrid + reranking: **93.3% Recall@5**

The production retriever therefore keeps the required hybrid design and reranking stage. See `docs/retrieval_evaluation.md` for the reproducible comparison.
