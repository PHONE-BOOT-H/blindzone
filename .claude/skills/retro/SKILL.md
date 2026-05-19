---
name: retro
description: Use this skill after completing a feature, fixing a major bug, or finishing a milestone. Triggers on: "회고", "retro", "retrospective", "돌아보기", "마일스톤 완료", "기능 완성". Reviews what happened and improves the workflow.
---

# Retro — 작업 완료 후 회고

기능 완성 또는 마일스톤 완료 후 실행합니다.

## 회고 프로세스

### Step 1: 컨텍스트 수집
다음을 자동으로 조회:
- 이번 작업의 git log (커밋 목록, 변경 파일)
- 테스트 결과 요약
- 작업에 걸린 시간 (세션 기준)

### Step 2: 분석 질문
AskUserQuestion으로 확인:
1. 이번 작업에서 잘 된 점은?
2. 어렵거나 막혔던 부분은?
3. Claude가 잘못된 방향으로 간 순간이 있었는가?
4. 다음에 더 잘하려면 무엇을 바꿔야 하는가?

### Step 3: 개선 사항 도출
회고 결과를 바탕으로:

**CLAUDE.md 업데이트 제안:**
- 새로 발견한 규칙이나 패턴
- 피해야 할 접근법
- 추가할 Git 규칙

**새 Skill 제안:**
- 이번에 반복한 작업이 있으면 skill로 분리

**문서 업데이트:**
- ARCHITECTURE.md에 반영할 결정사항
- DECISION_LOG.md에 기록할 선택

### Step 4: 회고 기록 저장
`docs/RETRO_LOG.md`에 추가:

```markdown
## [날짜] — [기능/마일스톤 이름]

### 잘 된 것
- ...

### 어려웠던 것
- ...

### 개선 사항
- ...

### 다음에 적용할 것
- ...
```

### Step 5: 적용
확인된 개선 사항을 즉시 적용:
- CLAUDE.md 업데이트
- 새 skill 생성 (필요 시)
- docs 업데이트
