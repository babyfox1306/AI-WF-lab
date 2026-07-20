from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # Application
    app_name: str = "SignalForge"
    app_version: str = "2.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./signalforge.db"

    # JWT
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Encryption (for provider API keys)
    master_encryption_key: str = "change-this-to-a-32-char-key-for-aes!"

    # CORS
    cors_origins: str = "*"

    # Worker
    worker_poll_interval_seconds: int = 2
    stale_execution_timeout_minutes: int = 30
    max_concurrent_executions_per_workspace: int = 3

    # LLM Provider defaults
    default_openai_compatible_url: str = "http://localhost:20128/v1"
    default_ollama_url: str = "http://localhost:11434"
    default_timeout_seconds: int = 120

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
