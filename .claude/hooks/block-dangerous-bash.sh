#!/bin/bash
# block-dangerous-bash.sh
# PreToolUse hook — 위험한 bash 명령 실행 전 차단
#
# Claude Code settings.json에 등록 방법:
# "hooks": {
#   "PreToolUse": [{
#     "matcher": "Bash",
#     "hooks": [{"type": "command", "command": "bash .claude/hooks/block-dangerous-bash.sh"}]
#   }]
# }

# stdin에서 tool input JSON 읽기
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print((d.get('tool_input') or {}).get('command') or d.get('command',''))" 2>/dev/null)

# 위험 패턴 목록
DANGEROUS_PATTERNS=(
    "rm -rf"
  "Remove-Item.*-Recurse"
  "Remove-Item.*-Force"
  "git reset --hard"
  "git push --force"
  "git push -f"
  "DROP TABLE"
  "DROP DATABASE"
  "chmod 777"
  "chmod "
  "sudo rm"
  "npm publish"
  "> /dev/null 2>&1 &"  # 백그라운드 숨김 실행
  "curl.*| bash"         # 원격 스크립트 실행
  "curl.*| sh"
  "wget.*| bash"
  "wget.*| sh"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qi "$pattern"; then
    # 차단 — 공식 PreToolUse JSON 형식으로 차단
    python3 - <<PY
import json
print(json.dumps({
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Dangerous command blocked: '$pattern'. Ask the user before running it."
  }
}, ensure_ascii=False))
PY
    exit 0
  fi
done

# 통과
exit 0
