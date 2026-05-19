---
name: controlled-randomness
description: Use this skill for creative tasks, design decisions, or when the user wants variety but within constraints. Triggers on: "창의적으로", "다양하게", "여러 옵션", "아이디어 내줘", "alternatives". Generates controlled creative options within defined boundaries.
---

# Controlled Randomness — 제어된 창의성

창의적 옵션을 제시할 때 사용합니다.
무작위가 아니라, 명확한 제약 조건 안에서 다양성을 만듭니다.

## 실행 단계

### Step 1: 제약 조건 파악
AskUserQuestion으로 확인:
- 반드시 지켜야 할 것은? (non-negotiable)
- 선호하는 방향은?
- 피해야 할 것은?
- 몇 가지 옵션을 원하는가?

### Step 2: 기준 축 정의
창의적 옵션을 다음 축으로 분류:
- 보수적 ↔ 실험적
- 단순 ↔ 복잡
- 빠름 ↔ 완성도

### Step 3: 옵션 생성
각 축을 기준으로 옵션 생성:

```markdown
## 옵션 A — 보수적/안전한 선택
[설명, 장단점, 예시]

## 옵션 B — 균형잡힌 선택 (추천)
[설명, 장단점, 예시]

## 옵션 C — 실험적/대담한 선택
[설명, 장단점, 예시]
```

### Step 4: 추천 및 이유 설명
- 각 옵션의 장단점 명확히 설명
- 현재 상황에 가장 맞는 옵션 추천 (이유 포함)
- 사용자의 선택 존중

### Step 5: 선택 기반 실행
사용자가 선택한 옵션으로 진행.
취향/판단이 필요한 부분은 자동 반복(loop) 금지.
