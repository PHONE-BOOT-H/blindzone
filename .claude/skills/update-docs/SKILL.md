---
name: update-docs
description: Use this skill after completing any feature implementation or significant change. Triggers on: "문서 업데이트", "docs update", "update documentation", "기능 완성 후", "커밋 전". Updates all relevant documentation and commits.
---

# Update Docs — 문서 업데이트 + 커밋

기능 구현 완료 후 실행합니다.

## 실행 단계

### Step 1: 변경 사항 파악
```bash
git diff --name-only HEAD
git log --oneline -5
```
어떤 파일이 변경됐는지 확인.

### Step 2: 문서 업데이트

**CHANGELOG.md 업데이트:**
```markdown
## [버전 or 날짜]
### Added
- [추가된 기능]
### Changed
- [변경된 동작]
### Fixed
- [수정된 버그]
```

**ARCHITECTURE.md 업데이트 (해당 시):**
- 새 컴포넌트/모듈 추가
- 데이터 흐름 변경
- 외부 의존성 추가

**PROJECT_SPEC.md 업데이트 (해당 시):**
- 완료된 milestone 체크
- 변경된 요구사항 반영

### Step 3: 코드 내 문서 확인
- 새 함수/클래스에 주석 필요한지 확인
- README 업데이트 필요한지 확인
- API 문서 업데이트 필요한지 확인

### Step 4: 커밋
```bash
git add [관련 파일들]
git commit -m "docs: update documentation for [기능명]"
```

### Step 5: 확인
AskUserQuestion: "문서 업데이트 완료. 추가로 업데이트할 내용이 있나요?"
