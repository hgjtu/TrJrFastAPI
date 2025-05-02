from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
from typing import Optional
import base64
import io
import uuid
from app.core.config.config import settings

class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    async def upload_file(self, file: UploadFile) -> str:
        """Upload a file to MinIO"""
        try:
            file_name = self._generate_file_name(file.filename)
            file_content = await file.read()
            
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=io.BytesIO(file_content),
                length=len(file_content),
                content_type=file.content_type
            )
            
            return file_name
        except S3Error as e:
            raise Exception(f"Error uploading file to MinIO: {str(e)}")

    async def get_file(self, file_name: str) -> Optional[bytes]:
        """Get a file from MinIO"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=file_name
            )
            return response.read()
        except S3Error:
            return None
        finally:
            response.close()
            response.release_conn()

    async def get_file_as_base64(self, file_name: str) -> str:
        """Get a file from MinIO as base64 string"""
        file_content = await self.get_file(file_name)
        if not file_content:
            return ""
        
        content_type = self._get_content_type(file_name)
        base64_content = base64.b64encode(file_content).decode('utf-8')
        return f"data:{content_type};base64,{base64_content}"

    async def delete_file(self, file_name: str) -> None:
        """Delete a file from MinIO"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=file_name
            )
        except S3Error as e:
            raise Exception(f"Error deleting file from MinIO: {str(e)}")

    async def file_exists(self, file_name: str) -> bool:
        """Check if a file exists in MinIO"""
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=file_name
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise Exception(f"Error checking file existence in MinIO: {str(e)}")

    def get_file_url(self, file_name: str) -> str:
        """Get the URL for a file in MinIO"""
        return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{file_name}"

    def _generate_file_name(self, original_name: str) -> str:
        """Generate a unique file name"""
        return f"{uuid.uuid4()}-{original_name}"

    def _get_content_type(self, file_name: str) -> str:
        """Get content type based on file extension"""
        ext = file_name.split('.')[-1].lower()
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        return content_types.get(ext, 'application/octet-stream') 