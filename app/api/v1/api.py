from fastapi import APIRouter

from app.api.v1.endpoints import auth, admin, moderator, post, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admins", tags=["admins"])
api_router.include_router(moderator.router, prefix="/moderators", tags=["moderators"])
api_router.include_router(post.router, prefix="/posts", tags=["posts"])
api_router.include_router(user.router, prefix="/users", tags=["users"]) 