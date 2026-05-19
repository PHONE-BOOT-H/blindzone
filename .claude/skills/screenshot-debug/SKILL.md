---
name: screenshot-debug
description: Use this skill when the user pastes a screenshot of a UI bug, error, or visual issue. Triggers on: image input, "스크린샷", "화면 오류", "UI 버그", "이렇게 나와", "screenshot". Analyzes the visual and diagnoses the issue.
---

# Screenshot Debug — 스크린샷 기반 디버깅

## 분석 프로세스

### Step 1: 스크린샷 분석
이미지를 보고 다음을 파악:
- 어떤 UI 요소가 문제인가?
- 에러 메시지가 있는가? 정확한 텍스트는?
- 레이아웃/스타일 문제인가?
- 데이터 표시 문제인가?
- 콘솔 에러가 보이는가?

### Step 2: 문제 진단
문제 유형별 접근:

**에러 메시지인 경우:**
- 에러 텍스트 전체 파악
- 스택 트레이스 확인
- 관련 코드 위치 탐색

**레이아웃 문제인 경우:**
- CSS/스타일 파일 확인
- 반응형 문제인지 확인
- 브라우저 호환성 문제인지 확인

**데이터 문제인 경우:**
- API 응답 확인
- 상태 관리 확인
- 렌더링 로직 확인

### Step 3: 원인 특정
```
관련 파일 읽기 → 문제 코드 위치 파악 → 수정 계획 수립
```

### Step 4: 수정
- 수정 계획을 사용자에게 설명
- 승인 후 수정 진행
- 수정 후 테스트

### Step 5: 확인
- 수정 후 동일한 시나리오 재현 가능한지 확인
- 관련 테스트 추가 (회귀 방지)
