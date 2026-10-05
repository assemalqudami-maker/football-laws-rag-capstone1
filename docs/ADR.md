# ADR-001 — Football Laws RAG Architecture

**Status:** Accepted for implementation; retrieval quality must still pass the measured Recall@5 gate before final submission.  
**Date:** 5 October 2026

## Context

The system must answer English questions about football refereeing from 20–50 authoritative documents, show evidence, use hybrid search plus reranking, reach at least 80% Recall@5 on 30 golden questions, expose a simple authenticated web UI, and be deployable at low cost. The corpus is small but terminology is exact and rule exceptions matter, so both semantic matching and literal legal terms must be preserved.

## Decision

The corpus uses official IFAB material only and targets the 2026/27 Laws of the Game. Source snapshots are downloaded reproducibly from the version-controlled manifest during build; full third-party source text is not committed to Git.

Extraction uses BeautifulSoup for HTML and PyMuPDF for PDFs while preserving source URL, title, section, season, and page metadata. The baseline chunker is section-aware and uses approximately 600-token windows with 90-token overlap. This is preferred over blind fixed-size splitting because IFAB rules are organised by Law, subsection, condition, sanction, and exception.

Dense retrieval uses **BAAI/bge-small-en-v1.5** with normalized embeddings stored in **Chroma**. It was chosen as a compact English retrieval model that can run locally and avoids recurring embedding API cost. Chroma is appropriate because the corpus is small, persistent local indexing is simple, and no external vector-database service is required.

Retrieval is **hybrid**: dense search plus **BM25**, fused with **Reciprocal Rank Fusion (RRF)**. BM25 protects exact terms such as DOGSO, VAR, measurements, and disciplinary wording while dense retrieval handles paraphrases. The top candidate set is reranked locally with **cross-encoder/ms-marco-MiniLM-L-6-v2**, then the best five chunks are sent to generation.

Generation uses the OpenAI **Responses API** with a low-cost model configured through `OPENAI_MODEL` (baseline: `gpt-6-luna`). The prompt requires answers only from retrieved IFAB evidence, bracket citations, and explicit abstention when evidence is insufficient. Secrets are provided only through environment variables.

The interface is **Streamlit** with username/password authentication from deployment secrets. Deployment uses a Docker image so the same build can run on Hugging Face Spaces or Railway. During the image build the corpus is collected, extracted, chunked, and indexed, avoiding the need to publish raw IFAB text in the Git repository.

## Consequences

This architecture minimizes recurring cost and vendor dependence in retrieval, keeps provenance auditable, and satisfies the required hybrid/rerank design. The trade-offs are larger Docker builds, model-download time, and CPU reranking latency. Final acceptance depends on measured Recall@5 >= 80%, a 20-question RAGAS report, three real-user tests, and successful public deployment.
