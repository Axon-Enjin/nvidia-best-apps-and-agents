param(
  [Parameter(Mandatory=$true)][ValidateSet('init','start','stop','backup')][string]$Action,
  [string]$Checkpoint = 'workspace.backup'
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $projectRoot
$localEnvironment = Join-Path $projectRoot 'data/container.env'
if ($Action -eq 'init') {
  New-Item -ItemType Directory -Force -Path 'data/backups' | Out-Null
  if (Test-Path -LiteralPath $localEnvironment) { throw 'Container environment already exists. Keep its database password.' }
  $passwordBytes = New-Object byte[] 32
  $randomGenerator = [Security.Cryptography.RandomNumberGenerator]::Create()
  $randomGenerator.GetBytes($passwordBytes)
  $randomGenerator.Dispose()
  $databasePassword = -join ($passwordBytes | ForEach-Object { $_.ToString('x2') })
  [IO.File]::WriteAllText($localEnvironment, "POSTGRES_PASSWORD=$databasePassword`n")
  Write-Output 'Created private data/container.env. Keep it and your recovery key backed up privately.'
  exit 0
}
if (!(Test-Path -LiteralPath $localEnvironment)) { throw 'Run scripts/local.ps1 init first.' }
if ($Action -eq 'start') {
  & docker compose --env-file $localEnvironment up --build -d
} elseif ($Action -eq 'stop') {
  & docker compose --env-file $localEnvironment stop frontend web worker
} else {
  if ($Checkpoint -notmatch '^[A-Za-z0-9._-]+$') { throw 'Use a simple checkpoint filename.' }
  & docker compose --env-file $localEnvironment stop frontend web worker
  if ($LASTEXITCODE -ne 0) { throw 'Could not stop services; no backup attempted.' }
  & docker compose --env-file $localEnvironment run --rm --no-deps web python -m sentinel.recovery backup --services-stopped --backup-key /backups/recovery.key --target "/backups/$Checkpoint"
  if ($LASTEXITCODE -ne 0) { throw 'Backup failed; services remain stopped for inspection.' }
  & docker compose --env-file $localEnvironment up -d web worker frontend
}
if ($LASTEXITCODE -ne 0) { throw "Compose failed with exit $LASTEXITCODE" }
