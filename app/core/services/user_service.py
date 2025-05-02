from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.post import Post
from app.models.enums import Role
from app.schemas.user import UserResponse, UserForResponse, UserEditRequest
from fastapi import UploadFile
from .minio_service import MinioService
from ..exceptions import ResourceNotFoundException

class UserService:
    def __init__(self, db: AsyncSession, minio_service: MinioService):
        self.db = db
        self.minio_service = minio_service

    async def save(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_user(self, user: User) -> User:
        # Check if username exists
        stmt = select(User).where(User.username == user.username)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists"
            )

        # Check if email exists
        stmt = select(User).where(User.email == user.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        return await self.save(user)

    async def update_user_data(self, user_edit_request: UserEditRequest, image_file: Optional[UploadFile] = None) -> Optional[UserResponse]:
        current_user = await self.get_current_user()

        try:
            # Check if email exists if it's being changed
            if user_edit_request.email and user_edit_request.email != current_user.email:
                stmt = select(User).where(User.email == user_edit_request.email)
                result = await self.db.execute(stmt)
                if result.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User with this email already exists"
                    )
                current_user.email = user_edit_request.email

            if image_file and image_file.filename:
                image_name = await self.minio_service.upload_file(image_file)
                current_user.image_name = image_name

            updated_user = await self.save(current_user)

            return UserResponse(
                username=updated_user.username,
                email=updated_user.email,
                image=await self.minio_service.get_file_as_base64(updated_user.image_name)
            )
        except Exception:
            return None

    async def reset_user_image(self) -> None:
        current_user = await self.get_current_user()
        current_user.image_name = "default-user-img.png"
        await self.save(current_user)

    async def get_user_data(self) -> Optional[UserResponse]:
        user = await self.get_current_user()

        try:
            return UserResponse(
                username=user.username,
                email=user.email,
                image=await self.minio_service.get_file_as_base64(user.image_name)
            )
        except Exception:
            return None

    async def get_user_min_data(self) -> Optional[UserForResponse]:
        user = await self.get_current_user()

        try:
            return UserForResponse(
                username=user.username,
                role=user.role,
                image=await self.minio_service.get_file_as_base64(user.image_name)
            )
        except Exception:
            return None

    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise ResourceNotFoundException("User not found")
        return user

    async def get_current_user(self) -> User:
        # This will be implemented with FastAPI's dependency injection
        # For now, we'll use a placeholder
        raise NotImplementedError("get_current_user needs to be implemented with FastAPI's dependency injection")

    async def is_liked_post(self, post: Post) -> bool:
        current_user = await self.get_current_user()
        return post in current_user.liked_posts

    async def add_like(self, post: Post) -> None:
        current_user = await self.get_current_user()
        current_user.liked_posts.append(post)
        post.liked_users.append(current_user)
        await self.save(current_user)

    async def delete_like(self, post: Post) -> None:
        current_user = await self.get_current_user()
        current_user.liked_posts.remove(post)
        post.liked_users.remove(current_user)
        await self.save(current_user) 