# CLAUDE.md — molit-2026

이 파일은 Claude Code가 매 세션마다 자동으로 읽는 프로젝트 컨텍스트입니다.

---

## 프로젝트 개요

- **무엇**: 2026 국토교통 데이터 활용 경진대회 출품작 (제품/서비스 트랙). 국토·교통 분야 공공데이터를 활용한 앱·웹 시제품 개발.
- **목적/맥락**: 국토교통부 주최 경진대회 입상 목표. 총상금 3,400만원 / 10건 시상. 가점 항목으로 AI 활용(최대 10점), 데이터융합·가명정보결합·안심구역(각 5점) 존재. K-MaaS 특별상 트랙은 본인 의사로 제외 — 일반(대상/우수상) 트랙 타깃.
- **마감/일정**: 2026-05-29 접수 마감 (D-10 / 오늘 2026-05-19 기준). 1차 심사 5~6월, 멘토링·2차 심사 6~7월, 최종발표·시상 7월.
- **팀/혼자**: 혼자 (1인 출품)
- **기타**: 한태영은 교통시스템공학과 재학. 직감 좋고 신기술 빨리 흡수하는 편. 가용시간 많음. 파주시 AI 공모전 등 경진대회 출품 경험 다수. 아이디어는 아직 미정 — 셋업 후 브레인스토밍 필요. 원본 대회 문서: `대회정보.txt`, `2026경진대회_기획서(최종).pdf`.

상세는:
- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) — 살아있는 스펙
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) — 지금 어디까지 왔는지

---

## 한태영 작업 스타일 (필수)

- **한국어로 대화**
- **AskUserQuestion 양식 회피** — 자유 텍스트 대화 선호
- **산출물에 이모지 X** — "AI 쓴 티" 안 나게 자연스럽게
- **간결한 응답** 선호 — 핵심부터, 불필요한 요약 X

---

## 핵심 작업 원칙

### 1. 큰 결정 전에 멈추기

다음 상황에서는 **반드시 한태영에게 확인** 후 진행:
- 아키텍처/기술스택 결정 (새 라이브러리, 새 도구 도입)
- 데이터 스키마 변경
- 외부 서비스 연동 방식 (API, DB, 외부 도구)
- 비용 발생 결정 (API 호출 비용, 유료 도구)
- 협업자에게 영향 가는 변경

확인 형식: 자유 텍스트로 충분.

### 2. 작업 흐름

- **코드 작업**: Research → Plan → Implement → Test 4단계 권장
  - 큰 작업이면 먼저 계획 세우고 한태영 확인 후 진행
- **비-코드 작업** (조사·인터뷰·발표자료·문서): 정보 수집 → 정리 → 산출물 작성 → 리뷰
- 어떤 워크플로/도구(skill 등)가 도움될 것 같으면 Claude가 먼저 제안. 한태영이 OK 해야 사용.

### 3. 컨텍스트 관리

- 새 작업 시작 시 `/clear`로 컨텍스트 초기화 권장
- 컨텍스트 사용량 70% 이상이면 새 세션
- 세션 끝낼 때 `docs/CURRENT_STATE.md` 업데이트 (다음 세션이 이어받기 위해)

### 4. 새 세션 시작 시 읽는 순서

1. `CLAUDE.md` (이 파일)
2. **`docs/CURRENT_STATE.md`** ← 가장 중요 (어디서 이어갈지)
3. 필요시 `docs/PROJECT_SPEC.md`, `docs/CHANGELOG.md`, `docs/DECISION_LOG.md`

→ 그래서 한태영이 "ㄱㄱ"만 해도 어디부터 이어갈지 안다.

---

## 위험 명령 — 반드시 확인

자동 실행 금지, 먼저 확인:

### 파일/저장소
- `rm -rf` (폴더 통째 삭제)
- `git reset --hard` (커밋 이력 강제 변경)
- `git push --force` (다른 작업 덮어쓸 수 있음)

### 보안/개인정보
- API key, secret, `.env` 파일 수정/공개
- 개인정보 포함 데이터를 외부 서비스에 전송

### 비용 발생
- 외부 API 대량 호출
- 유료 도구/서비스 가입

### 시스템
- 권한 상승 (`sudo`, `chmod 777`)
- 외부 데이터셋 대량 다운로드 전 사이즈/라이센스 확인

---

## 사용 가능한 Skill

`.claude/skills/` 안 슬래시 커맨드. 자주 쓰는 작업을 `/이름`으로 호출.

- `/spec-interview` — `docs/PROJECT_SPEC.md` 채울 때 인터뷰
- `/method-first` — "어떻게 하는 게 좋은지" 모를 때 방법론 조사
- `/controlled-randomness` — 디자인/접근법 결정할 때 옵션 제시
- `/rpit` — Research → Plan → Implement → Test 코드 루프
- `/code-review` — 큰 변경 전 리뷰
- `/update-docs` — 기능 완료 후 문서 갱신 + 커밋
- `/retro` — 마일스톤 회고
- `/whats-next` — 다음 할 일 막혔을 때
- `/screenshot-debug` — UI 스크린샷 기반 디버깅

> 같은 작업이 반복되면 Claude가 새 skill 만들 것을 제안.

---

## 관련 문서

- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) — 살아있는 스펙
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) — 현재 진행 상황 (세션 인수인계)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 시스템 구조 (코드 프로젝트일 때)
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — 변경 이력
- [docs/DECISION_LOG.md](docs/DECISION_LOG.md) — 주요 결정 기록
- [docs/RETRO_LOG.md](docs/RETRO_LOG.md) — 마일스톤 회고
