"""
공공데이터 다운로드 가이드 + 가능한 자동화.
대부분 공공데이터포털은 로그인/신청 필요 → 수동 다운로드 후 data/raw/에 배치.
파일명은 아래 SOURCES 딕셔너리에 명시된 대로 저장.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATA_RAW  # noqa: E402

SOURCES = {
    "taas_다발지역.csv": {
        "url": "https://www.data.go.kr/data/15029185/standard.do",
        "desc": "전국교통사고다발지역표준데이터 (좌표 포함)",
        "method": "manual",
    },
    "taas_다발지역_api.json": {
        "url": "https://www.data.go.kr/data/15057467/openapi.do",
        "desc": "한국도로교통공단_지자체별 교통사고 다발지역 (오픈 API)",
        "method": "api_optional",
    },
    "응급의료기관.csv": {
        "url": "https://www.data.go.kr/data/15096291/standard.do",
        "desc": "전국응급의료기관표준데이터",
        "method": "manual",
    },
    "119_구급통계연보.xlsx": {
        "url": "https://www.data.go.kr/data/15139158/fileData.do",
        "desc": "소방청_119구급서비스 통계연보 (시도·시군구 단위)",
        "method": "manual",
    },
    "시군구_경계.geojson": {
        "url": "https://sgis.kostat.go.kr/view/board/boardList?cur_menu_no=0001",
        "desc": "통계청 SGIS 시군구 행정경계 (대안: VWORLD)",
        "method": "manual",
    },
}


def main():
    print("=" * 70)
    print("BlindZone 데이터 다운로드 가이드")
    print("=" * 70)
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    for filename, info in SOURCES.items():
        target = DATA_RAW / filename
        status = "OK" if target.exists() else "MISSING"
        print(f"\n[{status}] {filename}")
        print(f"  설명: {info['desc']}")
        print(f"  URL: {info['url']}")
        print(f"  방식: {info['method']}")
        print(f"  저장 경로: {target}")

    print("\n" + "=" * 70)
    print("수동 다운로드 후 다시 실행하면 [OK] 표시로 검증 가능.")
    print("=" * 70)


if __name__ == "__main__":
    main()
