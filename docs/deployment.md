# Deployment Guide

The application is containerized and can be deployed to a Docker-capable Hugging Face Space or Railway service.

## Required secrets

Never commit secrets to Git. Configure these in the deployment platform:

- `OPENAI_API_KEY` — required for answer generation and RAGAS.
- `OPENAI_MODEL` — optional; defaults to `gpt-6-luna`.
- `APP_USERNAME` — demo login username.
- `APP_PASSWORD` — demo login password.

## What the image build does

The Docker build:

1. installs Python dependencies;
2. validates the official IFAB source manifest;
3. downloads the official source snapshots;
4. extracts and audits the corpus;
5. creates structure-aware chunks;
6. creates local BGE embeddings and a persistent Chroma index.

This makes the deployment reproducible without committing the downloaded IFAB text or local vector database to the public repository.

## Hugging Face Spaces

Create a new Space and select **Docker** as the SDK. Connect or push this GitHub repository to the Space, then define the required secrets in the Space settings. The container exposes port 7860 and starts Streamlit automatically.

After deployment, verify:

- the login screen appears;
- authentication rejects an incorrect password;
- at least five representative questions return answers;
- each answer exposes official IFAB evidence and source links;
- an unsupported question causes the system to abstain rather than invent a rule.

## Railway

Create a service from the GitHub repository. Railway should detect the Dockerfile. Add the required environment variables and deploy. The Docker command respects the platform `PORT` variable.

## Deployment acceptance checklist

- Public URL opens from a browser not signed into the developer account.
- Authentication works.
- Five golden questions return grounded answers.
- Source links open the official IFAB pages.
- No API key appears in logs, source code, or client-side HTML.
- The final live URL is added to `README.md`.
