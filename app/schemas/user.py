from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional

class ChangePasswordRequest(BaseModel):
    oldPassword: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="Старый пароль",
        example="my_1secret1_password"
    )
    newPassword: str = Field(
        ...,
        min_length=8,
        max_length=255,
        description="Новый пароль",
        example="my_1secret1_password2"
    )

    @validator('oldPassword', 'newPassword')
    def password_validation(cls, v):
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну: заглавную букву, строчную букву, цифру")
        return v

class UserEditRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Адрес электронной почты",
        example="jondoe@gmail.com"
    )

class UserForResponse(BaseModel):
    username: str
    email: EmailStr
    image: Optional[str] = None

class UserMinResponse(BaseModel):
    user: UserForResponse

class UserResponse(BaseModel):
    username: str = Field(..., description="Логин пользователя", example="Jon2000")
    email: EmailStr = Field(..., description="Адрес электронной почты", example="jondoe@gmail.com")
    image: Optional[str] = Field(None, description="base64 изображения") 