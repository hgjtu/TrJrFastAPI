from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    SignUpRequest,
    SignInRequest,
    JwtAuthenticationResponse,
    UserForResponse
)
from app.core.database import get_db
from app.core.services.auth_service import AuthenticationService
from app.core.services.user_service import UserService
from app.core.services.jwt_service import JWTService

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
    auth_service = AuthenticationService(
        db=db,
        user_service=UserService(db),
        jwt_service=JWTService()
    )
    
    try:
        user_response = await auth_service.sign_up(request)
        return JwtAuthenticationResponse(
            token=user_response.token,
            user=UserForResponse(
                username=user_response.username,
                email=user_response.email,
                image=None
            )
        )
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
    auth_service = AuthenticationService(
        db=db,
        user_service=UserService(db),
        jwt_service=JWTService()
    )
    
    try:
        user_response = await auth_service.sign_in(request)
        return JwtAuthenticationResponse(
            token=user_response.token,
            user=UserForResponse(
                username=user_response.username,
                email=user_response.email,
                image=None
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) 