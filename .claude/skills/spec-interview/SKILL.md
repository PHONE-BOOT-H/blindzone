---
name: spec-interview
description: Use this skill when starting a new project or major feature, or when the user says "스펙 만들어", "기획서", "요구사항 정리", "project spec", "what should I build". Interviews the user to create a complete PROJECT_SPEC.md.
---

# Spec Interview — 프로젝트 스펙 인터뷰

새 프로젝트나 큰 기능을 시작할 때 사용합니다.

## 인터뷰 프로세스

AskUserQuestion을 사용해 다음 질문들을 순서대로 진행하세요.
한 번에 1-2개 질문씩, 답변을 받으면 다음 질문으로.

### 제품 요구사항 (Product Requirements)
1. 이 프로젝트/기능으로 해결하려는 문제가 무엇인가?
2. 주요 사용자는 누구이고, 그들이 원하는 것은?
3. 핵심 기능 3가지를 꼽는다면?
4. MVP(최소 기능 제품)에 포함될 것과 제외될 것은?
5. 성공은 어떻게 측정하는가?

### 엔지니어링 요구사항 (Engineering Requirements)
6. 사용할 기술 스택은? (언어, 프레임워크, DB)
7. 기존 시스템과 통합이 필요한가?
8. 성능 요구사항이 있는가? (응답 속도, 동시 사용자 수 등)
9. 보안/인증 요구사항은?
10. 배포 환경은? (클라우드, 서버, 로컬)

### 마일스톤
11. 언제까지 MVP를 완성해야 하는가?
12. 이후 버전에서 추가할 기능은?

## 결과물 생성

인터뷰 완료 후 `docs/PROJECT_SPEC.md`를 다음 구조로 작성:

```markdown
# Project Spec: [프로젝트명]

## 문제 정의
## 목표 사용자
## 핵심 기능
## MVP 범위
## 제외 범위
## 성공 지표
## 기술 스택
## 아키텍처 개요
## 마일스톤
  - MVP
  - v1.0
  - v2.0
## 미결 사항
```

작성 후 GitHub issue로 분해할지 물어보세요.
