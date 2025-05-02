from app.models.enums import PostStatus
from .user_service import UserService
from .post_service import PostService
from ..exceptions import ResourceNotFoundException, UnauthorizedException, BadRequestException

class ModeratorService(UserService):
    def __init__(self, db, post_service: PostService):
        super().__init__(db)
        self.post_service = post_service

    async def set_decision(self, post_id: int, decision: str) -> None:
        """Set post status after moderation"""
        post = await self.post_service.get_post_by_id(post_id)
        current_user = await self.get_current_user()

        if current_user.role != "ROLE_MODERATOR":
            raise UnauthorizedException("Only moderators can make decisions on posts")

        if post.status != PostStatus.PENDING:
            raise BadRequestException("Can only make decisions on pending posts")

        if decision.lower() == "approve":
            post.status = PostStatus.APPROVED
        elif decision.lower() == "reject":
            post.status = PostStatus.REJECTED
        else:
            raise BadRequestException("Invalid decision. Must be either 'approve' or 'reject'")

        await self.post_service.save(post) 