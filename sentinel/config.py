import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///data/sentinel.db"
    embedded_worker: bool = True
    auto_migrate: bool = True
    environment: str = "development"
    access_token: str = ""
    allowed_hosts: tuple[str, ...] = ("localhost", "127.0.0.1", "testserver")
    nebius_api_key: str = ""
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1"
    nebius_model: str = "nvidia/nemotron-3-super-120b-a12b"

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
            access_token=os.getenv("APP_ACCESS_TOKEN", ""),
            allowed_hosts=tuple(h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if h.strip()),
            nebius_api_key=os.getenv("NEBIUS_API_KEY", ""),
            nebius_base_url=os.getenv("NEBIUS_BASE_URL", cls.nebius_base_url),
            nebius_model=os.getenv("NEBIUS_MODEL", cls.nebius_model),
        )
        settings.validate()
        return settings

    def validate(self):
        if self.environment not in {"development", "production"}:
            raise ValueError("APP_ENV must be development or production.")
        if self.environment == "production":
            if len(self.access_token) < 24:
                raise ValueError("Production requires APP_ACCESS_TOKEN with at least 24 characters.")
            if not self.database_url.startswith("postgresql+psycopg://"):
                raise ValueError("Production requires PostgreSQL. Use SQLite only for local development.")
            if not self.allowed_hosts or "*" in self.allowed_hosts:
                raise ValueError("Production requires explicit ALLOWED_HOSTS.")
        if not self.nebius_base_url.startswith("https://"):
            raise ValueError("NEBIUS_BASE_URL must use HTTPS.")


def migrate(database_url: str):
    from alembic import command
    from alembic.config import Config

    if database_url.startswith("sqlite:///"):
        Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    config = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parent.parent / "migrations"))
    # Pass via attributes so passwords containing '%' are not ConfigParser interpolation.
    config.attributes["database_url"] = database_url
    command.upgrade(config, "head")
