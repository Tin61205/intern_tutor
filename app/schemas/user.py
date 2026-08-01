# app/schemas/user.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Mật khẩu ít nhất 6 ký tự")


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=2, max_length=100)


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    # Pydantic v2: ConfigDict(from_attributes=True) thay cho orm_mode = True
    model_config = ConfigDict(from_attributes=True)
