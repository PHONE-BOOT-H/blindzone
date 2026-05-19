---
name: whats-next
description: Use this skill when the user asks what to work on next, or when finishing a task and planning next steps. Triggers on: "다음 뭐해", "what's next", "다음 작업", "할 일", "우선순위". Analyzes project state and recommends next task.
---

# What's Next — 다음 작업 추천

현재 프로젝트 상태를 분석하고 다음에 할 일을 추천합니다.

## 분석 단계

### Step 1: 현재 상태 파악
```bash
# 미완성 브랜치 확인
git branch -a

# 최근 커밋 확인
git log --oneline -10

# 변경된 파일 확인
git status
```

### Step 2: GitHub Issues 확인 (gh CLI 사용 시)
```bash
gh issue list --label "priority" --state open
gh issue list --state open --limit 10
```

### Step 3: 프로젝트 스펙 확인
- `docs/PROJECT_SPEC.md`의 마일스톤 진행 상황
- 완료된 기능 vs 미완성 기능

### Step 4: 추천 생성
다음 기준으로 우선순위 결정:
1. **블로킹 버그** — 다른 작업을 막는 것
2. **마일스톤 크리티컬** — 현재 마일스톤 완성에 필요한 것
3. **높은 가치 낮은 노력** — 임팩트 대비 쉬운 것
4. **기술 부채** — 미루면 더 커지는 것

### Step 5: 제안 출력
```markdown
## 다음 작업 추천

### 즉시 해야 할 것 (Priority 1)
- [ ] ...

### 이번 마일스톤 내 (Priority 2)
- [ ] ...

### 다음 마일스톤 (Priority 3)
- [ ] ...
```

AskUserQuestion으로 어떤 작업을 시작할지 확인.
