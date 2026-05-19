# run-project-checks.ps1
# Stop hook - run common local checks when a Claude Code turn finishes.

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $projectRoot

function Invoke-Check {
  param(
    [Parameter(Mandatory = $true)][string]$Command,
    [Parameter(Mandatory = $true)][string[]]$Arguments,
    [Parameter(Mandatory = $true)][string]$Label
  )

  Write-Host "-> $Label"
  & $Command @Arguments
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED: $Label"
    exit $LASTEXITCODE
  }
  Write-Host "OK: $Label"
}

function Test-NpmScript {
  param(
    [Parameter(Mandatory = $true)]$PackageJson,
    [Parameter(Mandatory = $true)][string]$Name
  )

  return ($null -ne $PackageJson.scripts -and
    $PackageJson.scripts.PSObject.Properties.Name -contains $Name)
}

Write-Host "=== Project checks start ==="

$packagePath = Join-Path $projectRoot "package.json"
if (Test-Path -LiteralPath $packagePath) {
  $packageJson = Get-Content -Raw -Encoding UTF8 -LiteralPath $packagePath | ConvertFrom-Json

  if (Test-NpmScript -PackageJson $packageJson -Name "typecheck") {
    Invoke-Check -Command "npm" -Arguments @("run", "typecheck") -Label "npm run typecheck"
  } elseif (Test-Path -LiteralPath (Join-Path $projectRoot "tsconfig.json")) {
    $localTsc = Join-Path $projectRoot "node_modules\.bin\tsc.cmd"
    if (Test-Path -LiteralPath $localTsc) {
      Invoke-Check -Command $localTsc -Arguments @("--noEmit") -Label "tsc --noEmit"
    }
  }

  if (Test-NpmScript -PackageJson $packageJson -Name "lint") {
    Invoke-Check -Command "npm" -Arguments @("run", "lint") -Label "npm run lint"
  }

  if (Test-NpmScript -PackageJson $packageJson -Name "test") {
    $previousCi = $env:CI
    $env:CI = "true"
    try {
      Invoke-Check -Command "npm" -Arguments @("test") -Label "npm test"
    } finally {
      $env:CI = $previousCi
    }
  }

  if ($env:RUN_BUILD_CHECKS -eq "1" -and (Test-NpmScript -PackageJson $packageJson -Name "build")) {
    Invoke-Check -Command "npm" -Arguments @("run", "build") -Label "npm run build"
  }
} else {
  Write-Host "No package.json found; skipping Node checks."
}

Write-Host "=== Project checks passed ==="
exit 0
