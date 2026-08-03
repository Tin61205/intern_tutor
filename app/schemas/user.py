# app/schemas/user.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.core.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Mật khẩu ít nhất 6 ký tự")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@taskhub.com",
                "full_name": "Quản trị viên",
                "password": "strongpassword123"
            }
        }
    )


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=2, max_length=100)


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    # Pydantic v2: ConfigDict(from_attributes=True) thay cho orm_mode = True
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "admin@taskhub.com",
                "full_name": "Quản trị viên",
                "id": 1,
                "role": "ADMIN",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class UserRegister(UserBase):
    """
    Schema dành riêng cho API Đăng ký tài khoản (Register).
    Kế thừa email và full_name từ UserBase.
    """

    password: str = Field(
        min_length=6, description="Mật khẩu phải dài tối thiểu 6 ký tự"
    )
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserRegister":
        """
        Pydantic v2: mode='after' nghĩa là hàm này chạy sau khi
        các field đã được parse và gán vào object (self).
        """
        if self.password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không khớp!")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@taskhub.com",
                "full_name": "Người dùng mới",
                "password": "password123",
                "confirm_password": "password123"
            }
        }
    )


class LoginRequest(BaseModel):
    """
    Schema nhận dữ liệu đăng nhập bằng JSON payload (Thay vì Form Data).
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Schema trả về cho Client sau khi đăng nhập thành công.
    """
    access_token: str
    token_type: str = "bearer"
