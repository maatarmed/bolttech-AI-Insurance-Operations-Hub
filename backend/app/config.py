from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Insurance Operations Hub"
    app_env: str = "local"
    database_url: str = "postgresql+asyncpg://hub:hub@localhost:5432/ops_hub"
    checkpoint_database_url: str = ""
    seed_on_startup: bool = True
    openai_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    aws_region: str = "ap-southeast-1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sync_checkpoint_url(self) -> str:
        if self.checkpoint_database_url:
            return self.checkpoint_database_url
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
