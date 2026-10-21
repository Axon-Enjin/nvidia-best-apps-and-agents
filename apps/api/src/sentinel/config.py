import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def workspace_root() -> Path:
    """Directory that relative settings (``data/...``) resolve against, whatever the working directory.

    ``WORKSPACE_ROOT`` wins; a source checkout uses the repository root; an installed package uses the
    current directory (containers and other installs configure absolute paths).
    """
    explicit = os.getenv("WORKSPACE_ROOT")
    if explicit:
        return Path(explicit).resolve()
    checkout = Path(__file__).resolve().parents[4]
    if (checkout / "apps" / "api" / "src" / "sentinel" / "config.py").is_file():
        return checkout
    return Path.cwd()


def _absolute(value: str) -> bool:
    return Path(value).is_absolute() or value.startswith(("/", "\\"))


def _workspace_path(value: str) -> str:
    return value if _absolute(value) else str(workspace_root() / value)


def _workspace_database_url(url: str) -> str:
    prefix = "sqlite:///"
    path = url.removeprefix(prefix)
    if url.startswith(prefix) and path and not path.startswith(":memory:") and not _absolute(path):
        return prefix + (workspace_root() / path).as_posix()
    return url


def alembic_resources() -> tuple[Path, Path]:
    """Return ``(alembic.ini, migrations)`` from the installed package, else the source checkout."""
    package = Path(__file__).resolve().parent / "_alembic"
    if (package / "alembic.ini").is_file():
        return package / "alembic.ini", package / "migrations"
    project = Path(__file__).resolve().parents[2]
    return project / "alembic.ini", project / "migrations"


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///data/sentinel.db"
    embedded_worker: bool = True
    auto_migrate: bool = True
    environment: str = "development"
    network_mode: str = "offline"
    access_token: str = ""
    auth_mode: str = "named"
    secret_key_file: str = "data/account.key"
    source_storage_root: str = "data/sources"
    secure_cookies: bool = False
    session_hours: int = 8
    session_idle_minutes: int = 20
    allowed_hosts: tuple[str, ...] = ("localhost", "127.0.0.1", "testserver")
    # Browser origins of the web frontend whose same-origin proxy forwards changes here.
    trusted_origins: tuple[str, ...] = ()
    nebius_api_key: str = ""
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1"
    nebius_model: str = "nvidia/nemotron-3-super-120b-a12b"

    def __post_init__(self):
        object.__setattr__(self, "database_url", _workspace_database_url(self.database_url))
        object.__setattr__(self, "secret_key_file", _workspace_path(self.secret_key_file))
        object.__setattr__(self, "source_storage_root", _workspace_path(self.source_storage_root))
        object.__setattr__(self, "trusted_origins", tuple(self.trusted_origins))

    @classmethod
    def from_env(cls):
        load_dotenv()
        url = os.getenv("DATABASE_URL", cls.database_url)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        settings = cls(
            database_url=url,
            embedded_worker=os.getenv("EMBEDDED_WORKER", "true").lower() == "true",
            auto_migrate=os.getenv("AUTO_MIGRATE", "true").lower() == "true",
            environment=os.getenv("APP_ENV", "development"),
            network_mode=os.getenv("NETWORK_MODE", "offline").strip().lower(),
            access_token=os.getenv("APP_ACCESS_TOKEN", ""),
            auth_mode=os.getenv("AUTH_MODE", "named").strip().lower(),
            secret_key_file=os.getenv("SECRET_KEY_FILE", cls.secret_key_file),
            source_storage_root=os.getenv("SOURCE_STORAGE_ROOT", cls.source_storage_root),
            secure_cookies=os.getenv("SECURE_COOKIES", "false").lower() == "true",
            allowed_hosts=tuple(h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if h.strip()),
            trusted_origins=tuple(o.strip() for o in os.getenv("TRUSTED_ORIGINS", "").split(",") if o.strip()),
            nebius_api_key=os.getenv("NEBIUS_API_KEY", ""),
            nebius_base_url=os.getenv("NEBIUS_BASE_URL", cls.nebius_base_url),
            nebius_model=os.getenv("NEBIUS_MODEL", cls.nebius_model),
        )
        settings.validate()
        return settings

    def validate(self):
        if self.auth_mode not in {"named", "legacy"}:
            raise ValueError("AUTH_MODE must be named or legacy.")
        if self.auth_mode == "legacy" and (self.environment != "development" or len(self.access_token) < 24):
            raise ValueError("Legacy migration requires development mode and APP_ACCESS_TOKEN of at least 24 characters.")
        if not 1 <= self.session_hours <= 12 or not 1 <= self.session_idle_minutes <= 30:
            raise ValueError("Invalid session timeout.")
        if self.network_mode not in {"offline", "online"}:
            raise ValueError("NETWORK_MODE must be offline or online.")
        if self.environment not in {"development", "production"}:
            raise ValueError("APP_ENV must be development or production.")
        if self.environment == "production":
            if not self.secure_cookies:
                raise ValueError("Production requires SECURE_COOKIES=true and HTTPS.")
            if not self.database_url.startswith("postgresql+psycopg://"):
                raise ValueError("Production requires PostgreSQL. Use SQLite only for local development.")
            if not self.allowed_hosts or "*" in self.allowed_hosts:
                raise ValueError("Production requires explicit ALLOWED_HOSTS.")
        for origin in self.trusted_origins:
            if not re.fullmatch(r"https?://[^/\s*]+", origin):
                raise ValueError("TRUSTED_ORIGINS entries must be bare origins such as http://localhost:3000.")
            if self.environment == "production" and not origin.startswith("https://"):
                raise ValueError("Production TRUSTED_ORIGINS must use HTTPS.")
        if not self.nebius_base_url.startswith("https://"):
            raise ValueError("NEBIUS_BASE_URL must use HTTPS.")


def migrate(database_url: str):
    from alembic import command
    from alembic.config import Config

    if database_url.startswith("sqlite:///"):
        Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    ini, scripts = alembic_resources()
    config = Config(str(ini))
    config.set_main_option("script_location", str(scripts))
    # Pass via attributes so passwords containing '%' are not ConfigParser interpolation.
    config.attributes["database_url"] = database_url
    command.upgrade(config, "head")
