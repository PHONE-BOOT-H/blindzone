---
name: rpit
description: Use this skill when building any new feature, fixing a bug, or implementing a change. Triggers on: "기능 만들어", "구현해", "추가해", "수정해", "feature", "implement", "build". Runs the full Research → Plan → Implement → Test loop.
---

# RPIT — 기능 개발 루프

모든 기능 개발의 표준 워크플로입니다.

## 실행 순서

### Phase 1: Research (조사)
큰 기능이거나 새 기술/API가 필요한 경우:
1. 필요한 라이브러리, API, 패턴을 웹에서 조사
2. `docs/research-<feature-name>.md`에 조사 결과 저장
3. 조사 내용: 옵션 비교, 추천 접근법, 주의사항

작은 기능이면 생략 가능.

### Phase 2: Plan (계획) — `/ultraplan` 사용
1. `/ultraplan`을 실행해서 깊은 계획 수립
2. ultraplan이 AskUserQuestion으로 다음을 확인:
   - 정확히 무엇을 만드는가?
   - 성공 기준은 무엇인가?
   - 어떤 파일/모듈이 영향받는가?
   - 선호하는 접근법이 있는가?
3. ultraplan이 작업을 단계로 분해하고 계획서 제출
4. 사용자가 계획 검토 및 승인 후 구현 시작

### Phase 3: Implement (구현)
1. 테스트 먼저 작성 (TDD)
2. 테스트가 통과할 만큼만 구현
3. 작은 단위로 커밋
4. 복잡한 부분은 주석으로 "왜"를 설명

### Phase 4: Test (검증)
1. 단위 테스트 실행
2. 통합 테스트 실행
3. 수동 검증 (필요 시 Playwright로 브라우저 자동화)
4. 성공 기준 달성 확인

## 완료 후
- `/update-docs` skill로 문서 업데이트
- `/retro` skill로 회고 실행
- GitHub issue 닫기 (해당하는 경우)
