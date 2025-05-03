from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import validator, Field

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "travel-journal-web-service"
    PORT: int = 8010
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["*"]  # In production, replace with specific origins
    
    # Database settings
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    POSTGRESQL_USER: str = Field(..., env="POSTGRESQL_USER")
    POSTGRESQL_PASSWORD: str = Field(..., env="POSTGRESQL_PASSWORD")
    
    # JWT settings
    TOKEN_SIGNING_KEY: str = Field(..., env="TOKEN_SIGNING_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # MinIO settings
    MINIO_URL: str = Field(..., env="MINIO_URL")
    MINIO_BUCKET: str = Field(..., env="MINIO_BUCKET")
    MINIO_ACCESS_KEY: str = Field(..., env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(..., env="MINIO_SECRET_KEY")
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    @validator("TOKEN_SIGNING_KEY")
    def validate_token_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("TOKEN_SIGNING_KEY must be at least 32 characters long")
        return v
    
    @validator("MINIO_URL")
    def validate_minio_url(cls, v):
        if not v:
            raise ValueError("MINIO_URL must be set")
        return v
    
    @validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    def validate_token_expire_minutes(cls, v):
        try:
            return int(v)
        except (TypeError, ValueError):
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be a valid integer")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        raise RuntimeError(f"Failed to load settings: {str(e)}")

settings = get_settings() 