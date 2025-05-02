from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime

from app.schemas.user import (
    UserEditRequest,
    ChangePasswordRequest,
    UserResponse,
    UserForResponse,
    UserMinResponse
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/check-session", response_model=UserMinResponse)
async def check_session():
    # TODO: Implement check session logic
    return UserMinResponse(
        user=UserForResponse(
            username="user",
            email="user@example.com",
            image=None
        )
    )

@router.get("/get-user-data", response_model=UserResponse)
async def get_user_data():
    # TODO: Implement get user data logic
    return UserResponse(
        username="user",
        email="user@example.com",
        image=None
    )

@router.put("/update-user-data", response_model=UserResponse)
async def update_user(
    user: UserEditRequest,
    image: Optional[UploadFile] = File(None)
):
    # TODO: Implement update user logic
    return UserResponse(
        username="user",
        email=user.email,
        image=None
    )

@router.put("/change-password")
async def change_password(request: ChangePasswordRequest):
    # TODO: Implement change password logic
    return {"message": "Password changed successfully"}

@router.post("/reset-user-image")
async def reset_user_image():
    # TODO: Implement reset user image logic
    return {"message": "User image reset successfully"} 