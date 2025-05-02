from pydantic import BaseModel, Field
from typing import List, Optional, TypeVar, Generic
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class PostStatus(str, Enum):
    STATUS_NOT_CHECKED = "STATUS_NOT_CHECKED"
    STATUS_VERIFIED = "STATUS_VERIFIED"
    STATUS_DENIED = "STATUS_DENIED"

class PostRequest(BaseModel):
    id: Optional[int] = Field(None, description="Id поста", example="1")
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название поста",
        example="Невероятные виды Санторини"
    )
    location: str = Field(
        ...,
        max_length=100,
        description="Локация",
        example="Санторини, Греция"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Основной текст поста",
        example="Потрясающие закаты, белоснежные дома и синее море..."
    )

class PostResponse(BaseModel):
    id: int = Field(..., description="Id поста", example="1")
    title: str = Field(..., description="Название поста", example="Невероятные виды Санторини")
    author: str = Field(..., description="Username автора поста")
    date: datetime = Field(..., description="Дата создания поста", example="2023-05-15T10:30:00")
    location: str = Field(..., description="Локация", example="Санторини, Греция")
    description: Optional[str] = Field(None, description="Основной текст поста")
    image: Optional[str] = Field(None, description="base64 изображение", example="none-post-img")
    likes: int = Field(..., description="Кол-во лайков на посте", example="123")
    isLiked: bool = Field(..., description="Признак того, что пост лайкнут запросившим пользователем", example="true")
    status: PostStatus = Field(..., description="Статус проверки")

class PageResponse(BaseModel, Generic[T]):
    content: List[T]
    page: int
    size: int
    totalElements: int
    totalPages: int
    first: bool
    last: bool 