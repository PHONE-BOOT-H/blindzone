"""라이브 사이트 시제품 캡처 → docs/submission/evidence/.

WebGL(deck.gl/maplibre) 렌더링을 위해 swiftshader + 충분한 대기.
실행: py -3.12 backend/scripts/capture_demo.py
"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[2] / "docs" / "submission" / "evidence"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://blindzone-brown.vercel.app"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        def shot(path, name):
            url = BASE + path
            print(f"  -> {url}", flush=True)
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(6)  # 지도 타일·deck.gl 레이어 렌더 대기
            page.screenshot(path=str(OUT / name), full_page=False)
            print(f"     saved {name}", flush=True)

        shot("/", "10_demo_main.png")            # 메인 지도 + TOP10
        shot("/about", "13_demo_about.png")       # About

        # 정책 시뮬레이터 — 옹진 인근 가상 거점 추가 후 결과 화면
        try:
            page.goto(BASE + "/policy", wait_until="networkidle", timeout=60000)
            time.sleep(3)
            ins = page.locator("input")
            ins.nth(0).fill("125.70")   # 경도
            ins.nth(1).fill("37.66")    # 위도
            page.get_by_role("button", name="추가").click()
            time.sleep(7)               # simulate 호출 + 지도/지표 렌더
            page.screenshot(path=str(OUT / "12_demo_policy.png"), full_page=True)
            print("     saved 12_demo_policy.png (옹진 거점 추가 결과)", flush=True)
        except Exception as e:
            print("     정책 거점추가 캡처 실패, 초기화면으로 대체:", str(e)[:70], flush=True)
            page.goto(BASE + "/policy", wait_until="networkidle"); time.sleep(4)
            page.screenshot(path=str(OUT / "12_demo_policy.png"))

        # 시민 모드 — 옹진군 선택 상세 + SHAP (전체 페이지)
        for label in ["옹진군", "인천 옹진군", "강원 인제군", "인제군"]:
            try:
                page.goto(BASE + "/", wait_until="networkidle", timeout=60000)
                time.sleep(3)
                page.select_option("select", label=label)
                time.sleep(5)
                fn = "11_demo_detail.png"
                page.screenshot(path=str(OUT / fn), full_page=True)
                print(f"     saved {fn} (선택: {label})", flush=True)
                break
            except Exception as e:
                print(f"     '{label}' 선택 실패: {str(e)[:60]}", flush=True)
        browser.close()
    print("완료:", OUT)


if __name__ == "__main__":
    main()
