# app/api/v1/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.response import BaseResponse
from app.schemas.user import TokenResponse, UserRegister, UserResponse
from app.services.user_service import UserService

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/login", response_model=TokenResponse, summary="Đăng nhập để nhận Access Token"
)
async def login(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep
):
    """
    API đăng nhập bằng Form Data chuẩn OAuth2 của FastAPI.
    Swagger UI sẽ tự động nhận diện và tích hợp vào nút Authorize.
    """
    return await UserService.login(db, login_data=login_data)


@router.post(
    "/register",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
async def register(user_in: UserRegister, db: SessionDep):
    """
    API dành cho người dùng cuối tự tạo tài khoản.
    """
    user = await UserService.register(db, user_in=user_in)
    return BaseResponse(data=user, message="Đăng ký tài khoản thành công")
