# Cohere API Setup

The project is now configured to use one Cohere API key for three credentialed parts of the capstone:

1. **Production reranking** — `rerank-v4.0-pro`
2. **Answer generation** — `command-a-03-2025`
3. **RAGAS evaluation** — Command A evaluator + `embed-v4.0`

The dense vector index still uses the local BGE embedding model, so the corpus can be built and the free retrieval baseline can be tested without consuming Cohere quota.

## 1. GitHub Actions secret — required next

Add the key as a repository secret:

**Repository → Settings → Secrets and variables → Actions → New repository secret**

Name:

```text
COHERE_API_KEY
```

Value: paste the Cohere API key itself.

Do not add the key to a repository file, README, issue, commit, or chat message.

After the secret is present, manually run:

**Actions → Cohere RAGAS evaluation → Run workflow**

That workflow first runs `scripts/check_cohere.py` to test Chat, Rerank, and Embed with very small requests. Only if those checks succeed does it continue to:

- 30-question Recall@5 with Cohere Rerank v4.0 Pro;
- 20-question RAGAS evaluation.

## 2. Railway variable — required at deployment

When the Railway service is created, add:

```text
COHERE_API_KEY=<secret>
COHERE_CHAT_MODEL=command-a-03-2025
COHERE_RERANK_MODEL=rerank-v4.0-pro
RERANK_PROVIDER=cohere
APP_USERNAME=<your-demo-username>
APP_PASSWORD=<your-demo-password>
```

Do not set `PORT`; Railway supplies it.

## 3. Local development

Copy `.env.example` to `.env`, paste the key into the local `.env`, and keep that file out of Git.

## Why the key is not needed during ordinary CI

The automatic retrieval workflow uses the local cross-encoder baseline. This allows code and retrieval regressions to be checked without API quota. The final credentialed measurements use Cohere and are run manually only when intended.
