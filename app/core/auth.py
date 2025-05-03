from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.services.jwt_service import JWTService
from app.core.services.user_service import UserService
from app.core.config.config import get_settings
from app.core.exceptions import UnauthorizedException

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/sign-in")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        jwt_service = JWTService()
        user_service = UserService()
        
        # Verify and decode the token
        payload = jwt_service.verify_token(token)
        if payload is None:
            raise UnauthorizedException("Invalid authentication credentials")
            
        # Get user from database
        user = user_service.get_user_by_id(payload.get("sub"))
        if user is None:
            raise UnauthorizedException("User not found")
            
        return user
    except Exception as e:
        raise UnauthorizedException(str(e)) 