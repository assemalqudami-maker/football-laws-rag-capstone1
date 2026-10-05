# Railway Deployment Guide

Railway is the selected public deployment target for this project. The repository contains a production Dockerfile, so Railway can build directly from GitHub without a separate build service.

## Required Railway variables

Configure these as Railway service variables. Never commit real values to Git.

- `OPENAI_API_KEY` — required for answer generation.
- `OPENAI_MODEL` — optional; defaults to `gpt-6-luna`.
- `APP_USERNAME` — username for the simple demo login.
- `APP_PASSWORD` — password for the simple demo login.

Railway provides `PORT`; do not define it manually. The Docker start command reads Railway's `PORT` value and binds Streamlit to `0.0.0.0`.

## Repository source

Use this public GitHub repository:

`https://github.com/assemalqudami-maker/football-laws-rag-capstone1`

Railway automatically uses the root `Dockerfile` when it detects it in the connected repository.

## What the Docker build does

The production image:

1. installs CPU-only PyTorch and the lean runtime dependency set;
2. pre-caches the BGE embedding model and cross-encoder reranker;
3. validates the official IFAB manifest;
4. downloads the 31 official IFAB sources;
5. extracts and audits the corpus;
6. verifies normalized source hashes against `data/source_lock.json`;
7. creates the structure-aware chunks;
8. builds the local Chroma vector index;
9. starts the Streamlit application.

Raw IFAB source text and the generated vector store are created inside the deployment image and are not republished in the Git repository.

## Railway deployment steps

1. Create a Railway project.
2. Add a service from the GitHub repository above.
3. Add the required service variables.
4. Deploy.
5. After the deployment becomes healthy, open **Settings → Networking** and generate a public domain.
6. Test the domain from a browser session that is not signed into Railway.
7. Add the final public URL to `README.md` and `docs/submission_checklist.md`.

## RAGAS credentials

RAGAS is intentionally not executed during Railway deployment because it would consume the student's API budget on every rebuild.

For the required 20-question RAGAS report, add `OPENAI_API_KEY` as a GitHub Actions repository secret and manually run the **RAGAS evaluation** workflow once after retrieval is final.

## Deployment acceptance checklist

- [ ] Docker build succeeds.
- [ ] Railway service reaches a running/healthy state.
- [ ] Public domain opens without a Railway account.
- [ ] Correct credentials allow login.
- [ ] Incorrect credentials are rejected.
- [ ] Five representative football-law questions return answers.
- [ ] Retrieved evidence is visible.
- [ ] Official IFAB source links open correctly.
- [ ] One unsupported/out-of-scope question triggers an evidence-insufficient response rather than fabrication.
- [ ] No secret appears in repository files, deployment logs, or client-side output.
- [ ] Public URL is recorded in the README.
