from pathlib import Path

import pytest

from sentinel.config import Settings, alembic_resources, workspace_root

REVISIONS = ["0001", "0002", "0003", "0004", "0005", "0006", "0007"]


def test_relative_data_settings_ignore_the_working_directory(monkeypatch, tmp_path):
    monkeypatch.delenv("WORKSPACE_ROOT", raising=False)
    expected = Settings()
    monkeypatch.chdir(tmp_path)
    actual = Settings()
    assert actual == expected
    root = workspace_root()
    assert Path(actual.secret_key_file) == root / "data" / "account.key"
    assert Path(actual.source_storage_root) == root / "data" / "sources"
    assert actual.database_url == f"sqlite:///{(root / 'data' / 'sentinel.db').as_posix()}"
    assert (root / "apps" / "api" / "src" / "sentinel").is_dir()


def test_workspace_root_can_be_set_explicitly(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    settings = Settings()
    assert Path(settings.secret_key_file) == tmp_path.resolve() / "data" / "account.key"
    assert settings.database_url == f"sqlite:///{(tmp_path.resolve() / 'data' / 'sentinel.db').as_posix()}"


@pytest.mark.parametrize("url", ["sqlite:///:memory:", "postgresql+psycopg://u:p@db:5432/sentinel"])
def test_non_file_database_urls_are_unchanged(url):
    assert Settings(database_url=url).database_url == url


def test_absolute_paths_are_unchanged(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'a.db'}", secret_key_file=str(tmp_path / "key"),
                        source_storage_root=str(tmp_path / "sources"))
    assert settings.database_url == f"sqlite:///{tmp_path / 'a.db'}"
    assert settings.secret_key_file == str(tmp_path / "key")
    assert settings.source_storage_root == str(tmp_path / "sources")


def test_migration_history_is_available_with_its_revision_identities():
    ini, scripts = alembic_resources()
    assert ini.is_file()
    names = sorted(path.name for path in (scripts / "versions").glob("*.py"))
    assert [name.split("_")[0] for name in names] == REVISIONS
