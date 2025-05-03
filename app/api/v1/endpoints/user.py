from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import (
    UserEditRequest,
    ChangePasswordRequest,
    UserResponse,
    UserForResponse,
    UserMinResponse
)
from app.core.services.user_service import get_current_user
from app.models.user import User
from app.core.database import get_db
from app.core.services.user_service import UserService
from app.core.services.minio_service import MinioService

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/check-session", response_model=UserMinResponse)
async def check_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        return await user_service.get_user_min_data(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/get-user-data", response_model=UserResponse)
async def get_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        return await user_service.get_user_data(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/update-user-data", response_model=UserResponse)
async def update_user(
    user: UserEditRequest,
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    minio_service = MinioService()
    try:
        return await user_service.update_user_data(current_user.id, user, image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        await user_service.change_password(current_user.id, request)
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reset-user-image")
async def reset_user_image(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        await user_service.reset_user_image(current_user.id)
        return {"message": "User image reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 