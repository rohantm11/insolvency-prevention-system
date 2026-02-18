"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SolvencyInsight"
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str = "sqlite:///./insolvency.db"

    # CORS settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # ML Model settings
    MODEL_PATH: str = "./ml_models"

    class Config:
        env_file = ".env"


settings = Settings()
