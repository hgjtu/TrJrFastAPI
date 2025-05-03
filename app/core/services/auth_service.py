from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import SignUpRequest, SignInRequest
from app.schemas.user import UserResponse, ChangePasswordRequest
from app.core.services.jwt_service import JWTService
from .user_service import UserService
from ..exceptions import BadRequestException, UnauthorizedException

class AuthenticationService:
    def __init__(self, db: AsyncSession, user_service: UserService, jwt_service: JWTService):
        self.db = db
        self.user_service = user_service
        self.jwt_service = jwt_service

    async def sign_up(self, sign_up_request: SignUpRequest) -> UserResponse:
        try:
            # Check if username exists
            stmt = select(User).where(User.username == sign_up_request.username)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise BadRequestException("User with this username already exists")

            # Check if email exists
            stmt = select(User).where(User.email == sign_up_request.email)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise BadRequestException("User with this email already exists")

            # Create new user
            user = User(
                username=sign_up_request.username,
                email=sign_up_request.email,
                password=sign_up_request.password
            )
            user = await self.user_service.save(user)

            # Generate JWT token
            token = self.jwt_service.generate_token(user.username)

            return UserResponse(
                username=user.username,
                email=user.email,
                token=token
            )
        except BadRequestException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during sign up: {str(e)}"
            )

    async def sign_in(self, sign_in_request: SignInRequest) -> UserResponse:
        try:
            # Find user by username
            stmt = select(User).where(User.username == sign_in_request.username)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user or not await user.verify_password(sign_in_request.password):
                raise UnauthorizedException("Invalid username or password")

            # Generate JWT token
            token = self.jwt_service.generate_token(user.username)

            return UserResponse(
                username=user.username,
                email=user.email,
                token=token
            )
        except UnauthorizedException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during sign in: {str(e)}"
            )

    async def change_password(self, change_password_request: ChangePasswordRequest) -> None:
        try:
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            if not await current_user.verify_password(change_password_request.oldPassword):
                raise UnauthorizedException("Invalid current password")

            if change_password_request.newPassword == change_password_request.oldPassword:
                raise BadRequestException("New password must be different from current password")

            current_user.password = current_user.get_password_hash(change_password_request.newPassword)
            await self.user_service.save(current_user)
        except (UnauthorizedException, BadRequestException):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error changing password: {str(e)}"
            ) 