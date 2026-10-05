FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python scripts/check_sources.py \
 && python scripts/collect_sources.py \
 && python scripts/extract_sources.py \
 && python scripts/audit_corpus.py \
 && python scripts/build_chunks.py \
 && python scripts/build_index.py

EXPOSE 7860

CMD ["sh", "-c", "streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-7860} --server.headless=true"]
