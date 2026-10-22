param([switch]$SkipE2E, [switch]$SkipWeb)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$api = @('--project', 'apps/api', '--offline', '--locked')
$env:NEXT_TELEMETRY_DISABLED = '1'

function Invoke-Step([string]$Name, [scriptblock]$Command) {
  Write-Output "== $Name"
  & $Command
  if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit $LASTEXITCODE" }
}

Invoke-Step 'sync API environment' { uv sync --project apps/api --locked }
Invoke-Step 'lint' { uv run @api ruff check apps/api/src apps/api/tests apps/api/migrations apps/api/scripts tests/e2e }
Invoke-Step 'API tests' { uv run @api pytest apps/api/tests -q --tb=short }
if (-not $SkipWeb) {
  # The web app's dependencies install from its lockfile; build and tests then run without network access.
  Invoke-Step 'install web dependencies' { pnpm --dir apps/web install --frozen-lockfile }
  Invoke-Step 'web unit tests' { pnpm --dir apps/web test }
  Invoke-Step 'web type check' { pnpm --dir apps/web typecheck }
  Invoke-Step 'web lint' { pnpm --dir apps/web lint }
  Invoke-Step 'web production build' { pnpm --dir apps/web build }
}
if (-not $SkipE2E) {
  if ($SkipWeb) {
    Invoke-Step 'browser acceptance (static UI)' { uv run @api pytest tests/e2e -q --tb=short -k 'not web' }
  } else {
    Invoke-Step 'browser acceptance' { uv run @api pytest tests/e2e -q --tb=short }
  }
}
