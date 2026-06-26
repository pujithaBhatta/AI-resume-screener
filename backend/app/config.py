"""
config.py - Application Configuration
======================================
This file reads all settings from the .env file using pydantic-settings.
By centralizing config here, every other file imports from one place.

HOW IT WORKS:
- pydantic-settings reads variables from your .env file
- Each variable is typed (str, int, bool) for safety
- If a required variable is missing, the app fails fast with a clear error
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    pydantic-settings automatically reads from:
    1. Environment variables (e.g., export MONGODB_URL=...)
    2. .env file in the current directory
    """
    
    # --- Database ---
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "resume_screener"
    
    # --- Security ---
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    
    # --- App ---
    app_name: str = "AI Resume Screener"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000"
    
    # --- File Upload ---
    max_file_size_mb: int = 10
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"          # Look for .env file
        env_file_encoding = "utf-8"
        case_sensitive = False     # MONGODB_URL == mongodb_url


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached Settings instance.
    
    @lru_cache means this function only runs ONCE — the Settings object
    is created once and reused on every subsequent call. This is efficient
    because reading from .env on every request would be slow.
    """
    return Settings()


# Create a single settings instance to import throughout the app
settings = get_settings()
