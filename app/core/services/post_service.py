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
from ..exceptions import ResourceNotFoundException, UnauthorizedException, BadRequestException

class PostService:
    def __init__(self, db: AsyncSession, user_service: UserService, minio_service: MinioService):
        self.db = db
        self.user_service = user_service
        self.minio_service = minio_service

    async def save(self, post: Post) -> Post:
        try:
            self.db.add(post)
            await self.db.commit()
            await self.db.refresh(post)
            return post
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    async def create_post(self, create_post_request: PostRequest, image_file: Optional[UploadFile] = None) -> PostResponse:
        try:
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            image_name = "default-post-img.png"
            if image_file and image_file.filename:
                image_name = await self.minio_service.upload_file(image_file)

            new_post = Post(
                title=create_post_request.title,
                author=current_user,
                date=datetime.utcnow(),
                location=create_post_request.location,
                description=create_post_request.description,
                image_name=image_name,
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
                isLiked=False,
                status=saved_post.status
            )
        except (UnauthorizedException, BadRequestException):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating post: {str(e)}"
            )

    async def update_post_data(self, post_edit_request: PostRequest, image_file: Optional[UploadFile] = None) -> PostResponse:
        try:
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

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
                isLiked=await self.user_service.is_liked_post(updated_post),
                status=updated_post.status
            )
        except (UnauthorizedException, BadRequestException, ResourceNotFoundException):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating post: {str(e)}"
            )

    async def get_post_data(self, post_id: int) -> PostResponse:
        try:
            post = await self.get_post_by_id(post_id)
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            if post.status == PostStatus.STATUS_NOT_CHECKED and post.author.username != current_user.username:
                raise UnauthorizedException("You are not authorized to view this post")

            is_liked = await self.user_service.is_liked_post(post)

            return PostResponse(
                id=post.id,
                title=post.title,
                author=post.author.username,
                date=post.date,
                location=post.location,
                description=post.description,
                image=await self.minio_service.get_file_as_base64(post.image_name),
                likes=post.likes,
                isLiked=is_liked,
                status=post.status
            )
        except (UnauthorizedException, ResourceNotFoundException):
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting post data: {str(e)}"
            )

    async def delete_post(self, post_id: int) -> None:
        try:
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            post = await self.get_post_by_id(post_id)

            if post.author.username != current_user.username and current_user.role != Role.ROLE_ADMIN:
                raise UnauthorizedException("You are not authorized to delete this post")

            await self.db.delete(post)
            await self.db.commit()
        except (UnauthorizedException, ResourceNotFoundException):
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting post: {str(e)}"
            )

    async def like_post(self, post_id: int) -> int:
        try:
            post = await self.get_post_by_id(post_id)
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            is_liked = await self.user_service.is_liked_post(post)
            if is_liked:
                post.likes -= 1
                await self.user_service.delete_like(post)
            else:
                post.likes += 1
                await self.user_service.add_like(post)

            await self.save(post)
            return post.likes
        except (UnauthorizedException, ResourceNotFoundException):
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating like: {str(e)}"
            )

    async def resubmit_post(self, post_id: int) -> None:
        try:
            post = await self.get_post_by_id(post_id)
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            if post.author.username != current_user.username and current_user.role != Role.ROLE_ADMIN:
                raise UnauthorizedException("You are not authorized to resubmit this post")

            if post.status != PostStatus.STATUS_REJECTED:
                raise BadRequestException("Only rejected posts can be resubmitted")

            post.status = PostStatus.STATUS_NOT_CHECKED
            await self.save(post)
        except (UnauthorizedException, BadRequestException, ResourceNotFoundException):
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error resubmitting post: {str(e)}"
            )

    async def reset_post_image(self, post_id: int) -> None:
        try:
            post = await self.get_post_by_id(post_id)
            current_user = await self.user_service.get_current_user()
            if not current_user:
                raise UnauthorizedException("User not authenticated")

            if post.author.username != current_user.username and current_user.role != Role.ROLE_ADMIN:
                raise UnauthorizedException("You are not authorized to reset this post's image")

            post.image_name = "default-post-img.png"
            await self.save(post)
        except (UnauthorizedException, ResourceNotFoundException):
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error resetting post image: {str(e)}"
            )

    async def get_post_by_id(self, post_id: int) -> Post:
        try:
            stmt = select(Post).where(Post.id == post_id)
            result = await self.db.execute(stmt)
            post = result.scalar_one_or_none()
            if not post:
                raise ResourceNotFoundException("Post not found")
            return post
        except ResourceNotFoundException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting post: {str(e)}"
            )

    async def find_all_posts(self, page: int, limit: int, sort: str, search: Optional[str] = None) -> PageResponse[PostResponse]:
        try:
            query = select(Post)

            # Apply filters based on sort
            if sort == "my-posts":
                try:
                    current_user = await self.user_service.get_current_user()
                    query = query.where(Post.author_id == current_user.id)
                except Exception:
                    raise UnauthorizedException("User not authenticated")
            elif sort == "moderator":
                query = query.where(Post.status == PostStatus.STATUS_NOT_CHECKED)
            else:
                query = query.where(Post.status != PostStatus.STATUS_DENIED)

            # Apply search filters
            if search and search.strip():
                try:
                    search_params = dict(param.split('=') for param in search.split('&') if '=' in param)
                    
                    if "author" in search_params and sort != "my-posts":
                        query = query.join(User).where(User.username.ilike(f"%{search_params['author']}%"))
                    
                    if "title" in search_params:
                        query = query.where(Post.title.ilike(f"%{search_params['title']}%"))
                    
                    if "location" in search_params:
                        query = query.where(Post.location.ilike(f"%{search_params['location']}%"))
                    
                    if "startDate" in search_params or "endDate" in search_params:
                        try:
                            start_date = datetime.fromisoformat(search_params.get("startDate", "")) if "startDate" in search_params else None
                            end_date = datetime.fromisoformat(search_params.get("endDate", "")) if "endDate" in search_params else None
                            
                            if start_date:
                                query = query.where(Post.date >= start_date)
                            if end_date:
                                query = query.where(Post.date <= end_date)
                        except ValueError as e:
                            raise BadRequestException(f"Invalid date format: {str(e)}")
                except Exception as e:
                    raise BadRequestException(f"Invalid search parameters: {str(e)}")

            # Apply sorting
            if sort == "my-posts":
                query = query.order_by(Post.status, Post.date.desc())
            elif sort == "latest" or sort == "date_desc":
                query = query.order_by(Post.date.desc())
            elif sort == "date_asc":
                query = query.order_by(Post.date.asc())
            elif sort == "likes_desc":
                query = query.order_by(Post.likes.desc())
            elif sort == "likes_asc":
                query = query.order_by(Post.likes.asc())
            elif sort == "status_desc":
                query = query.order_by(Post.status.desc())
            elif sort == "status_asc":
                query = query.order_by(Post.status.asc())
            else:
                query = query.order_by(Post.status.desc(), Post.date.desc())

            # Apply pagination
            total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
            query = query.offset(page * limit).limit(limit)
            
            result = await self.db.execute(query)
            posts = result.scalars().all()

            content = []
            for post in posts:
                try:
                    is_liked = await self.user_service.is_liked_post(post)
                except Exception:
                    is_liked = False
                content.append(PostResponse(
                    id=post.id,
                    title=post.title,
                    author=post.author.username,
                    date=post.date,
                    location=post.location,
                    description=post.description,
                    image=await self.minio_service.get_file_as_base64(post.image_name),
                    likes=post.likes,
                    isLiked=is_liked,
                    status=post.status
                ))

            return PageResponse(
                content=content,
                page=page,
                size=limit,
                totalElements=total,
                totalPages=(total + limit - 1) // limit,
                first=page == 0,
                last=page * limit + limit >= total
            )
        except (UnauthorizedException, BadRequestException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"500: Error finding posts: {str(e)}"
            )

    async def find_recommended_posts(self) -> PageResponse[PostResponse]:
        try:
            query = select(Post).where(
                Post.status != PostStatus.STATUS_DENIED
            ).order_by(
                Post.likes.desc(),
                Post.date.desc()
            ).limit(5)
            
            result = await self.db.execute(query)
            posts = result.scalars().all()

            content = []
            for post in posts:
                try:
                    is_liked = await self.user_service.is_liked_post(post)
                except Exception:
                    is_liked = False
                content.append(PostResponse(
                    id=post.id,
                    title=post.title,
                    author=post.author.username,
                    date=post.date,
                    location=post.location,
                    description=post.description,
                    image=await self.minio_service.get_file_as_base64(post.image_name),
                    likes=post.likes,
                    isLiked=is_liked,
                    status=post.status
                ))

            return PageResponse(
                content=content,
                page=0,
                size=5,
                totalElements=len(content),
                totalPages=1,
                first=True,
                last=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error finding recommended posts: {str(e)}"
            ) 