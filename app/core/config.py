"""
Configuration management for the FastAPI application.
"""

import os

from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://odoo:odoo@localhost/mathstep_db"
    
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Google OAuth
    # GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    # GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    
    # Server
    DEBUG: bool = False
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
