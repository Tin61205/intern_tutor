# app/api/v1/users.py

from typing import Annotated

from app.schemas.user import UserCreate, UserResponse, UserUpdate
from fastapi import APIRouter, Depends, status

from app.api.dependencies.pagination import PaginationParams
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def get_users(pagination: Annotated[PaginationParams, Depends()]):
    return UserService.get_all(skip=pagination.skip, limit=pagination.limit)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate):
    return UserService.create(user_in)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return UserService.get_by_id(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_in: UserUpdate):
    return UserService.update(user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    UserService.delete(user_id)
