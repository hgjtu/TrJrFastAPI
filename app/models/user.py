from sqlalchemy import Column, Integer, Sequence, String, Enum as SQLEnum, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.enums import Role
from passlib.context import CryptContext
from ..core.security import get_password_hash
import sqlalchemy as sa

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

    id = Column(Integer, Sequence('users_seq'), primary_key=True, index=True, autoincrement=True)
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
            kwargs['password'] = get_password_hash(kwargs['password'])
        super().__init__(**kwargs)

    @property
    def image_url(self) -> str:
        return self.image_name