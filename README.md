# Football Laws Referee RAG

A production-style Retrieval-Augmented Generation system for **association-football refereeing and the IFAB Laws of the Game**. The project is English-only and is deployed publicly for the Track B RAG capstone.

**Live demo:** https://football-laws-rag-production.up.railway.app

## What the system does

A user asks a football-law question. The system performs dense retrieval and BM25 keyword retrieval, fuses the results with Reciprocal Rank Fusion (RRF), reranks the candidates, and sends the strongest five pieces of IFAB evidence to an LLM. The answer is constrained to that evidence and displays its sources.

## Verified corpus

The automated corpus pipeline has successfully collected and extracted **31/31 official IFAB sources**:

- 31 English documents
- 29 HTML sources
- 2 PDF publications
- 71,191 extracted words
- 414,538 extracted characters
- 0 exact full-document duplicate groups
- 0 suspicious documents under 100 words

The source manifest is `data/sources_manifest.csv`. Normalized extracted-source hashes are pinned in `data/source_lock.json`, so upstream IFAB content drift is detected instead of silently changing the corpus. Raw IFAB snapshots and derived text are reproducibly collected but are not committed to this public repository.

## Architecture

```text
Official IFAB sources
        ↓
Validation + download + checksum
        ↓
HTML/PDF extraction + source metadata
        ↓
Section-aware chunking (~600 tokens, 90-token overlap)
        ↓
┌───────────────────┬──────────────────┐
│ BGE dense retrieval│ BM25 retrieval   │
└─────────┬─────────┴─────────┬────────┘
          └────── RRF fusion ─┘
                    ↓
           Cohere Rerank v4.0 Pro
                    ↓
               Top-5 evidence
                    ↓
        Grounded Cohere Command A
                    ↓
       Answer + official IFAB citations
```

Current retrieval components:

- Dense embedding model: `BAAI/bge-small-en-v1.5`
- Vector store: Chroma
- Lexical retrieval: BM25
- Fusion: RRF
- Production reranker: `rerank-v4.0-pro` via Cohere API
- Free CI baseline reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Generator: `command-a-03-2025` via Cohere API
- Interface: Streamlit
- Authentication: username/password from environment secrets

See `architecture.md` and `docs/ADR.md` for the decision rationale.

## Evaluation

The repository contains a fixed **30-question golden retrieval set**. The build resolves each human-authored evidence anchor to concrete chunk IDs before measuring Recall@5. Automated evaluation compares:

1. BM25
2. dense retrieval
3. hybrid dense + BM25 using RRF
4. hybrid + reranking

The required target is **Recall@5 >= 80%**. The credential-free local cross-encoder baseline already reaches **93.3% (28/30)**. The final production reranker is Cohere `rerank-v4.0-pro`; its Recall@5 is measured by the manual Cohere evaluation workflow after `COHERE_API_KEY` is configured. See `docs/retrieval_evaluation.md`.

A separate **20-question RAGAS** evaluation has been completed using Cohere Command A as the evaluator LLM and Cohere Embed v4 for embedding-dependent metrics. Final scores: **Faithfulness 0.9675**, **Answer Relevancy 0.7635**, **Mean RAGAS 0.8655**. See `docs/ragas_report.md`.

The production Docker build and Streamlit health check pass in GitHub Actions. The application is deployed on Railway at **https://football-laws-rag-production.up.railway.app**; the live service reports healthy and the Streamlit health endpoint returns HTTP 200.

## Repository layout

```text
.
├── app/
│   └── streamlit_app.py
├── data/
│   ├── eval/
│   └── sources_manifest.csv
├── docs/
│   ├── ADR.md
│   ├── cost_analysis.md
│   ├── deployment.md
│   └── user_testing.md
├── scripts/
│   ├── check_sources.py
│   ├── collect_sources.py
│   ├── extract_sources.py
│   ├── audit_corpus.py
│   ├── build_chunks.py
│   ├── label_gold_chunks.py
│   ├── build_index.py
│   ├── evaluate_recall.py
│   ├── summarize_retrieval.py
│   ├── ask.py
│   ├── run_ragas.py
│   └── cost_analysis.py
├── src/football_rag/
├── Dockerfile
├── domain.md
├── architecture.md
└── requirements.txt
```

## Local build

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python scripts/check_sources.py
python scripts/collect_sources.py
python scripts/extract_sources.py
python scripts/audit_corpus.py
python scripts/build_chunks.py
python scripts/label_gold_chunks.py
python scripts/build_index.py
python scripts/evaluate_recall.py --mode hybrid --reranker-provider local
```

Create a local `.env` from `.env.example`, but never commit your real API key.

To run the interface after building the index:

```bash
streamlit run app/streamlit_app.py
```

## Capstone status

- [x] Public GitHub repository
- [x] English-only football refereeing domain
- [x] 20–50 official sources (31 verified)
- [x] Reproducible source collection and corpus audit
- [x] Documented chunking / embedding / vector-store decisions
- [x] Hybrid dense + BM25 retrieval
- [x] RRF fusion and reranking
- [x] 30-question golden set and automated Recall@5 evaluation
- [x] Streamlit UI
- [x] Simple authentication
- [x] Docker deployment configuration
- [x] Production Docker image build + Streamlit health smoke test
- [x] One-page ADR
- [x] Cost analysis for 1K / 10K / 100K users
- [x] Local reranker baseline Recall@5 >= 80% — **93.3% (28/30)**
- [x] Measure final Recall@5 with Cohere `rerank-v4.0-pro` — **93.3% (28/30)**
- [x] Run 20-question RAGAS evaluation — **mean 0.8655**
- [x] Test with three real users
- [x] Deploy to Railway — **https://football-laws-rag-production.up.railway.app**

## Safety and scope

The application is educational. It does not replace IFAB, competition regulations, or the referee's authority in a real match. If retrieved evidence does not establish an answer, the generator is instructed to say so rather than guess.
