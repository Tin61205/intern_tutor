# app/api/v1/users.py
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    PaginationParams,
    get_current_user,
    require_ownership_or_roles,
    require_role,
)
from app.core.enums import UserRole

# Import get_db từ database
from app.db.database import get_db
from app.models.user import User
from app.schemas.response import BaseResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

# Dùng Annotated để bọc Depends lại
SessionDep = Annotated[AsyncSession, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Depends()]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=BaseResponse[UserResponse])
async def get_my_profile(current_user: CurrentUserDep):
    """
    API Protected: Yêu cầu phải truyền Bearer Token trên Header.
    """
    return BaseResponse(data=current_user)


@router.get(
    "/",
    response_model=BaseResponse[list[UserResponse]],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def get_users(pagination: PaginationDep, db: SessionDep):
    """
    API lấy danh sách User. CHỈ CÓ ADMIN mới được phép truy cập.
    """
    users = await UserService.get_all(db, skip=pagination.skip, limit=pagination.limit)
    return BaseResponse(data=users)


@router.get(
    "/{user_id}",
    response_model=BaseResponse[UserResponse],
    dependencies=[
        Depends(require_ownership_or_roles([UserRole.ADMIN, UserRole.STAFF]))
    ],
)
async def get_user(user_id: int, db: SessionDep):
    """
    Lấy thông tin một User cụ thể.
    ADMIN/STAFF có thể xem tất cả. USER bình thường chỉ xem được chính mình.
    """
    user = await UserService.get_by_id(db, user_id=user_id)
    return BaseResponse(data=user)


@router.post(
    "/",
    response_model=BaseResponse[UserResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def create_user(user_in: UserCreate, db: SessionDep):
    """
    Tạo người dùng mới (Dành cho Admin).
    Người dùng bình thường muốn tạo tài khoản thì dùng API /auth/register.
    """
    user = await UserService.create(db, user_in=user_in)
    return BaseResponse(data=user)


@router.patch(
    "/{user_id}",
    response_model=BaseResponse[UserResponse],
    dependencies=[Depends(require_ownership_or_roles([UserRole.ADMIN]))],
)
async def update_user(user_id: int, user_in: UserUpdate, db: SessionDep):
    """
    Cập nhật thông tin User.
    ADMIN có thể cập nhật bất kỳ ai. USER chỉ cập nhật được chính mình.
    """
    user = await UserService.update(db, user_id=user_id, user_in=user_in)
    return BaseResponse(data=user)


@router.delete(
    "/{user_id}",
    response_model=BaseResponse[bool],
    dependencies=[Depends(require_ownership_or_roles([UserRole.ADMIN]))],
)
async def delete_user(user_id: int, db: SessionDep):
    """
    Xóa User.
    ADMIN có thể xóa bất kỳ ai. USER chỉ tự xóa được chính mình.
    """
    success = await UserService.delete(db, user_id=user_id)
    return BaseResponse(data=success, message="Đã xóa user thành công")
