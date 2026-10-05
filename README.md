# Football Laws Referee RAG

A production-style Retrieval-Augmented Generation (RAG) capstone project focused on the **Laws of Association Football and refereeing**, using official IFAB sources and an English-only interface.

## Capstone target

This repository is being built from scratch to satisfy the Track B requirements:

1. **Domain and sources** — 20–50 high-quality documents and a documented domain.
2. **Ingestion** — reproducible loading, cleaning, chunking, embeddings, and vector storage with written architectural justification.
3. **Retrieval** — hybrid retrieval (dense + BM25), reranking, 30 golden questions, and Recall@5 >= 80%.
4. **Interface** — Streamlit UI with simple authentication and citations.
5. **Deployment and evaluation** — public deployment, RAGAS evaluation, cost analysis, and a one-page ADR.

## Domain

The system answers questions about football refereeing and the Laws of the Game. It is intended for referees, referee trainees, coaches, players, and fans who need grounded answers with traceable evidence.

The authoritative source family is **The International Football Association Board (IFAB)**. The initial corpus is English-only and targets the **2026/27** Laws of the Game plus current IFAB protocols and practical guidelines.

## Repository layout

```text
.
├── app/                  # Streamlit application
├── data/
│   ├── raw/              # Downloaded source snapshots (ignored by Git)
│   ├── processed/        # Cleaned/chunked data (ignored by Git)
│   ├── eval/             # Golden questions and evaluation outputs
│   └── sources_manifest.csv
├── docs/                 # ADR, cost analysis, reports
├── scripts/              # Collection, ingestion, retrieval, evaluation
├── tests/
├── domain.md
├── architecture.md
└── requirements.txt
```

## Source policy

The repository stores a manifest of official IFAB source URLs. The collector downloads snapshots locally for reproducible ingestion. Raw third-party source text is not committed to the public repository by default; only metadata, code, evaluation sets, and derived project artifacts are versioned.

## Current status

- [x] GitHub repository connected
- [x] Project initialized from scratch
- [x] English-only football refereeing domain defined
- [x] Initial official IFAB source manifest prepared
- [ ] Run source collection and validation
- [ ] Build chunking and ingestion pipeline
- [ ] Add dense retrieval + BM25 + reranking
- [ ] Build 30-question golden set and reach Recall@5 >= 80%
- [ ] Build Streamlit UI + authentication
- [ ] Run RAGAS
- [ ] Write cost analysis and ADR
- [ ] Deploy publicly

## Data provenance

All football-law content used by the RAG system must come from official IFAB pages or official IFAB publications listed in `data/sources_manifest.csv`. The system must answer from retrieved evidence and abstain when the corpus does not support an answer.

## Local setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python scripts/check_sources.py
python scripts/collect_sources.py
```

The next development step is to validate and collect the official source corpus, then build the ingestion pipeline.
