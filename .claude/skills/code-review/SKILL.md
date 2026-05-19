---
name: code-review
description: Use this skill before merging any PR, after implementing a feature, or when the user says "코드 리뷰", "review", "PR 리뷰", "검토". Reviews code for correctness, security, performance, and maintainability.
---

# Code Review — 코드 리뷰 워크플로

## 리뷰 범위

```bash
# 변경된 파일 파악
git diff main...HEAD --name-only

# 변경 내용 확인
git diff main...HEAD
```

## 리뷰 체크리스트

### 1. 정확성 (Correctness)
- [ ] 요구사항을 정확히 구현했는가?
- [ ] 엣지 케이스를 처리했는가?
- [ ] 에러 핸들링이 적절한가?
- [ ] 모든 테스트가 통과하는가?

### 2. 보안 (Security)
- [ ] SQL injection 취약점 없는가?
- [ ] XSS 취약점 없는가?
- [ ] API key / secret이 하드코딩되지 않았는가?
- [ ] 입력값 검증이 있는가?
- [ ] 권한 확인이 올바른가?

### 3. 성능 (Performance)
- [ ] 불필요한 DB 쿼리가 있는가?
- [ ] N+1 쿼리 문제가 있는가?
- [ ] 메모리 누수 가능성이 있는가?
- [ ] 캐싱이 필요한 부분이 있는가?

### 4. 유지보수성 (Maintainability)
- [ ] 함수/변수 이름이 명확한가?
- [ ] 함수가 너무 길지 않은가? (50줄 초과 주의)
- [ ] 중복 코드가 있는가?
- [ ] 복잡한 로직에 주석이 있는가?
- [ ] 타입이 명확한가?

### 5. 테스트 (Testing)
- [ ] 새 기능에 테스트가 있는가?
- [ ] 테스트가 의미 있는가? (단순 통과용이 아닌)
- [ ] 기존 테스트가 깨지지 않는가?

## 리뷰 결과 출력

```markdown
## 코드 리뷰 결과

### 승인 (Approve) / 수정 필요 (Request Changes)

### 필수 수정 사항
- ...

### 권장 개선 사항
- ...

### 잘 된 부분
- ...
```

수정이 필요한 경우 자동으로 수정할지 AskUserQuestion으로 확인.
