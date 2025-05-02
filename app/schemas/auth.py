from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class SignUpRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Имя пользователя",
        example="Jon"
    )
    email: EmailStr = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Адрес электронной почты",
        example="jondoe@gmail.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Пароль",
        example="my_1secret1_password"
    )

    @validator('password')
    def password_validation(cls, v):
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну: заглавную букву, строчную букву, цифру")
        return v

class SignInRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Имя пользователя",
        example="Jon"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Пароль",
        example="my_1secret1_password"
    )

    @validator('password')
    def password_validation(cls, v):
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну: заглавную букву, строчную букву, цифру")
        return v

class UserForResponse(BaseModel):
    username: str
    email: EmailStr
    image: Optional[str] = None

class JwtAuthenticationResponse(BaseModel):
    token: str = Field(
        ...,
        description="Токен доступа",
        example="eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYyMjUwNj..."
    )
    user: UserForResponse 