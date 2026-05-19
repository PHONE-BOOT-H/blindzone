#!/bin/bash
# run-project-checks.sh
# PostToolUse / Stop hook — 파일 수정 후 자동 검증
#
# Claude Code settings.json에 등록 방법:
# "hooks": {
#   "Stop": [{
#     "hooks": [{"type": "command", "command": "bash .claude/hooks/run-project-checks.sh"}]
#   }]
# }

echo "=== Project checks start ==="

has_npm_script() {
  node -e "const p=require('./package.json'); process.exit(p.scripts && p.scripts['$1'] ? 0 : 1)" >/dev/null 2>&1
}

run_check() {
  label="$1"
  shift
  echo "-> $label"
  "$@"
  status=$?
  if [ $status -ne 0 ]; then
    echo "FAILED: $label"
    exit $status
  fi
  echo "OK: $label"
}

if [ -f "package.json" ]; then
  if has_npm_script "typecheck"; then
    run_check "npm run typecheck" npm run typecheck
  elif [ -f "tsconfig.json" ] && [ -x "node_modules/.bin/tsc" ]; then
    run_check "tsc --noEmit" ./node_modules/.bin/tsc --noEmit
  fi

  if has_npm_script "lint"; then
    run_check "npm run lint" npm run lint
  fi

  if has_npm_script "test"; then
    CI=true run_check "npm test" npm test
  fi
else
  echo "No package.json found; skipping Node checks."
fi

if [ "$RUN_BUILD_CHECKS" = "1" ] && [ -f "package.json" ] && has_npm_script "build"; then
  run_check "npm run build" npm run build
fi

echo "=== Project checks passed ==="
exit 0
