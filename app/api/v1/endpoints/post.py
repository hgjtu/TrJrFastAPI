from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.post import PostRequest, PostResponse, PageResponse
from app.models.enums import PostSort
from app.core.services.user_service import get_current_user
from app.models.user import User
from app.core.database import get_db
from app.core.services.post_service import PostService
from app.core.services.user_service import UserService
from app.core.services.minio_service import MinioService

router = APIRouter(
    prefix="/posts",
    tags=["Посты"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/get-posts-data", response_model=PageResponse[PostResponse])
async def get_posts(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    sort: PostSort = Query(PostSort.DATE_DESC),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        return await post_service.find_all_posts(page, size, sort.value, search)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/create-post", response_model=PostResponse)
async def create_post(
    post: PostRequest,
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        return await post_service.create_post(post, image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/get-post-data/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        return await post_service.get_post_data(post_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/update-post-data", response_model=PostResponse)
async def update_post(
    post: PostRequest,
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        return await post_service.update_post_data(post, image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/delete-post/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        await post_service.delete_post(post_id)
        return {"message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/like-post/{post_id}")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        likes = await post_service.like_post(post_id)
        return {"likes": likes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/resubmit/{post_id}")
async def resubmit_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        await post_service.resubmit_post(post_id)
        return {"message": "Post resubmitted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/get-recommended-posts-data", response_model=PageResponse[PostResponse])
async def get_recommended_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    post_service = PostService(
        db=db,
        user_service=UserService(db),
        minio_service=MinioService()
    )
    
    try:
        return await post_service.find_recommended_posts()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 