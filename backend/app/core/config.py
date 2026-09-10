from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Investment Research Copilot"
    database_url: str = "postgresql+psycopg://copilot:copilot@localhost:5432/copilot"
    llm_provider: str = "azure_openai"
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    anthropic_api_key: str | None = None
    llm_timeout_seconds: float = 60.0
    max_context_tokens: int = 6000
    max_upload_bytes: int = 10_000_000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
