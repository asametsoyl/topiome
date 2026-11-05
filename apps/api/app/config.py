from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]
API_DIR = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "packages" / "disease-packs"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env", API_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "Topiome"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    secret_key: str = "dev-only-change-me-please-32-characters-minimum"
    session_cookie_name: str = "topiome_session"
    access_token_ttl_minutes: int = 60 * 24 * 7

    database_url: str = "sqlite:///./topiome.db"
    storage_backend: str = "local"
    storage_dir: str = "./storage"

    redis_url: str = "redis://localhost:6379/0"
    queue_mode: str = "inline"

    allow_demo_login: bool = True
    auto_seed: bool = True
    demo_email: str = "demo@topiome.com"
    demo_password: str = "demo1234"

    max_upload_mb: int = 2048
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def storage_path(self) -> Path:
        path = Path(self.storage_dir)
        if not path.is_absolute():
            path = (API_DIR / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_dev(self) -> bool:
        return self.app_env in {"development", "test"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
