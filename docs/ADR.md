# ADR-001 — Football Laws RAG Architecture

**Status:** Accepted  
**Date:** 5 October 2026

## Context

The capstone requires an English RAG system over 20–50 high-quality documents, hybrid retrieval with reranking, a fixed 30-question golden set, Recall@5 of at least 80%, an authenticated Streamlit or Gradio interface, public deployment, RAGAS evaluation, cost analysis, and a one-page architecture decision record. Football law is a high-precision domain: exact terminology, exceptions, sanctions, and source authority matter.

## Decision

The core corpus contains **31 official IFAB sources** for the 2026/27 Laws of the Game and related protocols/guidance. Unofficial commentary is excluded. The build stores provenance in a manifest and pins normalized extracted-source hashes in `data/source_lock.json`; if the upstream source text changes, the audit fails rather than silently changing the corpus.

HTML is extracted with BeautifulSoup and PDFs with PyMuPDF. Metadata such as source ID, title, URL, section, season, and page number is retained. Chunking is structure-aware: IFAB headings, paragraphs, bullets, and PDF page boundaries are preserved, while long sections use approximately 600-token windows with 90-token overlap. This produced 1,031 chunks with a median of 103 tokens and a maximum of 609, reflecting the deliberately short legal/rule units in the source material.

Dense retrieval uses **BAAI/bge-small-en-v1.5** with normalized embeddings stored in **Chroma**. The model is compact, English-focused, and can run locally, avoiding recurring embedding API cost. Chroma was selected because the corpus is small, persistence and metadata filtering are straightforward, and an external vector service would add unnecessary operational complexity.

Retrieval is hybrid: **dense search + BM25 + Reciprocal Rank Fusion (RRF)**. Production reranking uses Cohere **`rerank-v4.0-pro`** over the fused candidate set. A local cross-encoder remains only as a credential-free CI baseline; on the fixed 30-question set it reached **93.3% Recall@5 (28/30)**, while BM25 reached 90.0%, dense 86.7%, and hybrid RRF 86.7%. The final Cohere Recall@5 is measured with the same golden set once the API secret is configured.

Generation uses the Cohere **Chat API** with `command-a-03-2025`, configurable through `COHERE_CHAT_MODEL`. The model is instructed to answer only from supplied IFAB evidence, cite retrieved sources, and abstain when evidence is insufficient. The Streamlit interface uses simple environment-variable authentication and exposes the answer, evidence, official source links, and response latency.

Deployment uses a reproducible Docker image on **Railway**. Dense embeddings remain local, while one `COHERE_API_KEY` powers production reranking, Command A generation, Cohere Embed v4 for RAGAS, and the Cohere evaluator LLM. The 20-question RAGAS workflow is manual to prevent accidental quota use.

## Consequences

The architecture prioritizes provenance, low recurring retrieval cost, and measurable retrieval quality. Trade-offs are a larger container image, model download/build time, and CPU reranking latency. The retrieval target is already exceeded by the local reranker baseline at 93.3% Recall@5; the credentialed Cohere production score is measured separately. Final submission completion still requires a successful public Railway URL, the 20-question RAGAS run using the student's API credentials, and feedback from three real users.
