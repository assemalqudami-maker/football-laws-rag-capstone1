# RAGAS Evaluation Report

**Evaluation date:** 5 October 2026  
**Evaluation set:** 20 fixed football-law questions  
**Provider:** Cohere  
**Generator:** `command-a-03-2025`  
**Evaluator LLM:** `command-a-03-2025`  
**Evaluation embeddings:** `embed-v4.0`

## Final scores

| Metric | Score |
|---|---:|
| Faithfulness | **0.9675** |
| Answer Relevancy | **0.7635** |
| Mean RAGAS score | **0.8655** |

## Interpretation

The system achieved very high faithfulness, indicating that generated answers were strongly grounded in the retrieved IFAB evidence. Answer relevancy was lower than faithfulness but remained solid overall, producing a combined mean score of **0.8655** across the 20-question evaluation set.

The same project also achieved **Recall@5 = 93.3% (28/30)** with Cohere Rerank v4.0 Pro on the fixed retrieval golden set.

## Reproducibility

The evaluation is implemented in:

- `data/eval/ragas_questions.json`
- `scripts/run_ragas.py`
- `.github/workflows/ragas-resume.yml`

The successful GitHub Actions run is:

`https://github.com/assemalqudami-maker/football-laws-rag-capstone1/actions/runs/37262017568`

The detailed JSON artifact was uploaded by the workflow as `ragas-report-resumed`.
