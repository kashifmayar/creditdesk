from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/credit_analyst"
    SECRET_KEY: str = "dev-secret-key-change-in-production-256-bits"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # AI provider: gemini (free, default for testing) | anthropic | openai (production)
    AI_PROVIDER: str = "gemini"
    EMBEDDING_PROVIDER: str = "gemini"

    # Google Gemini — free tier via https://aistudio.google.com/apikey
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # Production providers (switch AI_PROVIDER / EMBEDDING_PROVIDER when ready)
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # 768 for Gemini, 1536 for OpenAI — must match active embedding provider
    EMBEDDING_DIMENSION: int = 768

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = "whatsapp:+14155238886"

    @model_validator(mode="after")
    def align_embedding_dimension(self):
        if self.EMBEDDING_PROVIDER.lower() == "openai":
            self.EMBEDDING_DIMENSION = 1536
        elif self.EMBEDDING_PROVIDER.lower() == "gemini":
            self.EMBEDDING_DIMENSION = 768
        return self


settings = Settings()
