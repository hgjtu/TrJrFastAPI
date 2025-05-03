from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.models.base import Base
from app.models.enums import Role
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan", lazy="selectin")
    liked_posts = relationship("Post", secondary=user_post_likes, back_populates="liked_users", lazy="selectin")

    def __init__(self, **kwargs):
        if 'password' in kwargs:
            kwargs['password'] = self.get_password_hash(kwargs['password'])
        super().__init__(**kwargs)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def verify_password(self, plain_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, self.password)
        except Exception:
            return False

    @property
    def image_url(self) -> str:
        return self.image_name 