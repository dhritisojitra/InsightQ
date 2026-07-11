"""Application configuration — reads from environment variables."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "InsightQ"
    app_version: str = "1.0.0"
    debug: bool = False

    # API Keys
    gemini_api_key: str = ""
    groq_api_key: str = ""

    # Storage paths
    upload_dir: str = "uploads"
    chroma_dir: str = "chroma_db"
    chat_history_dir: str = "chat_history"

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 5

    # Models
    embedding_model: str = "all-MiniLM-L6-v2"
    gemini_model: str = "gemini-3.5-flash"
    groq_model: str = "llama-3.3-70b-versatile"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    def ensure_dirs(self) -> None:
        """Create storage directories if they don't exist."""
        for d in [self.upload_dir, self.chroma_dir, self.chat_history_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
