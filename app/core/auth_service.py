from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import SignUpRequest, SignInRequest, ChangePasswordRequest
from app.schemas.user import UserResponse
from .jwt_service import JwtService
from .user_service import UserService
from .exceptions import BadRequestException, UnauthorizedException

class AuthenticationService:
    def __init__(self, db: AsyncSession, user_service: UserService, jwt_service: JwtService):
        self.db = db
        self.user_service = user_service
        self.jwt_service = jwt_service

    async def sign_up(self, sign_up_request: SignUpRequest) -> UserResponse:
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

    async def sign_in(self, sign_in_request: SignInRequest) -> UserResponse:
        # Find user by username
        stmt = select(User).where(User.username == sign_in_request.username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.verify_password(sign_in_request.password):
            raise UnauthorizedException("Invalid username or password")

        # Generate JWT token
        token = self.jwt_service.generate_token(user.username)

        return UserResponse(
            username=user.username,
            email=user.email,
            token=token
        )

    async def change_password(self, change_password_request: ChangePasswordRequest) -> None:
        current_user = await self.user_service.get_current_user()

        if not current_user.verify_password(change_password_request.old_password):
            raise UnauthorizedException("Invalid current password")

        if change_password_request.new_password == change_password_request.old_password:
            raise BadRequestException("New password must be different from current password")

        current_user.password = change_password_request.new_password
        await self.user_service.save(current_user) 