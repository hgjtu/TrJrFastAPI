from minio import Minio
from pydantic_settings import BaseSettings

class MinioSettings(BaseSettings):
    MINIO_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str

    class Config:
        env_file = ".env"

minio_settings = MinioSettings()

def get_minio_client() -> Minio:
    return Minio(
        minio_settings.MINIO_URL,
        access_key=minio_settings.MINIO_ACCESS_KEY,
        secret_key=minio_settings.MINIO_SECRET_KEY,
        secure=False
    )

def get_minio_bucket() -> str:
    return minio_settings.MINIO_BUCKET 