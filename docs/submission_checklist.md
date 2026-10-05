# Capstone Submission Checklist

**Supervisor:** Dr. Yousif Alyousifi  
**Track:** B — Complete RAG System  
**Project:** Football Laws Referee RAG  
**Language:** English

## Required submission items

| Required item | Status | Evidence |
|---|---|---|
| 1. Public GitHub repository link | Complete | https://github.com/assemalqudami-maker/football-laws-rag-capstone1 |
| 2. Live demo URL | Pending deployment | Add Railway public domain after deployment |
| 3. ADR — one page | Complete | `docs/ADR.md` |
| 4. RAGAS score on 20 questions | Pending credentialed run | `data/eval/ragas_questions.json` + `scripts/run_ragas.py` |
| 5. Cost analysis — 1K / 10K / 100K users | Complete | `docs/cost_analysis.md` |

## Stage requirements

### Stage 1 — Domain and sources

- [x] Domain defined in `domain.md`
- [x] 31 official IFAB sources
- [x] English-only corpus
- [x] Public GitHub repository
- [x] Reproducible collection
- [x] Source-content lock to detect upstream drift

### Stage 2 — Ingestion

- [x] HTML/PDF extraction
- [x] Structure-aware chunking
- [x] Written chunking justification
- [x] Local embedding model selected and justified
- [x] Chroma selected and justified
- [x] 1,031 chunks in measured build

### Stage 3 — Retrieval

- [x] BM25
- [x] Dense retrieval
- [x] Hybrid RRF
- [x] Cross-encoder reranking
- [x] 30 golden questions
- [x] Recall@5 measured
- [x] **Recall@5 = 93.3% (28/30)** with hybrid + reranking

### Stage 4 — Interface

- [x] Streamlit UI
- [x] Simple authentication
- [x] English interface
- [x] Evidence and official source links
- [ ] Test with three real users

### Stage 5 — Deploy and submit

- [x] Docker deployment configuration
- [x] One-page ADR
- [x] Cost-analysis model and report
- [x] 20-question RAGAS set and runner
- [ ] Run RAGAS with the student's API credentials
- [ ] Deploy to Railway
- [ ] Generate public Railway domain
- [ ] Complete three real-user tests
- [ ] Add live URL and final RAGAS score to README
