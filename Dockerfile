FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    RERANK_PROVIDER=cohere

WORKDIR /app

COPY requirements-deploy.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY . .

# Pre-cache the local BGE dense embedding model. Reranking and answer
# generation use Cohere at query time, so no local reranker is bundled.
RUN python scripts/cache_models.py

# Rebuild the pinned official IFAB corpus and local vector index.
RUN python scripts/check_sources.py \
 && python scripts/collect_sources.py \
 && python scripts/extract_sources.py \
 && python scripts/audit_corpus.py \
 && python scripts/build_chunks.py \
 && python scripts/build_index.py

EXPOSE 7860

CMD ["sh", "-c", "exec streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-7860} --server.headless=true"]
