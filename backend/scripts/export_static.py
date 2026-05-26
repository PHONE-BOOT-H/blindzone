"""API 응답을 정적 JSON으로 export → frontend/public/data/.

백엔드(Railway)가 cold start·다운되어도 프론트(Vercel)가 정적 JSON으로
지도·위험지수·SHAP·대조를 보여줄 수 있게 fallback 데이터를 생성한다.
TestClient로 실제 API 응답을 그대로 저장하므로 스키마가 100% 일치한다.

실행: py -3.12 backend/scripts/export_static.py
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient  # noqa: E402
from api.main import app  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "frontend" / "public" / "data"
OUT.mkdir(parents=True, exist_ok=True)

client = TestClient(app)


def save(name, obj):
    p = OUT / f"{name}.json"
    p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    print(f"  saved {p.name} ({p.stat().st_size:,} bytes)")


def main():
    # 헬스 체크 (데이터 로드 확인)
    h = client.get("/api/health").json()
    print(f"[health] {h}")

    features = client.get("/api/features").json()
    save("features", features)
    save("top10", client.get("/api/top10").json())
    save("contrast", client.get("/api/contrast").json())

    # 시군구별 상세(SHAP 포함) — sgg_code -> detail 맵
    details = {}
    for f in features:
        code = f["sgg_code"]
        details[code] = client.get(f"/api/features/{code}").json()
    save("details", details)
    print(f"  details: {len(details)}개 시군구")

    # 사전계산 시뮬 예시 (백엔드 없이도 What-if 데모 가능하게)
    examples = {
        # 인제 인근 가상 거점 (case-study 좌표)
        "inje": client.post("/api/simulate",
                            json={"virtual_ems": [[128.17, 38.06]]}).json(),
        # 옹진 인근 가상 거점
        "ongjin": client.post("/api/simulate",
                              json={"virtual_ems": [[125.70, 37.66]]}).json(),
    }
    save("simulate_examples", examples)
    print("완료. frontend/public/data/ 에 fallback JSON 생성됨.")


if __name__ == "__main__":
    main()
