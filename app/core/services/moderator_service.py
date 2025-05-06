from app.core.services.minio_service import MinioService
from app.models.enums import PostStatus
from .user_service import UserService
from .post_service import PostService
from ..exceptions import ResourceNotFoundException, UnauthorizedException, BadRequestException

class ModeratorService(UserService):
    def __init__(self, db, post_service: PostService, minio_service: MinioService):
        super().__init__(db, minio_service)
        self.post_service = post_service

    async def set_decision(self, current_user, post_id: int, decision: str) -> None:
        """Set post status after moderation"""
        post = await self.post_service.get_post_by_id(post_id)

        if current_user.role != "ROLE_MODERATOR":
            raise UnauthorizedException("Only moderators can make decisions on posts")

        if post.status != PostStatus.STATUS_NOT_CHECKED:
            raise BadRequestException("Can only make decisions on pending posts")

        if decision.lower() == "approved":
            post.status = PostStatus.STATUS_VERIFIED
        elif decision.lower() == "rejected":
            post.status = PostStatus.STATUS_DENIED
        else:
            raise BadRequestException("Invalid decision. Must be either 'approved' or 'rejected'")

        await self.post_service.save(post) 