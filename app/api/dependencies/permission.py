# app/api/dependencies/permission.py
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.api.dependencies.auth import get_current_user
from app.core.enums import UserRole
from app.core.exceptions import AuthorizationException
from app.models.user import User

# Lấy User hiện tại (đã đi qua chốt kiểm tra Authentication)
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(role: UserRole) -> Callable:
    """
    Dependency kiểm tra xem User có ĐÚNG Role yêu cầu không.
    Nếu không có quyền, trả về lỗi 403 Forbidden.
    """

    def role_checker(current_user: CurrentUser) -> User:
        if current_user.role != role:
            raise AuthorizationException()
        return current_user

    return role_checker


def require_any_role(roles: list[UserRole]) -> Callable:
    """
    Dependency kiểm tra xem User có 1 TRONG NHỮNG Role được cho phép không.
    """

    def role_checker(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise AuthorizationException()
        return current_user

    return role_checker


def require_ownership_or_roles(allowed_roles: list[UserRole]) -> Callable:
    """
    Dependency kết hợp (Combination):
    Cho phép đi tiếp nếu User có Role phù hợp HOẶC User đang thao tác trên chính dữ liệu của mình.
    Lưu ý: Dependency này yêu cầu Router phải nhận vào tham số 'user_id' trên URL.
    """

    def ownership_checker(user_id: int, current_user: CurrentUser) -> User:
        # 1. Nếu có Role xịn (VD: ADMIN, MANAGER) -> Cho qua
        if current_user.role in allowed_roles:
            return current_user

        # 2. Nếu Role thấp (USER), kiểm tra xem id thao tác có phải là chính họ không
        if current_user.id != user_id:
            raise AuthorizationException(
                message="Bạn không có quyền thao tác trên dữ liệu của người khác."
            )
        return current_user

    return ownership_checker
