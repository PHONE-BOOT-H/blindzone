# block-dangerous-bash.ps1
# PreToolUse hook - block dangerous shell commands before Claude Code runs them.

$ErrorActionPreference = "Stop"

$inputJson = [Console]::In.ReadToEnd()

try {
  $payload = $inputJson | ConvertFrom-Json -ErrorAction Stop
} catch {
  exit 0
}

$command = ""
if ($null -ne $payload.tool_input -and $null -ne $payload.tool_input.command) {
  $command = [string]$payload.tool_input.command
} elseif ($null -ne $payload.command) {
  # Backward-compatible fallback for older examples or local tests.
  $command = [string]$payload.command
}

if ([string]::IsNullOrWhiteSpace($command)) {
  exit 0
}

$dangerousPatterns = @(
  @{ Pattern = '(?i)\brm\s+-rf\b'; Reason = 'recursive force delete' },
  @{ Pattern = '(?i)\bRemove-Item\b.*\b-Recurse\b'; Reason = 'recursive delete via PowerShell' },
  @{ Pattern = '(?i)\bRemove-Item\b.*\b-Force\b'; Reason = 'force delete via PowerShell' },
  @{ Pattern = '(?i)\bgit\s+reset\s+--hard\b'; Reason = 'hard git reset' },
  @{ Pattern = '(?i)\bgit\s+push\b.*(--force|-f)\b'; Reason = 'force push' },
  @{ Pattern = '(?i)\bchmod\b'; Reason = 'permission change' },
  @{ Pattern = '(?i)\bsudo\b'; Reason = 'privilege escalation' },
  @{ Pattern = '(?i)\bnpm\s+publish\b'; Reason = 'package publication' },
  @{ Pattern = '(?i)\bDROP\s+(TABLE|DATABASE)\b'; Reason = 'destructive database command' },
  @{ Pattern = '(?i)\b(curl|wget|iwr|Invoke-WebRequest)\b.*\|\s*(bash|sh|iex|Invoke-Expression)\b'; Reason = 'remote script execution' },
  @{ Pattern = '(?i)\bInvoke-Expression\b|\biex\b'; Reason = 'dynamic command execution' }
)

foreach ($rule in $dangerousPatterns) {
  if ($command -match $rule.Pattern) {
    $response = @{
      hookSpecificOutput = @{
        hookEventName = "PreToolUse"
        permissionDecision = "deny"
        permissionDecisionReason = "Dangerous command blocked: $($rule.Reason). Ask the user before running it."
      }
    }

    [Console]::Out.WriteLine(($response | ConvertTo-Json -Depth 5 -Compress))
    exit 0
  }
}

exit 0
