"""
configs/settings.py
Central configuration using Pydantic Settings — loaded from .env
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    # ── LLM ──────────────────────────────────────────────────
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o", env="LLM_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")

    # ── Research Tools ────────────────────────────────────────
    tavily_api_key: str = Field(default="", env="TAVILY_API_KEY")

    # ── Storage ───────────────────────────────────────────────
    databricks_host: str = Field(default="", env="DATABRICKS_HOST")
    databricks_token: str = Field(default="", env="DATABRICKS_TOKEN")
    databricks_catalog: str = Field(default="intellicam", env="DATABRICKS_CATALOG")
    databricks_schema: str = Field(default="credit_appraisal", env="DATABRICKS_SCHEMA")
    chroma_persist_dir: str = Field(default="./chroma_store", env="CHROMA_PERSIST_DIR")

    # ── App ───────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # ── Derived ───────────────────────────────────────────────
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def models_dir(self) -> Path:
        return self.project_root / "models"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
