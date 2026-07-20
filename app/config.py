from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    database_url: str = "sqlite:///./ai_workflow_lab.db"
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
