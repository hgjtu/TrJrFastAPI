from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.models.enums import Role

Base = declarative_base()

# Association table for user-post likes
user_post_likes = Table(
    'user_post_likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('post_id', Integer, ForeignKey('posts.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    image_name = Column(String, nullable=False, default="default-user-img")
    role = Column(SQLEnum(Role), nullable=False, default=Role.ROLE_USER)

    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    liked_posts = relationship("Post", secondary=user_post_likes, back_populates="liked_users")

    @property
    def image_url(self) -> str:
        return self.image_name 