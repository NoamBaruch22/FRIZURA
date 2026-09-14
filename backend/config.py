import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, model_validator

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/frizura"
    postgres_url: str | None = None
    
    @model_validator(mode='after')
    def setup_database_url(self) -> 'Settings':
        if self.postgres_url:
            url = self.postgres_url
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            if "?" not in url:
                url += "?ssl=require"
            self.database_url = url
        return self
    
    # Security (RS256 asymmetric)
    jwt_private_key: SecretStr
    jwt_public_key: str
    jwt_algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # AI Chatbot
    chatbot_provider: str = "gemini" # 'gemini', 'ollama', 'groq'
    gemini_api_key: SecretStr | None = None
    ollama_url: str = "http://localhost:11434"
    groq_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '.env'),
        env_file_encoding="utf-8"
    )

settings = Settings()
