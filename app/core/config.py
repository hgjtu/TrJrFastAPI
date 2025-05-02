from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "travel-journal-web-service"
    PORT: int = 8010
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/tr_jr_db")
    POSTGRESQL_USER: str = os.getenv("POSTGRESQL_USER", "postgres")
    POSTGRESQL_PASSWORD: str = os.getenv("POSTGRESQL_PASSWORD", "1234")
    
    # JWT settings
    TOKEN_SIGNING_KEY: str = os.getenv("TOKEN_SIGNING_KEY", "Jssu8aTdbT8hjeZ610Z0IGeHfDQvr6EE6Gj56JWM1E80b4t2l2GC62PRMKTYEHDS")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 28800  # 20 days in minutes
    
    # MinIO settings
    MINIO_URL: str = os.getenv("MINIO_URL", "http://127.0.0.1:9000")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "tr-jr-bucket")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = Settings() 