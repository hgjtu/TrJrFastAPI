from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    SignUpRequest,
    SignInRequest,
    JwtAuthenticationResponse
)
from app.core.database import get_db
from app.core.services.auth_service import AuthenticationService
from app.core.services.user_service import UserService
from app.core.services.jwt_service import JWTService
from app.core.services.minio_service import MinioService

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/sign-up", response_model=JwtAuthenticationResponse)
async def sign_up(
    request: SignUpRequest,
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    auth_service = AuthenticationService(
        db=db,
        user_service=UserService(db, minio_service),
        jwt_service=JWTService()
    )
    
    try:
        return await auth_service.sign_up(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/sign-in", response_model=JwtAuthenticationResponse)
async def sign_in(
    request: SignInRequest,
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    auth_service = AuthenticationService(
        db=db,
        user_service=UserService(db, minio_service),
        jwt_service=JWTService()
    )
    
    try:
        return await auth_service.sign_in(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 