from fastapi import HTTPException, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.sql import func
from datetime import datetime
from app.models.post import Post
from app.models.user import User
from app.models.enums import PostStatus, PostSort, Role
from app.schemas.post import PostResponse, PostRequest, PageResponse
from fastapi import UploadFile
from .minio_service import MinioService
from .user_service import UserService
from .exceptions import ResourceNotFoundException, UnauthorizedException, BadRequestException

class PostService:
    def __init__(self, db: AsyncSession, user_service: UserService, minio_service: MinioService):
        self.db = db
        self.user_service = user_service
        self.minio_service = minio_service

    async def save(self, post: Post) -> Post:
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def create_post(self, create_post_request: PostRequest, image_file: Optional[UploadFile] = None) -> PostResponse:
        current_user = await self.user_service.get_current_user()

        new_post = Post(
            title=create_post_request.title,
            author=current_user,
            date=datetime.utcnow(),
            location=create_post_request.location,
            description=create_post_request.description,
            image_name="default-post-img.png" if not image_file else await self.minio_service.upload_file(image_file),
            likes=0,
            status=PostStatus.STATUS_NOT_CHECKED
        )

        saved_post = await self.save(new_post)

        return PostResponse(
            id=saved_post.id,
            title=saved_post.title,
            author=saved_post.author.username,
            date=saved_post.date,
            location=saved_post.location,
            description=saved_post.description,
            image=await self.minio_service.get_file_as_base64(saved_post.image_name),
            likes=saved_post.likes,
            is_liked=False,
            status=saved_post.status
        )

    async def update_post_data(self, post_edit_request: PostRequest, image_file: Optional[UploadFile] = None) -> PostResponse:
        current_user = await self.user_service.get_current_user()
        post = await self.get_post_by_id(post_edit_request.id)

        if post.author.username != current_user.username and current_user.role != Role.ROLE_ADMIN:
            raise UnauthorizedException("You are not authorized to edit this post")

        post.title = post_edit_request.title
        post.location = post_edit_request.location
        post.description = post_edit_request.description

        if image_file and image_file.filename:
            post.image_name = await self.minio_service.upload_file(image_file)

        updated_post = await self.save(post)

        return PostResponse(
            id=updated_post.id,
            title=updated_post.title,
            author=updated_post.author.username,
            date=updated_post.date,
            location=updated_post.location,
            description=updated_post.description,
            image=await self.minio_service.get_file_as_base64(updated_post.image_name),
            likes=updated_post.likes,
            is_liked=await self.user_service.is_liked_post(updated_post),
            status=updated_post.status
        )

    async def get_post_data(self, post_id: int) -> PostResponse:
        post = await self.get_post_by_id(post_id)
        current_user = await self.user_service.get_current_user()

        if post.status == PostStatus.STATUS_NOT_CHECKED and post.author.username != current_user.username:
            raise UnauthorizedException("You are not authorized to view this post")

        is_liked = False

        try:
            is_liked = await self.user_service.is_liked_post(post)
        except Exception:
            pass

        return PostResponse(
            id=post.id,
            title=post.title,
            author=post.author.username,
            date=post.date,
            location=post.location,
            description=post.description,
            image=await self.minio_service.get_file_as_base64(post.image_name),
            likes=post.likes,
            is_liked=is_liked,
            status=post.status
        )

    async def delete_post(self, post_id: int) -> None:
        current_user = await self.user_service.get_current_user()
        post = await self.get_post_by_id(post_id)

        if post.author.username != current_user.username and current_user.role != Role.ROLE_ADMIN:
            raise UnauthorizedException("You are not authorized to delete this post")

        await self.db.delete(post)
        await self.db.commit()

    async def like_post(self, post_id: int) -> int:
        post = await self.get_post_by_id(post_id)
        current_user = await self.user_service.get_current_user()

        if await self.user_service.is_liked_post(post):
            post.likes -= 1
            await self.user_service.delete_like(post)
        else:
            post.likes += 1
            await self.user_service.add_like(post)

        await self.save(post)
        return post.likes

    async def resubmit_post(self, post_id: int) -> None:
        post = await self.get_post_by_id(post_id)
        current_user = await self.user_service.get_current_user()

        if post.author.username != current_user.username and current_user.role != Role.ROLE_ADMIN:
            raise UnauthorizedException("You are not authorized to resubmit this post")

        if post.status != PostStatus.STATUS_REJECTED:
            raise BadRequestException("Only rejected posts can be resubmitted")

        post.status = PostStatus.STATUS_NOT_CHECKED
        await self.save(post)

    async def reset_post_image(self, post_id: int) -> None:
        post = await self.get_post_by_id(post_id)
        current_user = await self.user_service.get_current_user()

        if post.author.username != current_user.username and current_user.role != Role.ROLE_ADMIN:
            raise UnauthorizedException("You are not authorized to reset this post's image")

        post.image_name = "default-post-img.png"
        await self.save(post)

    async def get_post_by_id(self, post_id: int) -> Post:
        stmt = select(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)
        post = result.scalar_one_or_none()
        if not post:
            raise ResourceNotFoundException("Post not found")
        return post

    async def find_all_posts(self, page: int, limit: int, sort: str, search: Optional[str] = None) -> PageResponse[PostResponse]:
        query = select(Post)

        # Apply filters based on sort
        if sort == "my-posts":
            current_user = await self.user_service.get_current_user()
            query = query.where(Post.author_id == current_user.id)
        elif sort == "moderator":
            query = query.where(Post.status == PostStatus.STATUS_NOT_CHECKED)
        else:
            query = query.where(Post.status != PostStatus.STATUS_DENIED)

        # Apply search filters
        if search:
            search_params = dict(param.split('=') for param in search.split('&') if '=' in param)
            
            if "author" in search_params and sort != "my-posts":
                query = query.join(User).where(User.username.ilike(f"%{search_params['author']}%"))
            
            if "title" in search_params:
                query = query.where(Post.title.ilike(f"%{search_params['title']}%"))
            
            if "location" in search_params:
                query = query.where(Post.location.ilike(f"%{search_params['location']}%"))
            
            if "startDate" in search_params or "endDate" in search_params:
                start_date = datetime.fromisoformat(search_params.get("startDate", "")) if "startDate" in search_params else None
                end_date = datetime.fromisoformat(search_params.get("endDate", "")) if "endDate" in search_params else None
                
                if start_date:
                    query = query.where(Post.date >= start_date)
                if end_date:
                    query = query.where(Post.date <= end_date)

        # Apply sorting
        if sort == "my-posts":
            query = query.order_by(Post.status, Post.date.desc())
        else:
            query = query.order_by(Post.status.desc(), Post.date.desc())

        # Apply pagination
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
        query = query.offset(page * limit).limit(limit)
        
        result = await self.db.execute(query)
        posts = result.scalars().all()

        content = []
        for post in posts:
            is_liked = False
            try:
                is_liked = await self.user_service.is_liked_post(post)
            except Exception:
                pass

            content.append(PostResponse(
                id=post.id,
                title=post.title,
                author=post.author.username,
                date=post.date,
                location=post.location,
                description=post.description,
                image=await self.minio_service.get_file_as_base64(post.image_name),
                likes=post.likes,
                is_liked=is_liked,
                status=post.status
            ))

        return PageResponse(
            content=content,
            page=page,
            size=limit,
            total_elements=total,
            total_pages=(total + limit - 1) // limit,
            is_first=page == 0,
            is_last=page * limit + limit >= total
        )

    async def find_recommended_posts(self) -> PageResponse[PostResponse]:
        query = select(Post).where(Post.status != PostStatus.STATUS_DENIED).order_by(Post.likes.desc()).limit(5)
        result = await self.db.execute(query)
        posts = result.scalars().all()

        content = []
        for post in posts:
            is_liked = False
            try:
                is_liked = await self.user_service.is_liked_post(post)
            except Exception:
                pass

            content.append(PostResponse(
                id=post.id,
                title=post.title,
                author=post.author.username,
                date=post.date,
                location=post.location,
                description=post.description,
                image=await self.minio_service.get_file_as_base64(post.image_name),
                likes=post.likes,
                is_liked=is_liked,
                status=post.status
            ))

        return PageResponse(
            content=content,
            page=0,
            size=5,
            total_elements=len(content),
            total_pages=1,
            is_first=True,
            is_last=True
        ) 