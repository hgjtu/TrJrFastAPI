from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.exceptions import UnauthorizedException
from .security import verify_password

class AuthenticationManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, username: str, password: str) -> User:
        try:
            # Find user by username
            stmt = select(User).where(User.username == username)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise UnauthorizedException("Invalid username")

            # Verify password
            if not verify_password(password, user.password):
                raise UnauthorizedException(f"Invalid password")

            return user
        except UnauthorizedException:
            raise
        except Exception as e:
            raise UnauthorizedException(f"Authentication error: {str(e)}")
        