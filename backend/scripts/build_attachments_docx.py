"""별첨 DOCX 생성 → 바탕화면. (AI 활용 증빙 / 시제품 포트폴리오)

그림이 삽입된 제출용 초안. Claude Code 대화 캡처만 본인이 추가하면 완성.
실행: py -3.12 backend/scripts/build_attachments_docx.py
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn


def set_kfont(doc, font="맑은 고딕"):
    """문서 기본 스타일에 한글 폰트 지정(기본 Calibri는 한글 글리프 없어 깨짐)."""
    for name in ["Normal", "Title", "Heading 1", "Heading 2", "Light Grid Accent 1"]:
        try:
            st = doc.styles[name]
        except KeyError:
            continue
        st.font.name = font
        rpr = st.element.get_or_add_rPr()
        rf = rpr.get_or_add_rFonts()
        rf.set(qn("w:ascii"), font)
        rf.set(qn("w:hAnsi"), font)
        rf.set(qn("w:eastAsia"), font)

ROOT = Path(__file__).resolve().parents[1].parent
EV = ROOT / "docs" / "submission" / "evidence"
DESK = Path(os.path.expanduser("~")) / "Desktop"


def caption(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)


def pic(doc, name, width=6.2):
    f = EV / name
    if f.exists():
        doc.add_picture(str(f), width=Inches(width))


# ───────────── 1) AI 활용 증빙 ─────────────
d = Document()
set_kfont(d)
d.add_heading("AI 활용 증빙 — BlindZone", 0)
d.add_paragraph("2026 국토교통 데이터 활용 경진대회 / 가점(AI 학습도구·AI 분석도구) 증빙자료")
d.add_paragraph("라이브: https://blindzone-brown.vercel.app  ·  코드: https://github.com/PHONE-BOOT-H/blindzone")

d.add_heading("1. AI 분석도구 — XGBoost + SHAP", level=1)
d.add_paragraph(
    "정의한 잠재 위험지수를 XGBoost 회귀로 학습(재현도 R²=0.90, MAE=0.0079)하고, "
    "SHAP TreeExplainer로 지역별로 어떤 요인이 위험지수를 끌어올렸는지 설명했다. "
    "사고·사망 예측이 아니라, 정의식의 기여요인을 분해하는 설명 레이어로 활용했다.")
pic(d, "01_xgboost_feature_importance.png")
caption(d, "[그림1] XGBoost 변수 중요도(gain) — 사고 건수·응급기관 거리가 상위 기여")
pic(d, "02_shap_summary.png")
caption(d, "[그림2] SHAP 요약 — 응급기관 거리(ems_distance_km)가 위험지수의 핵심 요인")
pic(d, "03_shap_bar.png")
caption(d, "[그림3] 변수별 평균 기여도(mean |SHAP value|)")
pic(d, "04_shap_inje_waterfall.png")
caption(d, "[그림4] 인제군 위험지수의 변수별 SHAP 분해 — 응급거리 기여 최대")
d.add_paragraph("코드: backend/src/train.py(학습), backend/scripts/precompute_shap.py(SHAP). "
                "서비스 반영: 시민 모드에서 시군구 클릭 시 '왜 위험한가'로 표출.")

d.add_heading("2. AI 학습도구 — Claude Code", level=1)
d.add_paragraph(
    "코드 작성·수정·디버깅·배포 전 과정에서 Claude Code(Anthropic)를 보조 도구로 활용했다. "
    "모든 커밋 메시지에 'Co-Authored-By: Claude Opus'를 명시해 기여를 투명하게 기록했다. "
    "단순 검색이 아니라 실제 코드·문서·분석 산출물 생성에 직접 사용했다. "
    "(총 74개 커밋 중 Co-Authored-By: Claude 명시 16건)")
tbl = d.add_table(rows=1, cols=2)
tbl.style = "Light Grid Accent 1"
tbl.rows[0].cells[0].text = "커밋"
tbl.rows[0].cells[1].text = "내용"
rows = [
    ("08a56a1", "외부검증·도로 실거리 robust 재산출 + 가점표현 정직화"),
    ("84d3845", "레버1·4 — 고령 수요 교차분석 + 수혜인구"),
    ("68a5a76", "다발지점 vs 전체 교통사고 대조 분석"),
    ("f08ee6b", "정적 fallback + 배포 — 백엔드 다운 시에도 데모 동작"),
    ("3ea4a71", "HF Spaces Docker 설정 + 배포"),
    ("3754f3d", "About 페이지 공개용 재작성"),
]
for h, t in rows:
    c = tbl.add_row().cells
    c[0].text = h
    c[1].text = t
d.add_paragraph("활용 영역: Next.js 지도 UI·정적 fallback, FastAPI 엔드포인트, HF Spaces "
                "배포(Dockerfile), 분석 스크립트(가중치 민감도·OSRM 실거리·SHAP) 등. "
                "데이터셋 선택·지표 설계·발견 해석·정직성 표현은 사람이 직접 결정.")
d.add_paragraph("")
p = d.add_paragraph()
p.add_run("[직접 추가] Claude Code 대화 화면 캡처 1~2장(질문→생성 코드→실제 반영), "
          "GitHub 커밋 상세에 Co-Authored-By 줄이 보이는 캡처 1장.").bold = True

out1 = DESK / "BlindZone_AI활용증빙.docx"
d.save(str(out1))
print("saved:", out1)


# ───────────── 2) 시제품 포트폴리오 ─────────────
d2 = Document()
set_kfont(d2)
d2.add_heading("시제품 포트폴리오 — BlindZone", 0)
d2.add_paragraph("2026 국토교통 데이터 활용 경진대회 / 제품·서비스 개발 분야 별첨")
d2.add_paragraph("라이브: https://blindzone-brown.vercel.app  ·  백엔드: "
                 "https://hananhan-blindzone-backend.hf.space  ·  코드: github.com/PHONE-BOOT-H/blindzone")

shots = [
    ("10_demo_main.png", "화면 1 — 메인: 전국 위험지도 + TOP10",
     "전국 252개 시군구 잠재 위험지수. 상위는 대부분 대도시(이미 알려진 사고다발지)."),
    ("11_demo_detail.png", "화면 2 — 시군구 상세 + '왜 위험한가'(SHAP)",
     "옹진군 선택 화면: 다발지점 사고 0건이나 응급거리 75.3km. SHAP가 응급 접근성을 핵심 "
     "요인으로 설명. 사각지대 대조·TOP10도 함께 표시."),
    ("12_demo_policy.png", "화면 3 — 정책 시뮬레이터",
     "가상 응급거점 추가 시 최근접 거리 재계산 → 위험지수 변화(평균·최대 감소·개선 시군구 수). "
     "정책효과 예측이 아닌 거리 기반 접근성 민감도 분석."),
    ("13_demo_about.png", "화면 4 — 서비스 소개(About)",
     "무엇을 푸는지·어떻게 찾는지·다섯 가지 검증·한계를 일반 사용자도 이해하게 정리."),
]
for fn, title, desc in shots:
    d2.add_heading(title, level=1)
    d2.add_paragraph(desc)
    pic(d2, fn)
    d2.add_paragraph("")

d2.add_heading("기술 구성", level=1)
d2.add_paragraph("프론트엔드: Next.js 14 + MapLibre GL + deck.gl (Vercel) / "
                 "백엔드: FastAPI + XGBoost + SHAP (Hugging Face Spaces, Docker). "
                 "백엔드 일시 중단 시에도 정적 스냅샷으로 핵심 화면이 동작하도록 설계.")

out2 = DESK / "BlindZone_시제품포트폴리오.docx"
d2.save(str(out2))
print("saved:", out2)
print("완료")
