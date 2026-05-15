from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_NAME: str = "access_token"
    COOKIE_REFRESH_NAME: str = "refresh_token"
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"

    DATABASE_URL: str = "postgresql+asyncpg://backend:backend@localhost:5432/backend"

    # Ollama — модерация текста чата: https://ollama.com
    # Windows: .\scripts\setup_ollama.ps1  |  Docker: docker compose up -d ollama
    OFF_PLATFORM_OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str | None = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_REQUEST_TIMEOUT_SEC: float = 60.0
    OLLAMA_PULL_ON_STARTUP: bool = True

    # Загрузки вложений чата (локальные файлы + раздача через StaticFiles)
    CHAT_UPLOAD_DIR: str = "uploads/chat"
    CHAT_STATIC_MOUNT: str = "/static/chat"
    CHAT_PUBLIC_BASE_URL: str = ""
    CHAT_MAX_UPLOAD_BYTES: int = 15 * 1024 * 1024

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @field_validator("OLLAMA_BASE_URL", mode="before")
    @classmethod
    def normalize_ollama_url(cls, v: object) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            return None
        s = v.strip()
        return None if not s else s.rstrip("/")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }