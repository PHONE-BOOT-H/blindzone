# Hugging Face Spaces — BlindZone FastAPI 백엔드 (Docker SDK)
# 런타임은 데이터 읽기 + XGBoost 추론만 (geopandas/shap는 사전계산용이라 불포함 → 가벼움)
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# 런타임 코드 + 사전계산 데이터·모델
COPY api ./api
COPY src ./src
COPY models ./models
COPY data/processed ./data/processed

# HF Spaces 기본 포트 7860
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
