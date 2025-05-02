from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime

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
    author = relationship("User", back_populates="posts")
    liked_users = relationship("User", secondary="user_post_likes", back_populates="liked_posts")

    @property
    def is_liked(self) -> bool:
        # This will be set by the service layer based on the current user
        return False

    @property
    def image(self) -> str:
        return self.image_name 