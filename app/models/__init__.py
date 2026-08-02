# app/models/__init__.py
from app.models.base import Base
from app.models.users import User  # Chú ý file của bạn tên là users.py

__all__ = ["Base", "User"]
