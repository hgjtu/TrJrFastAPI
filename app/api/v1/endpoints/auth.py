from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.auth import (
    SignUpRequest,
    SignInRequest,
    JwtAuthenticationResponse,
    UserForResponse
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/sign-up", response_model=JwtAuthenticationResponse)
async def sign_up(request: SignUpRequest):
    # TODO: Implement sign up logic
    return JwtAuthenticationResponse(
        token="dummy_token",
        user=UserForResponse(
            username=request.username,
            email=request.email,
            image=None
        )
    )

@router.post("/sign-in", response_model=JwtAuthenticationResponse)
async def sign_in(request: SignInRequest):
    # TODO: Implement sign in logic
    return JwtAuthenticationResponse(
        token="dummy_token",
        user=UserForResponse(
            username=request.username,
            email="user@example.com",
            image=None
        )
    ) 