from app.models.enums import Role
from .user_service import UserService
from .exceptions import UnauthorizedException

class AdminService(UserService):
    async def get_admin(self) -> None:
        """Grant admin rights to the current user (for demonstration purposes)"""
        current_user = await self.get_current_user()

        if current_user.role != Role.ROLE_ADMIN:
            raise UnauthorizedException("Only admins can access this endpoint")

        current_user.role = Role.ROLE_ADMIN
        await self.save(current_user) 