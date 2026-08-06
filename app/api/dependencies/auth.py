# app/api/dependencies/auth.py
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenException, UserNotFoundException
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.services.user_service import UserService

# Khai báo Bearer Token với Swagger UI, trỏ URL tới API login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency dùng để bảo vệ API.
    1. Trích xuất token từ Header.
    2. Giải mã token để lấy user_id.
    3. Truy vấn Database để lấy object User tương ứng.
    """
    # 1. Giải mã token
    payload = decode_access_token(token)
    if payload is None:
        raise InvalidTokenException()

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise InvalidTokenException()

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise InvalidTokenException()

    # 2. Bắn qua Service Layer để lấy thông tin (Service sẽ tự lo phần Cache)
    try:
        user = await UserService.get_by_id(db, user_id=user_id)
    except UserNotFoundException:
        raise InvalidTokenException()

    return user
