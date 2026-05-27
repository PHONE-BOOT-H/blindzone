# backend/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="BlindZone API",
    description="사고 위험 × 응급 사각지대 분석 API (탐색형 surrogate)",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    """루트 안내 — 심사 중 직접 접속 시 서비스 상태/엔드포인트 표시."""
    return {
        "service": "BlindZone API",
        "status": "ok",
        "frontend": "https://blindzone-brown.vercel.app",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": ["/api/features", "/api/features/{sgg_code}", "/api/top10",
                      "/api/contrast", "/api/simulate"],
    }
