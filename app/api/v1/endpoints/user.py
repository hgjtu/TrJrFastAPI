from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.config import get_settings

from app.schemas.auth import UserForResponse
from app.schemas.user import (
    UserEditRequest,
    ChangePasswordRequest,
    UserResponse,
    UserMinResponse
)

from app.models.user import User
from app.core.database import get_db
from app.core.services.user_service import UserService
from app.core.services.auth_service import AuthenticationService
from app.core.services.minio_service import MinioService

settings = get_settings()

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/sign-in")

@router.get("/check-session")
async def check_session(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    user_service = UserService(db, minio_service)
    try:
        current_user = await user_service.get_current_user(token)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        user_data = await user_service.get_user_min_data(current_user)

        # raise Exception(user_data)
        
        return user_data
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/get-user-data")
async def get_user_data(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    user_service = UserService(db, minio_service)
    current_user = await user_service.get_current_user(token)
    try:
        return await user_service.get_user_data(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/update-user-data")
async def update_user(
    user: UserEditRequest,
    image: Optional[UploadFile] = File(None),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    user_service = UserService(db, minio_service)
    current_user = await user_service.get_current_user(token)
    try:
        return await user_service.update_user_data(current_user, user, image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    user_service = UserService(db, minio_service)
    current_user = await user_service.get_current_user(token)
    auth_service = AuthenticationService(db)
    try:
        await auth_service.change_password(current_user, request)
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reset-user-image")
async def reset_user_image(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    user_service = UserService(db, minio_service)
    current_user = await user_service.get_current_user(token)
    try:
        await user_service.reset_user_image(current_user)
        return {"message": "User image reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 