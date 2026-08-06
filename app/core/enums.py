# app/core/enums.py
from enum import Enum


class UserRole(str, Enum):
    """
    Khai báo các Role có trong hệ thống.
    Kế thừa str để FastAPI/Pydantic tự động serialize thành JSON String.
    """

    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"
