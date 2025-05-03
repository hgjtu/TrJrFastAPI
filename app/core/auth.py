from fastapi.security import OAuth2PasswordBearer
from app.core.exceptions import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
