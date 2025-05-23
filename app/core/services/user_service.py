from fastapi import HTTPException, status, Depends
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.post import Post
from app.models.enums import Role
from app.schemas.user import UserResponse, UserForResponse, UserEditRequest
from fastapi import UploadFile
from .minio_service import MinioService
from ..exceptions import ResourceNotFoundException, UnauthorizedException
from app.core.database import get_db
from fastapi import Depends
from app.core.auth import oauth2_scheme
from app.core.services.jwt_service import JWTService
from app.core.exceptions import UnauthorizedException
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, db: AsyncSession, minio_service: MinioService):
        self.db = db
        self.minio_service = minio_service

    async def save(self, user: User) -> User:
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                if "username" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already exists"
                    )
                elif "email" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists"
                    )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    async def create_user(self, user: User) -> User:
        try:
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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}"
            )

    async def update_user_data(self, current_user, user_edit_request: UserEditRequest, image_file: Optional[UploadFile] = None) -> Optional[UserResponse]:
        try:
            if not current_user:
                raise UnauthorizedException("User not authenticated")

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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user: {str(e)}"
            )

    async def reset_user_image(self, current_user) -> None:
        try:
            if not current_user:
                raise UnauthorizedException("User not authenticated")
            
            current_user.image_name = "default-user-img.png"
            await self.save(current_user)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error resetting user image: {str(e)}"
            )

    async def get_user_data(self, current_user) -> Optional[UserResponse]:
        try:
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            return UserResponse(
                username=current_user.username,
                email=current_user.email,
                image=await self.minio_service.get_file_as_base64(current_user.image_name)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user data: {str(e)}"
            )

    async def get_user_min_data(self, current_user) -> UserForResponse:
        try:
            if not current_user:
                raise UnauthorizedException(f"User not authenticated")
            
            try:
                image_db=await self.minio_service.get_file_as_base64(current_user.image_name)
            except Exception as e:
                image_db = None

            return UserForResponse(
                username=current_user.username,
                image=image_db,
                role=current_user.role
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user minimal data: {str(e)}"
            )

    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise ResourceNotFoundException(f"User with username {username} not found")
        return user


    async def get_current_user(self, token) -> User:
        try:
            if token is not None:
                jwt_service = JWTService()
                # Verify and decode the token
                payload = jwt_service.verify_token(token)
                if payload is None:
                    raise UnauthorizedException(f"Invalid authentication credentials")
                user = await self.get_by_username(payload.get("sub"))
                if user is None:
                    raise UnauthorizedException("User not found")
                
                return user
            else: return None

        except Exception as e:
            raise UnauthorizedException(f"Authentication error: {str(e)}")

    async def is_liked_post(self, current_user_id, post: Post) -> bool:
        try:
            return await post.is_liked_by(current_user_id)
        except Exception:
            return False
        
    async def add_like(self, current_user, post: Post) -> None:
        try:
            if not await post.is_liked_by(current_user.id):
                post.liked_users.append(current_user)
                await self.save(post)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error adding like: {str(e)}"
            )

    async def delete_like(self, current_user, post: Post) -> None:
        try:
            if await post.is_liked_by(current_user.id):
                post.liked_users.remove(current_user)
                await self.save(post)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting like: {str(e)}"
            )
