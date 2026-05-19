# AI Coding Workflow Template

Claude Code와 Codex를 여러 프로젝트에서 일관되게 쓰기 위한 시작 템플릿입니다.
앱 코드가 아니라, 새 프로젝트를 만들 때 복사해서 쓰는 AI 작업 운영 폴더입니다.

## What This Gives You

- `CLAUDE.md`: Claude Code가 매 세션 읽는 프로젝트 메모리
- `AGENTS.md`: Codex가 따르는 작업 운영 지침
- `.claude/skills/`: 반복 워크플로를 slash skill로 분리
- `.claude/agents/`: 조사, 테스트, 리뷰, UI 검토용 subagent 정의
- `.claude/hooks/`: 위험 명령 차단과 자동 검증 hook
- `docs/`: 스펙, 아키텍처, 변경 이력, 회고, 의사결정 로그 템플릿

## Recommended Use

1. 새 프로젝트 폴더에 이 템플릿 파일들을 복사합니다.
2. `docs/PROJECT_SPEC.md`를 채우거나 Claude Code에서 `/spec-interview`를 실행합니다.
3. 스펙이 잡히면 `docs/ARCHITECTURE.md`를 작성합니다.
4. 기능 개발은 `/rpit` 또는 아래 프롬프트로 시작합니다.

```text
[기능 설명]을 구현해줘.
Research -> Plan -> Implement -> Test 순서로 진행해.
계획 단계에서 필요한 질문이 있으면 먼저 물어봐.
```

5. 기능 완료 후 `/code-review`, `/update-docs`, `/retro`를 순서대로 사용합니다.

## Claude Code Setup

Windows/PowerShell 기준으로는 예시 설정을 실제 설정으로 복사해서 시작합니다.

```powershell
Copy-Item .claude/settings.example.json .claude/settings.json
```

`.claude/settings.json`은 프로젝트에 맞게 조정하세요. 특히 `permissions.allow`, `permissions.ask`, `permissions.deny`는 팀이나 개인의 위험 허용 범위에 맞게 줄이는 것이 좋습니다.

## Hooks

기본 설정은 PowerShell hook을 사용합니다.

- `.claude/hooks/block-dangerous-bash.ps1`: `rm -rf`, `git reset --hard`, force push, 원격 스크립트 실행 같은 위험 명령을 차단합니다.
- `.claude/hooks/run-project-checks.ps1`: Claude Code 응답이 끝날 때 `typecheck`, `lint`, `test` 스크립트가 있으면 실행합니다.

Unix 계열 환경을 쓰는 경우 `.sh` 파일도 fallback으로 유지되어 있습니다. 이 경우 `.claude/settings.json`의 hook command를 `.sh`로 바꾸면 됩니다.

## Skills

주요 skill 흐름은 다음과 같습니다.

- `/spec-interview`: 프로젝트나 큰 기능의 요구사항을 인터뷰로 정리
- `/rpit`: Research -> Plan -> Implement -> Test 개발 루프
- `/tdd`: 테스트 먼저 작성하는 구현 루프
- `/code-review`: 병합 전 코드 리뷰
- `/update-docs`: 변경 후 문서 업데이트
- `/retro`: 작업 완료 후 회고와 개선점 기록
- `/whats-next`: 현재 상태 기준 다음 작업 추천
- `/screenshot-debug`: UI 스크린샷 기반 디버깅

## Docs Flow

- `docs/PROJECT_SPEC.md`: 무엇을 왜 만드는지
- `docs/ARCHITECTURE.md`: 시스템 구조와 설계 결정
- `docs/DECISION_LOG.md`: 중요한 결정과 이유
- `docs/CHANGELOG.md`: 변경 이력
- `docs/RETRO_LOG.md`: 회고와 다음 개선 사항
- `docs/AI_WORKFLOW_PLAYBOOK.md`: 전체 운영 방법
- `docs/PROMPT_PATTERNS.md`: 자주 쓰는 프롬프트

## Safety Notes

- production DB 변경, secret 수정, 대량 삭제, 권한 변경, CI/CD 변경은 자동 실행하지 않습니다.
- `dangerously-skip-permissions` 대신 설정 파일의 allow/ask/deny를 좁게 조정하는 쪽을 권장합니다.
- hook은 보조 안전장치입니다. 최종 책임은 Git, PR 리뷰, 테스트, 수동 확인으로 닫아야 합니다.

## When To Make A New Skill

같은 요청을 두 번 이상 반복하게 되면 `.claude/skills/` 또는 `.agents/skills/`에 skill로 빼는 것을 권장합니다.

예:

- 반복되는 기능 개발 절차
- 배포 전 체크리스트
- 특정 프레임워크의 코드 스타일
- 프로젝트 고유 리뷰 기준

## Template Status

이 repo는 계속 개선하는 운영 템플릿입니다. 각 실제 프로젝트에 적용할 때는 `PROJECT_SPEC.md`, `ARCHITECTURE.md`, hook command, permission rule을 프로젝트 상황에 맞게 줄이고 바꾸세요.
