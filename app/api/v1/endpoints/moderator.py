from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.services.moderator_service import ModeratorService
from app.core.services.post_service import PostService
from app.core.services.user_service import UserService
from app.core.services.minio_service import MinioService

router = APIRouter(
    prefix="/moderators",
    tags=["Модераторы"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/{post_id}/decision/{decision}")
async def set_decision(
    post_id: int, 
    decision: str,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    minio_service = MinioService()
    post_service = PostService(
        db=db,
        user_service=UserService(db, minio_service),
        minio_service=minio_service
    )
    moderator_service = ModeratorService(db, post_service)
    
    user_service = UserService(db, minio_service)
    current_user = await user_service.get_current_user(token)
    
    try:
        await moderator_service.set_decision(current_user, post_id, decision)
        return {"message": "Decision set successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 