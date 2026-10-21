# Run Sentinel Claims locally

Synthetic patient records only. The supported local target is PostgreSQL 17.11 with separate web/worker containers, pinned Python 3.14.5, local OCR and local browser assets. The current Windows host has no Docker engine, WSL, Podman or PostgreSQL executable. Compose 5.6.1 configuration validation ran locally with the official standalone binary; an image build, PostgreSQL workflow and container restore have **not run**. CI is defined, with no hosted CI result claimed.

## Install, then disconnect

Install Docker with Compose and a working Linux-container engine. From PowerShell:

```powershell
./scripts/local.ps1 init
docker compose --env-file data/container.env config --quiet
docker compose --env-file data/container.env build
docker compose --env-file data/container.env pull db
./scripts/local.ps1 start
docker compose --env-file data/container.env run --rm web python -m sentinel account-create reviewer --roles reviewer
docker compose --env-file data/container.env run --rm web python -m sentinel account-create supervisor --roles supervisor
```

Privileged provisioning requires enrollment in a local TOTP authenticator. Keep the generated database password, `/data/account.key` and the separately generated recovery key private and backed up. There is no default account. Open `http://127.0.0.1:8000`; import a fixture folder's `manifest.json` and all originals under `tests/fixtures/development` (shared at the repository root). Use `discrepant`, then `corrected` as the next version of the same case. All required artifacts remain mandatory. The narrative comparison needs a reviewer and a different supervisor; the AI status remains not run offline.

Compose publishes only loopback port 8000 and uses an internal network for web, worker and database. Download images, Python dependencies, OCR English data and browser test binaries before disconnecting. No provider credential or remote identity service is selected. LAN publication requires an explicit Compose/allowed-host change; hosted HTTPS/private access remains outside this local milestone.

Stop with `./scripts/local.ps1 stop`; resume with `./scripts/local.ps1 start`. Do not remove volumes to stop the app. The migration service runs before web/worker startup. Containers run as UID 10001 with a read-only root, private data volume and temporary OCR directory.

## Encrypted backups and isolated restore

Generate a separate recovery key once. In direct development, `SecretBox.from_file(path, create=True)` creates a private Fernet key; keep it outside source control and separately from checkpoints. For containers, generate it in the mounted backups folder:

```powershell
docker compose --env-file data/container.env run --rm web python -c "from sentinel.accounts import SecretBox; SecretBox.from_file('/backups/recovery.key', create=True)"
./scripts/local.ps1 backup -Checkpoint first-checkpoint.backup
```

The backup script stops web/worker before creating an encrypted database/source/key checkpoint, then resumes them only after success. It preserves source hashes, role/assignment state, decisions, reports, pending jobs and the retirement ledger. Prototype checkpoints are bounded to 512 MB uncompressed; larger workspaces require a coordinated volume backup. Keep seven daily recovery points. Scheduling, capacity and retention deletion are not established by these scripts.

For a PostgreSQL restore, create a **new empty isolated database** with the same supported PostgreSQL major and no public port. Stop the target app processes. Mount the encrypted checkpoint, recovery key and the newest retirement ledger. Use the installed `pg_restore` client and:

```powershell
uv run --project apps/api --locked python -m sentinel.recovery restore --services-stopped --backup data/backups/first-checkpoint.backup --backup-key data/backups/recovery.key --target data/restore-drill --restore-database-url 'postgresql+psycopg://USER:PASSWORD@127.0.0.1:5432/EMPTY_RESTORE_DATABASE' --deletion-ledger data/current-retirement-ledger
```

The target directory must not exist and a PostgreSQL target must have no tables. An explicitly supplied retirement-ledger directory must exist, even if empty; a missing mount/typo stops restore before target creation. Restore never drops an existing database. It validates original hashes, revokes all old sessions, resets interrupted leases and reconciles newer retirement tombstones before reopening. Configure the isolated app using the generated private `restore-settings.json`; keep it isolated until named login, history, source access, pending-job completion and report provenance have been checked. The PostgreSQL/container drill remains unrun on this host.

`python -m sentinel.recovery verify --services-stopped` checks the configured database/storage and reports orphan staging receipts without deleting them. `retire --case-id ID --reason REASON --services-stopped` is a local operator action that records an encrypted tombstone and denies access; it does not yet implement physical retention deletion. Preserve the newest `sources/deletions` directory across all older-backup restores. A lost encryption/recovery key cannot be reconstructed from a checkpoint.

## Optional SQLite development path

SQLite is a direct-development convenience. Its successful tests do not establish PostgreSQL concurrency or deployment suitability.

```powershell
uv sync --project apps/api --locked
uv run --project apps/api --locked python apps/api/scripts/install_ocr.py
uv run --project apps/api --locked python -m sentinel migrate
uv run --project apps/api --locked python -m sentinel account-create reviewer --roles reviewer
uv run --project apps/api --locked python -m sentinel account-create supervisor --roles supervisor
uv run --project apps/api --offline --locked python -m sentinel serve
```

Default binding is loopback and the embedded worker is enabled for this path. Windows OCR installation extracts verified binaries into `data/tools`, with no administrator/PATH changes; see [OCR-NOTICES.md](OCR-NOTICES.md). Stop the server before a checkpoint:

```powershell
uv run --project apps/api --locked python -c "from sentinel.accounts import SecretBox; SecretBox.from_file('data/recovery.key', create=True)"
uv run --project apps/api --offline --locked python -m sentinel.recovery backup --services-stopped --backup-key data/recovery.key --target data/backups/development.backup
uv run --project apps/api --offline --locked python -m sentinel.recovery restore --services-stopped --backup-key data/recovery.key --backup data/backups/development.backup --target data/isolated-restore --deletion-ledger data/sources/deletions
```

## Verification

```powershell
uv run --project apps/api --locked playwright install chromium
cd apps/api
uv run --offline --locked ruff check src tests migrations scripts
uv run --offline --locked pytest -q --tb=short
uv run --offline --locked pytest tests/test_recovery.py tests/browser/test_offline_acceptance.py -q
cd ../..
```

Set `TEST_DATABASE_URL` to an empty disposable PostgreSQL database to run `apps/api/tests/test_postgres.py`. The default local run explicitly skips it when absent. Run a full container correction loop and the isolated PostgreSQL restore before claiming the first prototype accepted. Browser request blocking and Python socket checks are not a whole-machine firewall; final container/OS isolation acceptance remains required.
