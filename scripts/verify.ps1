param([switch]$SkipE2E)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$api = @('--project', 'apps/api', '--offline', '--locked')

function Invoke-Step([string]$Name, [scriptblock]$Command) {
  Write-Output "== $Name"
  & $Command
  if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit $LASTEXITCODE" }
}

Invoke-Step 'sync API environment' { uv sync --project apps/api --locked }
Invoke-Step 'lint' { uv run @api ruff check apps/api/src apps/api/tests apps/api/migrations apps/api/scripts tests/e2e }
Invoke-Step 'API tests' { uv run @api pytest apps/api/tests -q --tb=short }
if (-not $SkipE2E) {
  Invoke-Step 'browser acceptance' { uv run @api pytest tests/e2e -q --tb=short }
}
