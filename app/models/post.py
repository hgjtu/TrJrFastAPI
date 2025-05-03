from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from typing import Optional

from app.models.base import Base
from app.models.enums import PostStatus

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    location = Column(String, nullable=False)
    description = Column(String(2000))
    image_name = Column(String, nullable=False, default="default-post-img.png")
    likes = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(PostStatus), nullable=False, default=PostStatus.STATUS_NOT_CHECKED)

    # Relationships
    author = relationship("User", back_populates="posts", lazy="selectin")
    liked_users = relationship("User", secondary="user_post_likes", back_populates="liked_posts", lazy="selectin")

    async def is_liked_by(self, user_id: int) -> bool:
        return any(user.id == user_id for user in self.liked_users)

    @property
    def image(self) -> str:
        return self.image_name 