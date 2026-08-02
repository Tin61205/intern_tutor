# app/api/v1/users.py
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import PaginationParams, get_current_user

# Import get_db từ database
from app.db.database import get_db
from app.models.users import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

# Dùng Annotated để bọc Depends lại
SessionDep = Annotated[AsyncSession, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Depends()]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: CurrentUserDep):
    """
    API Protected: Yêu cầu phải truyền Bearer Token trên Header.
    """
    return current_user


@router.get("/", response_model=list[UserResponse])
async def get_users(pagination: PaginationDep, db: SessionDep):
    return await UserService.get_all(db, skip=pagination.skip, limit=pagination.limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: SessionDep):
    return await UserService.get_by_id(db, user_id=user_id)


@router.post("/", response_model=UserResponse)
async def create_user(user_in: UserCreate, db: SessionDep):
    return await UserService.create(db, user_in=user_in)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_in: UserUpdate, db: SessionDep):
    return await UserService.update(db, user_id=user_id, user_in=user_in)


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: SessionDep):
    return await UserService.delete(db, user_id=user_id)
